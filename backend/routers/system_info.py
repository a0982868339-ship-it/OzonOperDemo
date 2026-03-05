"""
routers/system_info.py — 系统全局信息 API

GET  /admin/system/info          系统信息（版本/Python/DB/运行时间）
GET  /admin/system/stats         实时数据：在线用户数、今日采集条数等
GET  /admin/audit-logs           审计日志（分页）
GET  /admin/notices              公告列表
POST /admin/notices              创建公告
PUT  /admin/notices/{id}         编辑公告
DELETE /admin/notices/{id}       删除公告
GET  /admin/backup/export        导出 CSV 数据包（users + keywords）
"""
import csv
import io
import os
import platform
import sys
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.audit_log import AuditLog
from backend.models.hot_keyword import HotKeyword
from backend.models.system_notice import SystemNotice
from backend.models.usage_log import UsageLog
from backend.models.user import User

router = APIRouter(prefix="/admin/system", tags=["system"])
router_notices = APIRouter(prefix="/admin/notices", tags=["notices"])
router_audit   = APIRouter(prefix="/admin/audit-logs", tags=["audit"])
router_backup  = APIRouter(prefix="/admin/backup", tags=["backup"])

_server_start = datetime.utcnow()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── System Info ───────────────────────────────────────────────────────────────

@router.get("/info")
def system_info():
    uptime = datetime.utcnow() - _server_start
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    minutes = rem // 60
    return {
        "app_version":  "v1.3.0",
        "python_version": sys.version.split()[0],
        "platform":     platform.system() + " " + platform.release(),
        "uptime":       f"{hours}h {minutes}m",
        "server_time":  datetime.utcnow().isoformat(),
    }


@router.get("/stats")
def system_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    total_users   = db.query(func.count(User.id)).scalar() or 0
    active_users  = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    vip_users     = db.query(func.count(User.id)).filter(User.is_vip == True).scalar() or 0
    today_keywords = db.query(func.count(HotKeyword.id)).filter(
        func.date(HotKeyword.snapshot_date) == today
    ).scalar() or 0
    total_tokens  = db.query(func.sum(UsageLog.tokens_input + UsageLog.tokens_output)).scalar() or 0
    total_cost    = db.query(func.sum(UsageLog.cost_estimate)).scalar() or 0.0
    today_logs    = db.query(func.count(AuditLog.id)).filter(
        func.date(AuditLog.created_at) == today
    ).scalar() or 0
    return {
        "total_users":    total_users,
        "active_users":   active_users,
        "vip_users":      vip_users,
        "today_keywords": today_keywords,
        "total_tokens":   int(total_tokens),
        "total_cost_usd": round(float(total_cost), 4),
        "today_actions":  today_logs,
    }


# ── Usage stats for charts ────────────────────────────────────────────────────

@router.get("/usage")
def usage_stats(days: int = 7, db: Session = Depends(get_db)):
    """Token usage per agent over last N days."""
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            UsageLog.agent_name,
            UsageLog.model_id,
            func.date(UsageLog.created_at).label("day"),
            func.sum(UsageLog.tokens_input + UsageLog.tokens_output).label("tokens"),
            func.sum(UsageLog.cost_estimate).label("cost"),
        )
        .filter(UsageLog.created_at >= since)
        .group_by(UsageLog.agent_name, UsageLog.model_id, func.date(UsageLog.created_at))
        .all()
    )
    # Also totals
    totals = (
        db.query(
            UsageLog.agent_name,
            UsageLog.model_id,
            func.sum(UsageLog.tokens_input + UsageLog.tokens_output).label("tokens"),
            func.sum(UsageLog.cost_estimate).label("cost"),
            func.count(UsageLog.id).label("calls"),
        )
        .group_by(UsageLog.agent_name, UsageLog.model_id)
        .all()
    )

    # Per-user quota summary
    users = db.query(User).all()
    user_quota = [
        {
            "username":   u.username,
            "email":      u.email,
            "role":       u.role,
            "is_vip":     u.is_vip,
            "token_quota": u.token_quota,
            "tokens_used": u.tokens_used,
            "quota_pct":  round(u.tokens_used / u.token_quota * 100, 1) if u.token_quota > 0 else 0,
        }
        for u in users
    ]

    return {
        "daily": [{"agent": f"{r.agent_name} ({r.model_id})", "day": str(r.day), "tokens": int(r.tokens), "cost": float(r.cost)} for r in rows],
        "totals": [{"agent": f"{r.agent_name} ({r.model_id})", "tokens": int(r.tokens), "cost": round(float(r.cost), 4), "calls": r.calls} for r in totals],
        "user_quota": user_quota,
        "summary": {
            "total_tokens": int(db.query(func.sum(UsageLog.tokens_input + UsageLog.tokens_output)).scalar() or 0),
            "total_cost":   round(float(db.query(func.sum(UsageLog.cost_estimate)).scalar() or 0), 4),
            "total_calls":  db.query(func.count(UsageLog.id)).scalar() or 0,
        }
    }


