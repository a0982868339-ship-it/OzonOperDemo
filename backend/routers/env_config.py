"""
routers/env_config.py — 环境配置 API

提供：
  GET  /admin/env/platforms              列出所有平台配置（key 打码）
  PUT  /admin/env/platforms/{platform}   更新平台 key（加密存储）+ 开关
  POST /admin/env/platforms/{platform}/test  测试连通性
  GET  /admin/env/scheduler              获取调度配置
  PUT  /admin/env/scheduler              更新调度配置
"""
import json
import logging
import os
from datetime import datetime, date
from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.platform_config import PlatformConfig, SchedulerConfig
from backend.services.crypto import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/env", tags=["env-config"])

# ── Default platform definitions ─────────────────────────────────────────────
PLATFORM_DEFAULTS = [
    {"platform": "yandex",  "display_name": "Yandex",      "color": "#FF0000", "required_keys": [],                                             "status": "no_key_needed"},
    {"platform": "wb",      "display_name": "Wildberries", "color": "#CB11AB", "required_keys": [],                                             "status": "no_key_needed"},
    {"platform": "ozon",    "display_name": "Ozon",        "color": "#0069FF", "required_keys": [],                                             "status": "no_key_needed"},
    {"platform": "youtube", "display_name": "YouTube",     "color": "#FF0000", "required_keys": ["YOUTUBE_API_KEY"],                            "status": "pending"},
    {"platform": "vk",      "display_name": "VK",          "color": "#0077FF", "required_keys": ["VK_ACCESS_TOKEN"],                            "status": "pending"},
    {"platform": "ok",      "display_name": "OK",          "color": "#EE8208", "required_keys": ["OK_APP_ID", "OK_APP_KEY", "OK_ACCESS_TOKEN", "OK_SESSION_SECRET_KEY"], "status": "pending"},
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_defaults(db: Session) -> None:
    """初始化默认平台配置行（只在首次运行时插入）"""
    for p in PLATFORM_DEFAULTS:
        exists = db.query(PlatformConfig).filter(PlatformConfig.platform == p["platform"]).first()
        if not exists:
            db.add(PlatformConfig(
                platform=p["platform"],
                display_name=p["display_name"],
                color=p["color"],
                status=p["status"],
            ))
    db.commit()


def _mask_key(value: str) -> str:
    """将密钥打码显示：前4位 + *** + 后4位"""
    if len(value) <= 8:
        return "••••••••"
    return value[:4] + "••••••••" + value[-4:]


def _serialize_platform(p: PlatformConfig) -> dict:
    keys_info = {}
    required = next((d["required_keys"] for d in PLATFORM_DEFAULTS if d["platform"] == p.platform), [])

    raw_keys: Dict[str, str] = {}
    if p.keys_json:
        try:
            raw_keys = json.loads(p.keys_json)
        except Exception:
            pass

    for key_name in required:
        enc_val = raw_keys.get(key_name, "")
        if enc_val.startswith("enc:"):
            try:
                plain = decrypt_value(enc_val[4:])
                keys_info[key_name] = _mask_key(plain)
            except Exception:
                keys_info[key_name] = ""
        else:
            keys_info[key_name] = ""

    return {
        "platform":      p.platform,
        "display_name":  p.display_name,
        "color":         p.color,
        "is_active":     p.is_active,
        "status":        p.status,
        "status_msg":    p.status_msg,
        "required_keys": required,
        "keys_masked":   keys_info,
        "last_tested_at": p.last_tested_at.isoformat() if p.last_tested_at else None,
        "updated_at":    p.updated_at.isoformat() if p.updated_at else None,
    }


# ─── Platform endpoints ───────────────────────────────────────────────────────

@router.get("/platforms")
def list_platforms(db: Session = Depends(get_db)):
    _ensure_defaults(db)
    rows = db.query(PlatformConfig).all()
    return [_serialize_platform(r) for r in rows]


class PlatformUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    keys: Optional[Dict[str, str]] = None  # {"VK_ACCESS_TOKEN": "plaintext_value"}


@router.put("/platforms/{platform}")
def update_platform(platform: str, body: PlatformUpdateRequest, db: Session = Depends(get_db)):
    _ensure_defaults(db)
    row = db.query(PlatformConfig).filter(PlatformConfig.platform == platform).first()
    if not row:
        raise HTTPException(status_code=404, detail="Platform not found")

    if body.is_active is not None:
        row.is_active = body.is_active

    if body.keys:
        existing: Dict[str, str] = {}
        if row.keys_json:
            try:
                existing = json.loads(row.keys_json)
            except Exception:
                pass

        for key_name, plain_val in body.keys.items():
            if plain_val:  # Only update non-empty values
                existing[key_name] = "enc:" + encrypt_value(plain_val)
                # Also write to process env so scheduler picks it up immediately
                os.environ[key_name] = plain_val

        row.keys_json = json.dumps(existing)
        # Check if all required keys are now configured
        required = next((d["required_keys"] for d in PLATFORM_DEFAULTS if d["platform"] == platform), [])
        if required and all(k in existing for k in required):
            row.status = "configured"

    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return _serialize_platform(row)


@router.post("/platforms/{platform}/test")
async def test_platform(platform: str, db: Session = Depends(get_db)):
    """立刻测试该平台采集器的连通性，更新 status 字段"""
    _ensure_defaults(db)
    row = db.query(PlatformConfig).filter(PlatformConfig.platform == platform).first()
    if not row:
        raise HTTPException(status_code=404, detail="Platform not found")

    # Decrypt and inject env vars for this test
    raw_keys: Dict[str, str] = {}
    if row.keys_json:
        try:
            raw_keys = json.loads(row.keys_json)
        except Exception:
            pass
    for key_name, enc_val in raw_keys.items():
        if enc_val.startswith("enc:"):
            try:
                os.environ[key_name] = decrypt_value(enc_val[4:])
            except Exception:
                pass

    status, msg = "error", "Unknown error"
    try:
        if platform == "yandex":
            import httpx
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.get("https://yandex.ru/suggest/suggest-ya.cgi", params={"v": 4, "part": "кормушка", "lang": "ru"})
            status, msg = ("configured", "Yandex Suggest OK") if r.status_code == 200 else ("error", f"HTTP {r.status_code}")

        elif platform == "wb":
            import httpx
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://www.wildberries.ru/",
            }
            async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as c:
                r = await c.get("https://search.wb.ru/exactmatch/ru/common/v4/search",
                                params={"appType": 1, "curr": "rub", "dest": -1257786, "query": "кормушка", "resultset": "catalog", "sort": "popular", "spp": 30})
            count = 0
            if r.status_code == 200:
                try:
                    count = r.json().get("data", {}).get("total", 0)
                except Exception:
                    count = 0
            status, msg = ("configured", f"WB OK — {count} products found") if r.status_code == 200 else ("error", f"HTTP {r.status_code}")

        elif platform == "ozon":
            import httpx
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Referer": "https://www.ozon.ru/",
                "X-Requested-With": "XMLHttpRequest",
            }
            async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=headers) as c:
                r = await c.get("https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2",
                                params={"url": "/search/?text=кормушка&sorting=rating&page=1"})
            ok = False
            if r.status_code == 200:
                try:
                    data = r.json()
                    widget_states = data.get("widgetStates", {})
                    ok = isinstance(widget_states, dict) and len(widget_states) > 0
                except Exception:
                    ok = False
            status = "configured" if ok else "error"
            msg = "Ozon API OK" if ok else f"Ozon HTTP {r.status_code}"

        elif platform == "youtube":
            key = os.environ.get("YOUTUBE_API_KEY", "")
            if not key:
                status, msg = "pending", "YOUTUBE_API_KEY not configured"
            else:
                import httpx
                async with httpx.AsyncClient(timeout=10) as c:
                    r = await c.get("https://www.googleapis.com/youtube/v3/search",
                                    params={"part": "snippet", "q": "кормушка", "type": "video", "regionCode": "RU", "key": key, "maxResults": 1})
                status = "configured" if r.status_code == 200 else "error"
                msg = f"YouTube API {'OK' if r.status_code == 200 else f'error {r.status_code}'}"

        elif platform == "vk":
            token = os.environ.get("VK_ACCESS_TOKEN", "")
            if not token:
                status, msg = "pending", "VK_ACCESS_TOKEN not configured"
            else:
                import httpx
                async with httpx.AsyncClient(timeout=10) as c:
                    r = await c.get("https://api.vk.com/method/users.get",
                                    params={"access_token": token, "v": "5.199"})
                data = r.json()
                status = "configured" if "response" in data else "error"
                msg = "VK API OK" if "response" in data else data.get("error", {}).get("error_msg", "VK API error")

        elif platform == "ok":
            app_id = os.environ.get("OK_APP_ID", "")
            if not app_id:
                status, msg = "pending", "OK credentials not configured"
            else:
                status, msg = "configured", "OK credentials present (test on next collect run)"

    except Exception as e:
        status, msg = "error", str(e)[:200]

    row.status = status
    row.status_msg = msg
    row.last_tested_at = datetime.utcnow()
    db.commit()
    return {"platform": platform, "status": status, "msg": msg}


# ─── Scheduler config endpoints ───────────────────────────────────────────────

def _get_or_create_scheduler_config(db: Session) -> SchedulerConfig:
    cfg = db.query(SchedulerConfig).first()
    if not cfg:
        cfg = SchedulerConfig()
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.get("/scheduler")
def get_scheduler_config(db: Session = Depends(get_db)):
    cfg = _get_or_create_scheduler_config(db)
    return {
        "collect_hour": cfg.collect_hour,
        "collect_min":  cfg.collect_min,
        "summary_hour": cfg.summary_hour,
        "summary_min":  cfg.summary_min,
        "timezone":     cfg.timezone,
        "webhook_url":  cfg.webhook_url,
    }


class SchedulerUpdateRequest(BaseModel):
    collect_hour: Optional[int] = None
    collect_min:  Optional[int] = None
    summary_hour: Optional[int] = None
    summary_min:  Optional[int] = None
    timezone:     Optional[str] = None
    webhook_url:  Optional[str] = None


@router.put("/scheduler")
def update_scheduler_config(body: SchedulerUpdateRequest, db: Session = Depends(get_db)):
    cfg = _get_or_create_scheduler_config(db)
    if body.collect_hour is not None: cfg.collect_hour = body.collect_hour
    if body.collect_min  is not None: cfg.collect_min  = body.collect_min
    if body.summary_hour is not None: cfg.summary_hour = body.summary_hour
    if body.summary_min  is not None: cfg.summary_min  = body.summary_min
    if body.timezone     is not None: cfg.timezone     = body.timezone
    if body.webhook_url  is not None: cfg.webhook_url  = body.webhook_url
    cfg.updated_at = datetime.utcnow()
    db.commit()

    # Hot-reload scheduler jobs with new times
    try:
        from backend.services.scheduler import get_scheduler, data_collect_job, daily_summary_job
        import asyncio
        scheduler = get_scheduler()
        if scheduler.running:
            from apscheduler.triggers.cron import CronTrigger
            scheduler.reschedule_job("data_collect",  trigger=CronTrigger(hour=cfg.collect_hour, minute=cfg.collect_min,  timezone=cfg.timezone))
            scheduler.reschedule_job("daily_summary", trigger=CronTrigger(hour=cfg.summary_hour, minute=cfg.summary_min, timezone=cfg.timezone))
    except Exception as e:
        logger.warning(f"[EnvConfig] Failed to reschedule jobs: {e}")

    return {"message": "Scheduler config updated", "collect": f"{cfg.collect_hour:02d}:{cfg.collect_min:02d}", "summary": f"{cfg.summary_hour:02d}:{cfg.summary_min:02d}"}
