
"""
vk_collector.py — VK (ВКонтакте) 热词采集器

VK 是俄罗斯最大社交平台，约 1 亿月活用户。
通过 VK API 抓取：公开社区帖子热度、话题标签趋势。

配置：VK_ACCESS_TOKEN（通过 vk.com/dev 申请 Standalone App 即可获取，免费）
"""
import asyncio
import httpx
import math
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

VK_API_BASE = "https://api.vk.com/method"
VK_API_VERSION = "5.199"

# 搜索的关键词（同时也是话题标签）
VK_SEARCH_QUERIES = {
    "宠物用品": [
        "автокормушка для кошек",
        "умная кормушка питомец",
        "товары для животных",
        "кошачьи игрушки",
    ],
    "智能家居": [
        "умный дом",
        "умная розетка",
        "Яндекс Станция",
    ],
    "母婴": [
        "детские товары",
        "коляска для новорождённых",
        "детские игрушки обзор",
    ],
    "电子配件": [
        "беспроводные наушники обзор",
        "лучший повербанк",
    ],
    "家居百货": [
        "товары для дома Ozon",
        "организация хранения дома",
    ],
}


async def collect_vk(access_token: str = "") -> List[Dict[str, Any]]:
    """
    Collects VK post counts for product-related queries.
    Without token: returns empty (VK API requires token for most methods).
    With token: uses newsfeed.search to count posts mentioning keywords.
    """
    if not access_token:
        logger.warning("[VK] VK_ACCESS_TOKEN not configured, skipping VK collection")
        return []

    results = []
    today = date.today()

    async with httpx.AsyncClient(timeout=20) as client:
        for category, queries in VK_SEARCH_QUERIES.items():
            for query in queries:
                try:
                    # newsfeed.search: count public posts matching keyword (last 24h)
                    resp = await client.get(
                        f"{VK_API_BASE}/newsfeed.search",
                        params={
                            "q":            query,
                            "count":        200,
                            "start_time":   int((datetime.utcnow().timestamp()) - 86400),  # last 24h
                            "extended":     0,
                            "access_token": access_token,
                            "v":            VK_API_VERSION,
                        },
                    )
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    if "error" in data:
                        logger.warning(f"[VK] API error for '{query}': {data['error']}")
                        continue

                    count = data.get("response", {}).get("total_count", 0)
                    score = min(100.0, math.log10(count + 1) * 20)

                    results.append({
                        "keyword":       query,
                        "keyword_ru":    query,
                        "category":      category,
                        "platform":      "vk",
                        "search_volume": count,
                        "trend_score":   round(score, 2),
                        "growth_rate":   0.0,
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })
                    await asyncio.sleep(0.5)  # respect VK rate limit (3 req/s)

                except Exception as e:
                    logger.warning(f"[VK] Query '{query}' failed: {e}")
                    continue

    logger.info(f"[VK] Collected {len(results)} keywords")
    return results