# ── Audit Logs ───────────────────────────────────────────────────────────────

@router_audit.get("")
def list_audit_logs(page: int = 1, per_page: int = 50, db: Session = Depends(get_db)):
    offset = (page - 1) * per_page
    total = db.query(func.count(AuditLog.id)).scalar() or 0
    rows = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "data": [
            {
                "id":         r.id,
                "operator":   r.operator,
                "action":     r.action,
                "target":     r.target,
                "detail":     r.detail,
                "ip_address": r.ip_address,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ],
    }


# ── System Notices ────────────────────────────────────────────────────────────

class NoticeBody(BaseModel):
    title:       str
    content:     str
    notice_type: str = "info"
    is_active:   bool = True
    pinned:      bool = False
    expires_at:  Optional[str] = None


def _notice_dict(n: SystemNotice) -> dict:
    return {
        "id":          n.id,
        "title":       n.title,
        "content":     n.content,
        "notice_type": n.notice_type,
        "is_active":   n.is_active,
        "pinned":      n.pinned,
        "expires_at":  n.expires_at.isoformat() if n.expires_at else None,
        "created_by":  n.created_by,
        "created_at":  n.created_at.isoformat(),
    }


@router_notices.get("")
def list_notices(db: Session = Depends(get_db)):
    rows = db.query(SystemNotice).order_by(SystemNotice.pinned.desc(), SystemNotice.created_at.desc()).all()
    return [_notice_dict(r) for r in rows]


@router_notices.post("")
def create_notice(body: NoticeBody, db: Session = Depends(get_db)):
    n = SystemNotice(
        title=body.title,
        content=body.content,
        notice_type=body.notice_type,
        is_active=body.is_active,
        pinned=body.pinned,
        expires_at=datetime.fromisoformat(body.expires_at) if body.expires_at else None,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return _notice_dict(n)


@router_notices.put("/{notice_id}")
def update_notice(notice_id: int, body: NoticeBody, db: Session = Depends(get_db)):
    n = db.query(SystemNotice).get(notice_id)
    if not n:
        from fastapi import HTTPException
        raise HTTPException(404, "Notice not found")
    n.title = body.title
    n.content = body.content
    n.notice_type = body.notice_type
    n.is_active = body.is_active
    n.pinned = body.pinned
    if body.expires_at:
        n.expires_at = datetime.fromisoformat(body.expires_at)
    db.commit()
    db.refresh(n)
    return _notice_dict(n)


@router_notices.delete("/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    n = db.query(SystemNotice).get(notice_id)
    if n:
        db.delete(n)
        db.commit()
    return {"ok": True}


# ── Backup / Export ───────────────────────────────────────────────────────────

@router_backup.get("/export")
def export_csv(table: str = "users", db: Session = Depends(get_db)):
    """Export table as CSV download."""
    buf = io.StringIO()
    writer = csv.writer(buf)

    if table == "users":
        writer.writerow(["id", "username", "email", "role", "is_active", "is_vip", "token_quota", "tokens_used", "created_at"])
        for u in db.query(User).all():
            writer.writerow([u.id, u.username, u.email, u.role, u.is_active, u.is_vip, u.token_quota, u.tokens_used, u.created_at])
    elif table == "keywords":
        writer.writerow(["id", "keyword", "category", "platform", "trend_score", "growth_rate", "search_volume", "snapshot_date"])
        for k in db.query(HotKeyword).order_by(HotKeyword.snapshot_date.desc()).limit(5000).all():
            writer.writerow([k.id, k.keyword, k.category, k.platform, k.trend_score, k.growth_rate, k.search_volume, k.snapshot_date])
    elif table == "usage":
        writer.writerow(["id", "agent_name", "model_id", "tokens_input", "tokens_output", "cost_estimate", "created_at"])
        for lg in db.query(UsageLog).order_by(UsageLog.created_at.desc()).limit(5000).all():
            writer.writerow([lg.id, lg.agent_name, lg.model_id, lg.tokens_input, lg.tokens_output, lg.cost_estimate, lg.created_at])

    buf.seek(0)
    fname = f"{table}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )
