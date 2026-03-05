"""
scheduler.py — APScheduler 定时任务调度器

Schedule:
  06:00 Asia/Shanghai → DataCollectJob（触发三路采集器，写入 hot_keywords 表）
  07:50 Asia/Shanghai → DailySummaryJob（计算涨跌幅环比、更新 MarketTrend 表）

内嵌在 FastAPI 启动事件中，无需额外进程。
"""
import asyncio
import os
import logging
from datetime import date, datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.hot_keyword import HotKeyword

logger = logging.getLogger(__name__)

# Singleton scheduler
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    return _scheduler


# ─────────────────────────────────────────────────────────────────────────────
# Job 1: 06:00 — 数据采集
# ─────────────────────────────────────────────────────────────────────────────

async def data_collect_job(youtube_api_key: str = "") -> None:
    """
    Runs all collectors in parallel and saves results to hot_keywords table.
    Today's existing records for the same platform are deleted first (idempotent).
    """
    logger.info("[Scheduler] 🚀 DataCollectJob started (all 6 platforms)")

    from backend.services.collectors.pytrends_collector import collect_pytrends
    from backend.services.collectors.youtube_collector import collect_youtube
    from backend.services.collectors.ozon_collector import collect_ozon
    from backend.services.collectors.yandex_collector import collect_yandex
    from backend.services.collectors.vk_collector import collect_vk
    from backend.services.collectors.ok_collector import collect_ok
    from backend.services.collectors.wb_collector import collect_wb

    # Read all API keys from environment
    yt_key      = youtube_api_key or os.environ.get("YOUTUBE_API_KEY", "")
    yandex_tok  = os.environ.get("YANDEX_OAUTH_TOKEN", "")
    yandex_cid  = os.environ.get("YANDEX_CLIENT_ID", "")
    vk_token    = os.environ.get("VK_ACCESS_TOKEN", "")
    ok_app_id   = os.environ.get("OK_APP_ID", "")
    ok_app_key  = os.environ.get("OK_APP_KEY", "")
    ok_token    = os.environ.get("OK_ACCESS_TOKEN", "")
    ok_ssk      = os.environ.get("OK_SESSION_SECRET_KEY", "")

    # Run all 7 collectors in parallel
    all_results = await asyncio.gather(
        collect_pytrends(),
        collect_youtube(api_key=yt_key),
        collect_ozon(),
        collect_yandex(oauth_token=yandex_tok, client_id=yandex_cid),
        collect_vk(access_token=vk_token),
        collect_ok(app_id=ok_app_id, app_key=ok_app_key, access_token=ok_token, session_secret_key=ok_ssk),
        collect_wb(),
        return_exceptions=True
    )

    all_rows = []
    for r in all_results:
        if isinstance(r, list):
            all_rows.extend(r)
        elif isinstance(r, Exception):
            logger.warning(f"[Scheduler] Collector error: {r}")

    if not all_rows:
        logger.warning("[Scheduler] No rows collected, skipping DB write")
        return

    today = date.today()
    with SessionLocal() as db:
        # Clear today's records for idempotency (safe to re-run)
        db.query(HotKeyword).filter(HotKeyword.snapshot_date == today).delete()
        db.bulk_insert_mappings(HotKeyword, all_rows)
        db.commit()

    logger.info(f"[Scheduler] ✅ DataCollectJob done — wrote {len(all_rows)} rows from all platforms")


# ─────────────────────────────────────────────────────────────────────────────
# Job 2: 07:50 — 汇总环比 (growth_rate relative to yesterday)
# ─────────────────────────────────────────────────────────────────────────────

async def daily_summary_job() -> None:
    """
    Computes growth_rate by comparing today's trend_score to yesterday's.
    Updates the growth_rate column for today's rows.
    """
    logger.info("[Scheduler] 📊 DailySummaryJob started")
    today = date.today()
    yesterday = today - timedelta(days=1)

    with SessionLocal() as db:
        today_rows: list[HotKeyword] = (
            db.query(HotKeyword).filter(HotKeyword.snapshot_date == today).all()
        )
        yesterday_rows: list[HotKeyword] = (
            db.query(HotKeyword).filter(HotKeyword.snapshot_date == yesterday).all()
        )

        # Build lookup: (keyword, platform) → trend_score
        yday_map = {
            (r.keyword, r.platform): r.trend_score
            for r in yesterday_rows
        }

        for row in today_rows:
            yday_score = yday_map.get((row.keyword, row.platform))
            if yday_score and yday_score > 0:
                row.growth_rate = round((row.trend_score - yday_score) / yday_score, 4)
            db.add(row)

        db.commit()
    logger.info("[Scheduler] ✅ DailySummaryJob done")


# ─────────────────────────────────────────────────────────────────────────────
# Startup / Shutdown hooks
# ─────────────────────────────────────────────────────────────────────────────

def start_scheduler(youtube_api_key: str = "") -> None:
    scheduler = get_scheduler()

    # 06:00 — collect
    scheduler.add_job(
        lambda: asyncio.ensure_future(data_collect_job(youtube_api_key)),
        CronTrigger(hour=6, minute=0),
        id="data_collect",
        replace_existing=True,
        name="Daily Data Collect (06:00)",
    )

    # 07:50 — summarise growth
    scheduler.add_job(
        lambda: asyncio.ensure_future(daily_summary_job()),
        CronTrigger(hour=7, minute=50),
        id="daily_summary",
        replace_existing=True,
        name="Daily Summary Growth (07:50)",
    )

    scheduler.start()
    logger.info("[Scheduler] ✅ Scheduler started. Jobs: 06:00 collect / 07:50 summary")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped")
