"""
wb_collector.py — Wildberries (WB) 爬虫采集器

Wildberries 是俄罗斯最大电商平台，无需 API Key 即可访问其公开搜索接口。

WB 提供两个公开接口：
1. /api/v2/search/products — 关键词搜索结果（含销量、评分等）
2. /api/v2/catalog/{categoryId}/products — 品类热销榜单

完全免费，无需注册。
"""
import asyncio
import httpx
import math
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# WB 搜索 API（CDN）
WB_SEARCH_API = "https://search.wb.ru/exactmatch/ru/common/v4/search"
WB_CATALOG_API = "https://catalog.wb.ru/catalog"

# 分品类搜索词
WB_QUERIES = {
    "宠物用品": [
        "автокормушка для кошек",
        "когтеточка угловая",
        "лежанка для кошки",
        "игрушки для кошек",
        "ошейник для собаки",
    ],
    "智能家居": [
        "умная розетка wifi",
        "лампочка умная",
        "датчик движения умный дом",
    ],
    "母婴": [
        "коляска детская",
        "игрушки мягкие для малышей",
        "подгузники ночные",
    ],
    "电子配件": [
        "наушники беспроводные",
        "зарядка беспроводная",
        "чехол для телефона",
    ],
    "家居百货": [
        "органайзер для хранения",
        "контейнер для хранения",
        "набор для кухни",
    ],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.wildberries.ru/",
}


async def collect_wb(queries: Optional[Dict[str, list]] = None) -> List[Dict[str, Any]]:
    """
    Scrapes Wildberries search API for each query keyword.
    Extracts product titles ranked by popularity.
    No API key needed.
    """
    all_queries = queries or WB_QUERIES
    results = []
    today = date.today()

    async with httpx.AsyncClient(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        for category, kws in all_queries.items():
            for kw in kws:
                try:
                    resp = None
                    for attempt in range(3):  # retry up to 3 times on 429
                        resp = await client.get(
                            WB_SEARCH_API,
                            params={
                                "appType": 1,
                                "curr": "rub",
                                "dest": -1257786,  # Moscow delivery dest
                                "query": kw,
                                "resultset": "catalog",
                                "sort": "popular",
                                "spp": 30,
                                "suppressSpellcheck": "false",
                            },
                        )
                        if resp.status_code == 429:
                            wait = 5 * (attempt + 1)
                            logger.debug(f"[WB] 429 rate limited, waiting {wait}s...")
                            await asyncio.sleep(wait)
                            continue
                        break

                    if resp.status_code != 200:
                        logger.debug(f"[WB] HTTP {resp.status_code} for '{kw}'")
                        continue

                    data = resp.json()
                    products = (
                        data.get("data", {}).get("products") or
                        data.get("value", {}).get("data", {}).get("products") or
                        []
                    )

                    if not products:
                        continue

                    # Use search result count as proxy for demand
                    total = data.get("data", {}).get("total", len(products))
                    score = min(100.0, math.log10(total + 1) * 14)

                    # Top product names as keyword
                    top = products[0]
                    title = top.get("name", kw)
                    feedbacks = top.get("feedbacks", 0)
                    rating = float(top.get("rating", 0))

                    results.append({
                        "keyword":       title,
                        "keyword_ru":    title,
                        "category":      category,
                        "platform":      "wb",
                        "search_volume": total,
                        "trend_score":   round(score, 2),
                        "growth_rate":   0.0,
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })

                    await asyncio.sleep(2.0)  # WB rate limit: be polite

                except Exception as e:
                    logger.warning(f"[WB] Query '{kw}' failed: {e}")
                    continue

    logger.info(f"[WB] Collected {len(results)} keywords")
    return results
