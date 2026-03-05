"""
pytrends_collector.py — Google趋势数据采集器

使用开源 pytrends 库，免费、无需 API Key。
抓取各关键词的近 7 天搜索趋势。
"""
import asyncio
from datetime import date, datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 预设关键字组（宠物用品品类示例，可在管理后台扩展）
DEFAULT_KEYWORDS = [
    # 宠物用品
    ["автокормушка для кошек", "умная кормушка", "кормушка для собак"],
    # 电子配件
    ["умный дом", "wi-fi розетка", "умная колонка"],
    # 母婴
    ["детская коляска", "детские игрушки", "слинг для новорождённых"],
]

CATEGORY_MAP = {
    "автокормушка для кошек": "宠物用品",
    "умная кормушка": "宠物用品",
    "кормушка для собак": "宠物用品",
    "умный дом": "智能家居",
    "wi-fi розетка": "智能家居",
    "умная колонка": "智能家居",
    "детская коляска": "母婴",
    "детские игрушки": "母婴",
    "слинг для новорождённых": "母婴",
}


async def collect_pytrends(keywords_groups: List[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Runs pytrends fetch in a thread pool to avoid blocking the event loop.
    Returns a list of dicts ready to be inserted into hot_keywords table.
    """
    groups = keywords_groups or DEFAULT_KEYWORDS
    return await asyncio.get_event_loop().run_in_executor(None, _sync_collect, groups)


def _sync_collect(groups: List[List[str]]) -> List[Dict[str, Any]]:
    results = []
    today = date.today()

    try:
        from pytrends.request import TrendReq
    except ImportError:
        logger.warning("pytrends not installed. Run: pip install pytrends")
        return []

    try:
        pt = TrendReq(hl="ru", tz=180, timeout=(10, 25))  # Moscow timezone

        for group in groups:
            try:
                pt.build_payload(group, cat=0, timeframe="now 7-d", geo="RU")
                interest_df = pt.interest_over_time()

                if interest_df.empty:
                    continue

                for kw in group:
                    if kw not in interest_df.columns:
                        continue

                    series = interest_df[kw]
                    if series.empty:
                        continue

                    # 当前值（最新的时间点）
                    latest_val = float(series.iloc[-1])
                    # 环比增长率：(最新 - 7天前) / (7天前 + 1)
                    oldest_val = float(series.iloc[0])
                    growth = (latest_val - oldest_val) / (oldest_val + 1)

                    results.append({
                        "keyword":       kw,
                        "keyword_ru":    kw,
                        "category":      CATEGORY_MAP.get(kw, "general"),
                        "platform":      "google",
                        "search_volume": int(latest_val * 10),  # Google Trends 是 0-100 指数，放大10倍
                        "trend_score":   round(latest_val, 2),
                        "growth_rate":   round(growth, 4),
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })

            except Exception as e:
                logger.warning(f"pytrends group {group} failed: {e}")
                continue

    except Exception as e:
        logger.error(f"pytrends init failed: {e}")

    return results
