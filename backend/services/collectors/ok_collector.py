"""
ok_collector.py — OK (Одноклассники) 热词采集器

OK 是俄罗斯第二大社交平台，主要用户群体：女性、30+ 岁、二三线城市。
通过 OK API 抓取公开主题讨论热度。

配置：
  OK_APP_ID      — 在 ok.ru/devaccess 创建应用获得
  OK_APP_KEY     — 同上
  OK_ACCESS_TOKEN — OAuth 授权后获得

文档：https://apiok.ru/en/dev/methods/rest/stream/stream.get
"""
import asyncio
import hashlib
import httpx
import math
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

OK_API_BASE = "https://api.ok.ru/fb.do"

OK_SEARCH_QUERIES = {
    "宠物用品": ["автокормушка кошки", "товары для животных", "игрушки питомец"],
    "智能家居": ["умный дом", "умные устройства дом"],
    "母婴":    ["детские товары", "коляска", "детские игрушки"],
    "电子配件": ["наушники bluetooth", "гаджеты смартфон"],
    "家居百货": ["полезное для дома", "хранение вещей"],
}


def _sign_ok_request(params: dict, app_key: str, session_secret_key: str) -> str:
    """OK API signature: MD5(sorted params concat + session_secret_key)"""
    sorted_params = "".join(f"{k}={v}" for k, v in sorted(params.items()) if k != "sig")
    raw = sorted_params + session_secret_key
    return hashlib.md5(raw.encode()).hexdigest().upper()


async def collect_ok(
    app_id: str = "",
    app_key: str = "",
    access_token: str = "",
    session_secret_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Collects OK stream search results for product keywords.
    Requires app credentials and a user access token.
    """
    if not all([app_id, app_key, access_token, session_secret_key]):
        logger.warning("[OK] OK credentials not configured, skipping OK collection")
        return []

    results = []
    today = date.today()

    async with httpx.AsyncClient(timeout=20) as client:
        for category, queries in OK_SEARCH_QUERIES.items():
            for query in queries:
                try:
                    params = {
                        "application_id": app_id,
                        "application_key": app_key,
                        "method": "stream.search",
                        "q": query,
                        "count": 100,
                        "format": "json",
                        "access_token": access_token,
                    }
                    params["sig"] = _sign_ok_request(params, app_key, session_secret_key)

                    resp = await client.get(OK_API_BASE, params=params)
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    if "error_code" in data:
                        logger.warning(f"[OK] API error for '{query}': {data}")
                        continue

                    count = data.get("totalCount", len(data.get("items", [])))
                    score = min(100.0, math.log10(count + 1) * 20)

                    results.append({
                        "keyword":       query,
                        "keyword_ru":    query,
                        "category":      category,
                        "platform":      "ok",
                        "search_volume": count,
                        "trend_score":   round(score, 2),
                        "growth_rate":   0.0,
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.warning(f"[OK] Query '{query}' failed: {e}")
                    continue

    logger.info(f"[OK] Collected {len(results)} keywords")
    return results
