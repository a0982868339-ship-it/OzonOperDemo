"""
youtube_collector.py — YouTube Data API v3 采集器

免费额度：每天 10,000 units (一次 search 消耗 100 units，每天最多100次)
抓取内容：trending 视频标题中的商品关键词 + 观看量当热度代理指标

需要在管理后台配置：YOUTUBE_API_KEY
"""
import asyncio
import httpx
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# 这些关键词将被搜索，每个关键词消耗 100 units
SEARCH_KEYWORDS_RU = [
    "автокормушка для кошек",
    "умный дом Ozon",
    "детские игрушки распродажа",
    "товары для дома Wildberries",
    "умная колонка",
]

CATEGORY_MAP = {
    "автокормушка": "宠物用品",
    "кормушка": "宠物用品",
    "игрушки": "母婴",
    "детские": "母婴",
    "умный дом": "智能家居",
    "умная колонка": "智能家居",
    "wildberries": "general",
    "ozon": "general",
    "товары": "general",
}


def _guess_category(text: str) -> str:
    lower = text.lower()
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in lower:
            return cat
    return "general"


async def collect_youtube(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch trending product keywords from YouTube Russia.
    api_key can be passed directly or read from env YOUTUBE_API_KEY.
    """
    key = api_key or os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        logger.warning("YOUTUBE_API_KEY not configured, skipping YouTube collection")
        return []

    results = []
    today = date.today()

    async with httpx.AsyncClient(timeout=15) as client:
        # 1. Get regionCode=RU trending videos (videoCategoryId=26=Howto&Style, or 17=Sports)
        # We use search instead of videos.list for keyword-level data
        for kw in SEARCH_KEYWORDS_RU:
            try:
                resp = await client.get(
                    f"{YOUTUBE_API_BASE}/search",
                    params={
                        "part": "snippet",
                        "q": kw,
                        "type": "video",
                        "regionCode": "RU",
                        "relevanceLanguage": "ru",
                        "order": "viewCount",
                        "maxResults": 10,
                        "key": key,
                    },
                )
                if resp.status_code != 200:
                    logger.warning(f"YouTube API error for '{kw}': {resp.status_code}")
                    continue

                items = resp.json().get("items", [])
                if not items:
                    continue

                # Fetch video statistics (viewCount) for the first result
                video_id = items[0]["id"].get("videoId", "")
                if video_id:
                    stats_resp = await client.get(
                        f"{YOUTUBE_API_BASE}/videos",
                        params={
                            "part": "statistics",
                            "id": video_id,
                            "key": key,
                        },
                    )
                    stats_items = stats_resp.json().get("items", [])
                    view_count = int(stats_items[0]["statistics"].get("viewCount", 0)) if stats_items else 0
                else:
                    view_count = 0

                # Normalise to a 0-100 trend score (log-scale)
                import math
                trend_score = min(100.0, math.log10(view_count + 1) * 14)

                results.append({
                    "keyword":       kw,
                    "keyword_ru":    kw,
                    "category":      _guess_category(kw),
                    "platform":      "youtube",
                    "search_volume": view_count,
                    "trend_score":   round(trend_score, 2),
                    "growth_rate":   0.0,  # Single snapshot; growth needs yesterday's data
                    "snapshot_date": today,
                    "created_at":    datetime.utcnow(),
                })

            except Exception as e:
                logger.warning(f"YouTube kw '{kw}' failed: {e}")
                continue

    return results
