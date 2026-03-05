"""
routers/users.py — 用户管理 API

GET    /admin/users              列出所有用户（含 token 使用率）
POST   /admin/users              创建用户
GET    /admin/users/{id}         获取用户详情
PUT    /admin/users/{id}         更新用户（角色/VIP/额度/状态）
DELETE /admin/users/{id}         删除用户
POST   /admin/users/{id}/reset-password  管理员重置密码
"""
import hashlib
import json
import os
import secrets
from datetime import datetime, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import SessionLocal
from backend.models.user import User
from backend.models.usage_log import UsageLog
from backend.models.audit_log import AuditLog

router = APIRouter(prefix="/admin/users", tags=["users"])

SEED_USERS = [
    {"username": "superadmin", "email": "admin@ozon.demo",    "role": "admin",    "is_vip": True,  "token_quota": -1,       "is_active": True},
    {"username": "张小明",    "email": "zhang@seller.ru",    "role": "operator", "is_vip": True,  "token_quota": 500_000,  "is_active": True},
    {"username": "Иван",       "email": "ivan@market.ru",     "role": "member",   "is_vip": True,  "token_quota": 200_000,  "is_active": True},
    {"username": "李雪梅",    "email": "li@ozon.demo",       "role": "member",   "is_vip": False, "token_quota": 50_000,   "is_active": True},
    {"username": "guest_user", "email": "guest@example.com",  "role": "guest",    "is_vip": False, "token_quota": 5_000,    "is_active": True},
    {"username": "王大力",    "email": "wang@trade.cn",      "role": "member",   "is_vip": False, "token_quota": 100_000,  "is_active": False},
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _ensure_seed(db: Session):
    if db.query(func.count(User.id)).scalar() == 0:
        for u in SEED_USERS:
            db.add(User(
                username=u["username"],
                email=u["email"],
                password_hash=_hash_pw("Ozon@2025"),
                role=u["role"],
                is_vip=u["is_vip"],
                token_quota=u["token_quota"],
                tokens_used=0,
                is_active=u["is_active"],
            ))
        db.commit()


def _serialize(u: User, total_tokens: int = 0) -> dict:
    used = u.tokens_used + total_tokens
    quota = u.token_quota
    pct = round(used / quota * 100, 1) if quota > 0 else 0
    return {
        "id":            u.id,
        "username":      u.username,
        "email":         u.email,
        "role":          u.role,
        "is_active":     u.is_active,
        "is_vip":        u.is_vip,
        "vip_expires_at": u.vip_expires_at.isoformat() if u.vip_expires_at else None,
        "token_quota":   quota,
        "tokens_used":   used,
        "quota_pct":     pct,
        "quota_warning": pct >= 80 and quota > 0,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        "created_at":    u.created_at.isoformat(),
    }


# ── CRUD ─────────────────────────────────────────────────────────────────────

@router.get("")
def list_users(db: Session = Depends(get_db)):
    _ensure_seed(db)
    users = db.query(User).order_by(User.created_at.desc()).all()
    # Aggregate token usage from logs per user-email mapping
    log_totals = (
        db.query(UsageLog.request_path, func.sum(UsageLog.tokens_input + UsageLog.tokens_output))
        .group_by(UsageLog.request_path)
        .all()
    )
    return [_serialize(u) for u in users]


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "member"
    is_vip: bool = False
    token_quota: int = 100_000

class UserUpdate(BaseModel):
    username:      Optional[str]  = None
    email:         Optional[str]  = None
    role:          Optional[str]  = None
    is_active:     Optional[bool] = None
    is_vip:        Optional[bool] = None
    vip_expires_at: Optional[str] = None  # ISO datetime string
    token_quota:   Optional[int]  = None


@router.post("")
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already exists")
    u = User(
        username=body.username,
        email=body.email,
        password_hash=_hash_pw(body.password),
        role=body.role,
        is_vip=body.is_vip,
        token_quota=body.token_quota,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    # Audit
    _audit(db, "admin", "user.create", f"user:{u.id}", f"Created {u.email}")
    return _serialize(u)


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return _serialize(u)


@router.put("/{user_id}")
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    changes = {}
    if body.username  is not None: u.username  = body.username;  changes["username"] = body.username
    if body.email     is not None: u.email     = body.email;     changes["email"]    = body.email
    if body.role      is not None: u.role      = body.role;      changes["role"]     = body.role
    if body.is_active is not None: u.is_active = body.is_active; changes["is_active"] = body.is_active
    if body.is_vip    is not None: u.is_vip    = body.is_vip;    changes["is_vip"]   = body.is_vip
    if body.token_quota is not None: u.token_quota = body.token_quota; changes["token_quota"] = body.token_quota
    if body.vip_expires_at:
        u.vip_expires_at = datetime.fromisoformat(body.vip_expires_at)
    u.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(u)
    _audit(db, "admin", "user.update", f"user:{u.id}", json.dumps(changes, ensure_ascii=False))
    return _serialize(u)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    email = u.email
    db.delete(u)
    db.commit()
    _audit(db, "admin", "user.delete", f"user:{user_id}", f"Deleted {email}")
    return {"ok": True}


class ResetPwBody(BaseModel):
    new_password: str

@router.post("/{user_id}/reset-password")
def reset_password(user_id: int, body: ResetPwBody, db: Session = Depends(get_db)):
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    u.password_hash = _hash_pw(body.new_password)
    db.commit()
    _audit(db, "admin", "user.reset_password", f"user:{user_id}", "Password reset by admin")
    return {"ok": True}


def _audit(db: Session, operator: str, action: str, target: str, detail: str):
    try:
        db.add(AuditLog(operator=operator, action=action, target=target, detail=detail))
        db.commit()
    except Exception:
        pass
