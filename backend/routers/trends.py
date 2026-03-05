"""
routers/trends.py — 热词数据 API

为以下三个前端页面提供数据：
  - 选品雷达  GET /trends/radar
  - 数据选品  GET /trends/analysis
  - 仪表盘    GET /trends/dashboard

同时提供手动触发采集的接口（测试用）：
  - POST /trends/collect   ← 立即执行采集（管理员权限）
"""
from datetime import date, timedelta
from typing import List, Optional, Iterator
import logging

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import SessionLocal
from backend.models.hot_keyword import HotKeyword
from backend.security.auth import get_current_admin as get_current_user
from backend.services.scheduler import data_collect_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trends", tags=["trends"])


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 选品雷达 Treemap 数据
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/radar")
async def get_radar_data(
    snapshot_date: Optional[str] = Query(None, description="YYYY-MM-DD, default=today"),
    db: Session = Depends(get_db),
):
    """
    Returns keywords formatted for the MarketRadar treemap.
    Shape: { words: [ { name, value, growth_rate, platform, category } ] }
    """
    target_date = _parse_date(snapshot_date)
    rows: List[HotKeyword] = (
        db.query(HotKeyword)
        .filter(HotKeyword.snapshot_date == target_date)
        .order_by(HotKeyword.trend_score.desc())
        .limit(60)
        .all()
    )

    # If no real data, return mock so the page isn't empty
    if not rows:
        return {"words": _mock_radar_words(), "source": "mock", "date": str(target_date)}

    words = [
        {
            "name":        r.keyword_ru or r.keyword,
            "value":       r.trend_score,
            "growth_rate": r.growth_rate,
            "source":      _source_label(r.platform),
            "platform":    [_platform_display(r.platform)],
            "category":    r.category,
        }
        for r in rows
    ]
    return {"words": words, "source": "live", "date": str(target_date)}


# ─────────────────────────────────────────────────────────────────────────────
# 数据选品 热词列表
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/analysis")
async def get_analysis_data(
    category: Optional[str] = Query(None),
    limit: int = Query(10),
    db: Session = Depends(get_db),
):
    """
    Returns top hot keywords for the Analysis page, optionally filtered by category.
    """
    target_date = date.today()
    q = db.query(HotKeyword).filter(HotKeyword.snapshot_date == target_date)
    if category:
        q = q.filter(HotKeyword.category == category)
    rows = q.order_by(HotKeyword.trend_score.desc()).limit(limit).all()

    if not rows:
        return {"keywords": _mock_analysis_keywords(), "source": "mock"}

    keywords = [
        {
            "word":  r.keyword_ru or r.keyword,
            "score": int(r.trend_score),
            "trend": f"+{r.growth_rate*100:.0f}%" if r.growth_rate >= 0 else f"{r.growth_rate*100:.0f}%",
        }
        for r in rows
    ]
    return {"keywords": keywords, "source": "live", "date": str(target_date)}


# ─────────────────────────────────────────────────────────────────────────────
# 仪表盘 KPI 摘要
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns hot categories, top rising keyword, and restock suggestions for Dashboard.
    """
    target_date = date.today()
    rows: List[HotKeyword] = (
        db.query(HotKeyword)
        .filter(HotKeyword.snapshot_date == target_date)
        .order_by(HotKeyword.trend_score.desc())
        .limit(30)
        .all()
    )

    if not rows:
        return {"summary": _mock_dashboard(), "source": "mock"}

    # Top keyword
    top = rows[0]

    # Category aggregation
    cat_scores: dict = {}
    for r in rows:
        cat_scores.setdefault(r.category, []).append(r.trend_score)
    cat_avg = {k: sum(v) / len(v) for k, v in cat_scores.items()}
    top_categories = sorted(cat_avg.items(), key=lambda x: x[1], reverse=True)[:5]

    # Biggest gainers
    gainers = sorted(rows, key=lambda r: r.growth_rate, reverse=True)[:3]

    return {
        "source": "live",
        "date": str(target_date),
        "top_keyword": {
            "word":        top.keyword_ru or top.keyword,
            "score":       top.trend_score,
            "growth_rate": top.growth_rate,
        },
        "top_categories": [
            {"category": k, "avg_score": round(v, 1)} for k, v in top_categories
        ],
        "hot_gainers": [
            {
                "word":  r.keyword_ru or r.keyword,
                "score": r.trend_score,
                "growth_rate": round(r.growth_rate * 100, 1),
            }
            for r in gainers
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 手动触发采集（管理员）
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/collect")
async def trigger_collect(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    """Manually triggers the data collection job immediately (admin only)."""
    if current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin only")

    background_tasks.add_task(data_collect_job)
    return {"message": "Data collection job triggered in background"}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers & Mock Fallbacks
# ─────────────────────────────────────────────────────────────────────────────

def _parse_date(s: Optional[str]) -> date:
    if s:
        try:
            return date.fromisoformat(s)
        except Exception:
            pass
    return date.today()


def _source_label(platform: str) -> str:
    mapping = {"google": "mixed", "youtube": "mixed", "ozon": "ozon", "vk": "vk"}
    return mapping.get(platform, "mixed")


def _platform_display(platform: str) -> str:
    mapping = {"google": "Google", "youtube": "YouTube", "ozon": "Ozon", "vk": "VK"}
    return mapping.get(platform, platform.capitalize())


def _mock_radar_words():
    return [
        {"name": "Умная кормушка", "value": 95, "growth_rate": 1.2, "source": "mixed", "platform": ["Ozon", "VK"], "category": "宠物用品"},
        {"name": "Автопоилка",     "value": 92, "growth_rate": 1.5, "source": "vk",    "platform": ["VK"],         "category": "宠物用品"},
        {"name": "GPS ошейник",    "value": 85, "growth_rate": 1.1, "source": "mixed", "platform": ["Ozon", "VK"], "category": "宠物用品"},
        {"name": "Умный дом",      "value": 80, "growth_rate": 0.8, "source": "mixed", "platform": ["Google"],     "category": "智能家居"},
        {"name": "Детская коляска","value": 75, "growth_rate": 0.5, "source": "ozon",  "platform": ["Ozon"],       "category": "母婴"},
        {"name": "Когтеточка",     "value": 88, "growth_rate": 0.5, "source": "ozon",  "platform": ["Ozon", "WB"], "category": "宠物用品"},
    ]


def _mock_analysis_keywords():
    return [
        {"word": "Автокормушка (自动喂食器)", "score": 98, "trend": "+120%"},
        {"word": "Лежанка для кошек (猫窝)",  "score": 85, "trend": "+45%"},
        {"word": "Игрушка рыба (鱼玩具)",     "score": 72, "trend": "+15%"},
        {"word": "Шлейка для собак (狗背带)", "score": 65, "trend": "+8%"},
        {"word": "Когтеточка (猫抓板)",       "score": 60, "trend": "-5%"},
    ]


def _mock_dashboard():
    return {
        "top_keyword":    {"word": "Умная кормушка", "score": 95.0, "growth_rate": 1.2},
        "top_categories": [{"category": "宠物用品", "avg_score": 87.0}],
        "hot_gainers":    [{"word": "Автопоилка", "score": 92.0, "growth_rate": 50.0}],
    }
