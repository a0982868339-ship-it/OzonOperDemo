"""
yandex_collector.py — Yandex Wordstat 关键词热度采集器

Yandex 是俄罗斯第一大搜索引擎（约 60% 市场份额），数据远比 Google Trends 准确。

两种模式：
1. Yandex Wordstat API（官方，需申请 OAuth Token）
   - 文档：https://yandex.com/dev/wordstat/
   - Token 配置：YANDEX_OAUTH_TOKEN + YANDEX_CLIENT_ID
2. 无 Key 降级：基于 Yandex 搜索结果页面的 suggest API（免费，无需认证）
   - GET https://suggest-maps.yandex.ru/suggest-geo → 搜索建议词量
   - GET https://wordstat.yandex.ru/ → 需要登录，跳过
"""
import asyncio
import httpx
import math
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── 关键词配置 ─────────────────────────────────────────────────────────────
YANDEX_KEYWORDS = {
    "宠物用品": [
        "автокормушка для кошек",
        "умная кормушка",
        "автопоилка для кошек",
        "GPS ошейник для собак",
        "когтеточка для кошек",
        "лежанка для кошек",
    ],
    "智能家居": [
        "умный дом",
        "умная колонка Яндекс",
        "wi-fi розетка",
        "умная лампочка",
    ],
    "母婴": [
        "детская коляска",
        "детские игрушки",
        "подгузники",
        "слинг для ребёнка",
    ],
    "电子配件": [
        "беспроводные наушники",
        "power bank",
        "чехол для телефона",
    ],
    "家居百货": [
        "роботы пылесосы",
        "товары для дома",
        "органайзеры для хранения",
    ],
}

YANDEX_SUGGEST_URL = "https://yandex.ru/suggest/suggest-ya.cgi"


async def collect_yandex(oauth_token: str = "", client_id: str = "") -> List[Dict[str, Any]]:
    """
    Entry point. Tries official Wordstat API first, falls back to suggest API.
    """
    if oauth_token and client_id:
        results = await _collect_via_wordstat_api(oauth_token, client_id)
        if results:
            return results

    # Fallback: Yandex Suggest (free, no auth)
    return await _collect_via_suggest()


# ── Strategy 1: Official Wordstat API ────────────────────────────────────────

async def _collect_via_wordstat_api(token: str, client_id: str) -> List[Dict[str, Any]]:
    """
    Uses Yandex Wordstat JSON API.
    Endpoint: POST https://api.wordstat.yandex.com/v1/keyword-summary
    Auth: OAuth token in Authorization header
    """
    results = []
    today = date.today()
    all_keywords = [kw for kws in YANDEX_KEYWORDS.values() for kw in kws]

    headers = {
        "Authorization": f"OAuth {token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # Wordstat API supports batch requests
            payload = {
                "Keywords": all_keywords[:10],  # max 10 per request
                "GeoID": [213],  # 213 = Москва; 0 = Россия
                "DateRange": "LAST_7_DAYS",
            }
            resp = await client.post(
                "https://api.wordstat.yandex.com/v1/keyword-summary",
                json=payload,
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", []):
                    kw = item.get("keyword", "")
                    shows = item.get("shows", 0)
                    cat = _find_category(kw)
                    results.append({
                        "keyword":       kw,
                        "keyword_ru":    kw,
                        "category":      cat,
                        "platform":      "yandex",
                        "search_volume": shows,
                        "trend_score":   min(100.0, math.log10(shows + 1) * 14),
                        "growth_rate":   0.0,
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })
    except Exception as e:
        logger.warning(f"[Yandex] Wordstat API failed: {e}")

    return results


# ── Strategy 2: Yandex Suggest API (free, no auth) ───────────────────────────

async def _collect_via_suggest() -> List[Dict[str, Any]]:
    """
    Uses Yandex's public search suggest endpoint.
    Returns relative popularity derived from number of suggest completions.
    Works without any API key.
    """
    results = []
    today = date.today()

    async with httpx.AsyncClient(timeout=15) as client:
        for category, keywords in YANDEX_KEYWORDS.items():
            for kw in keywords:
                try:
                    resp = await client.get(
                        YANDEX_SUGGEST_URL,
                        params={
                            "v":    4,
                            "part": kw,
                            "lang": "ru",
                            "lr":   213,   # Moscow
                        },
                    )
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    # Response format: ["query", ["suggestion1", "suggestion2", ...]]
                    suggestions = data[1] if isinstance(data, list) and len(data) > 1 else []

                    # Count how many suggestions contain our keyword = popularity proxy
                    match_count = sum(1 for s in suggestions if kw.lower() in str(s).lower())
                    # Presence itself = high signal (Yandex only suggests popular terms)
                    score = 30.0 + min(70.0, len(suggestions) * 8.0) if suggestions else 10.0

                    results.append({
                        "keyword":       kw,
                        "keyword_ru":    kw,
                        "category":      category,
                        "platform":      "yandex",
                        "search_volume": int(score * 1000),
                        "trend_score":   round(score, 2),
                        "growth_rate":   0.0,
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })
                    await asyncio.sleep(0.3)  # be polite

                except Exception as e:
                    logger.debug(f"[Yandex] Suggest failed for '{kw}': {e}")
                    continue

    return results


def _find_category(kw: str) -> str:
    for cat, kws in YANDEX_KEYWORDS.items():
        if kw in kws:
            return cat
    return "general"
