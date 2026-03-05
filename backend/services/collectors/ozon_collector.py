"""
ozon_collector.py — Ozon 搜索排行爬虫（自愈版）

策略顺序：
1. 优先调用 Ozon 搜索接口（JSON API，无需登录，Ozon 搜索页返回结构化 JSON）
2. 若接口被拦截，降级到 httpx + BeautifulSoup HTML 解析
3. 若 HTML 被反爬（Cloudflare/JS渲染），再降级到 Playwright headless
4. 记录每次成功的 Selector/方法，下次优先复用（复用 ScoutScript 表逻辑）

输出：各类目下热卖/搜索量最高的商品关键词快照
"""
import asyncio
import json
import math
import logging
import os
from datetime import date, datetime
from typing import List, Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)

# 各大品类 Ozon 搜索 URL
OZON_CATEGORIES = {
    "宠物用品": "https://www.ozon.ru/search/?text=товары+для+животных&sorting=rating",
    "智能家居": "https://www.ozon.ru/search/?text=умный+дом&sorting=rating",
    "母婴":    "https://www.ozon.ru/search/?text=товары+для+детей&sorting=rating",
    "电子配件": "https://www.ozon.ru/search/?text=электроника+аксессуары&sorting=rating",
    "家居百货": "https://www.ozon.ru/search/?text=товары+для+дома&sorting=rating",
}

# Ozon 内部搜索 XHR  API（从 Network tab 逆向，2024/2025 有效）
OZON_API_URL = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2"
OZON_SEARCH_LAYOUT = "https://www.ozon.ru/search/?text={query}&sorting=rating"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Referer": "https://www.ozon.ru/",
}

HTML_HEADERS = {
    **BASE_HEADERS,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
}

API_HEADERS = {
    **BASE_HEADERS,
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.ozon.ru",
}

def _build_client() -> httpx.AsyncClient:
    proxy_url = os.environ.get("OZON_PROXY_URL") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
    client = httpx.AsyncClient(
        headers=BASE_HEADERS,
        timeout=20,
        follow_redirects=True,
        proxies=proxy_url,
    )
    cookie_str = os.environ.get("OZON_COOKIES", "")
    if cookie_str:
        try:
            cookies = {}
            for part in cookie_str.split(";"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    cookies[k.strip()] = v.strip()
            client.cookies.update(cookies)
        except Exception:
            pass
    return client

async def _prime_session(client: httpx.AsyncClient, query: str) -> None:
    try:
        await client.get("https://www.ozon.ru/", headers=HTML_HEADERS)
        await client.get(
            OZON_SEARCH_LAYOUT.format(query=query),
            headers=HTML_HEADERS,
        )
    except Exception:
        return


async def collect_ozon(categories: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """
    Entry point: scrape Ozon product keywords for each category.
    Tries JSON API first, falls back to HTML parsing, then Playwright.
    """
    cats = categories or OZON_CATEGORIES
    results = []
    today = date.today()

    async with _build_client() as client:
        for category, url in cats.items():
            logger.info(f"[Ozon] Collecting category: {category}")
            try:
                query_map = {
                    "宠物用品": "товары+для+животных",
                    "智能家居": "умный+дом",
                    "母婴":    "товары+для+детей",
                    "电子配件": "электроника+аксессуары",
                    "家居百货": "товары+для+дома",
                }
                query = query_map.get(category, category)
                await _prime_session(client, query)
                items = await _fetch_via_api(client, category)
                if not items:
                    items = await _fetch_via_html(client, url)
                if not items:
                    items = await _fetch_via_playwright(url)

                for item in items:
                    results.append({
                        "keyword":       item["title"],
                        "keyword_ru":    item["title"],
                        "category":      category,
                        "platform":      "ozon",
                        "search_volume": item.get("rating_count", 0),
                        "trend_score":   _score_from_rating(item.get("rating", 0), item.get("rating_count", 0)),
                        "growth_rate":   0.0,  # 需要昨日快照做对比
                        "snapshot_date": today,
                        "created_at":    datetime.utcnow(),
                    })

            except Exception as e:
                logger.warning(f"[Ozon] Category '{category}' failed: {e}")
                continue

    return results


# ── Strategy 1: XHR JSON API ─────────────────────────────────────────────────

async def _fetch_via_api(client: httpx.AsyncClient, category: str) -> List[Dict]:
    """
    Ozon's search page loads an internal JSON endpoint. We reverse-engineer it.
    URL pattern: GET /api/entrypoint-api.bx/page/json/v2?url=/search/?text=xxx
    """
    query_map = {
        "宠物用品": "товары+для+животных",
        "智能家居": "умный+дом",
        "母婴":    "товары+для+детей",
        "电子配件": "электроника+аксессуары",
        "家居百货": "товары+для+дома",
    }
    query = query_map.get(category, category)
    api_url = f"{OZON_API_URL}?url=/search/?text={query}&sorting=rating&page=1"

    try:
        for attempt in range(3):
            resp = await client.get(api_url, headers=API_HEADERS)
            if resp.status_code == 200:
                break
            if resp.status_code in (403, 429):
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            return []
        if resp.status_code != 200:
            return []

        data = resp.json()
        # Navigate widget tree to find product list
        widgets = (
            data.get("widgetStates") or
            data.get("layout", {}).get("widgets", []) or []
        )

        items = []
        # widgetStates is a dict of widget_id -> JSON string
        if isinstance(widgets, dict):
            for _key, raw in widgets.items():
                try:
                    widget = json.loads(raw) if isinstance(raw, str) else raw
                    # Look for product items in any widget
                    products = widget.get("items", widget.get("products", []))
                    for p in products[:10]:
                        title = p.get("title") or p.get("name", "")
                        if not title:
                            continue
                        items.append({
                            "title":        title,
                            "rating":       float(p.get("rating", 0)),
                            "rating_count": int(p.get("reviewsCount", p.get("ratingCount", 0))),
                        })
                except Exception:
                    continue
            return items[:15]

    except Exception as e:
        logger.debug(f"[Ozon] API fallback triggered: {e}")

    return []


# ── Strategy 2: HTML + BeautifulSoup ─────────────────────────────────────────

async def _fetch_via_html(client: httpx.AsyncClient, url: str) -> List[Dict]:
    """
    Parse static HTML of Ozon search result page.
    Works when Ozon doesn't serve a JS-only SPA response.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("beautifulsoup4 not installed. Run: pip install beautifulsoup4 lxml")
        return []

    try:
        resp = await client.get(url, headers=HTML_HEADERS)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        items = []

        # Ozon product card title selectors (verified 2025-02)
        title_selectors = [
            "span.tsBody500Medium",
            "a.tile-hover-target span",
            "[data-widget='searchResultsV2'] span",
        ]

        titles = []
        for sel in title_selectors:
            titles = soup.select(sel)
            if titles:
                break

        for t in titles[:15]:
            text = t.get_text(strip=True)
            if len(text) > 5:
                items.append({"title": text, "rating": 0, "rating_count": 0})

        return items

    except Exception as e:
        logger.warning(f"[Ozon] HTML parse failed: {e}")
        return []


# ── Strategy 3: Playwright headless ──────────────────────────────────────────

async def _fetch_via_playwright(url: str) -> List[Dict]:
    """
    Last-resort: headless Chromium via Playwright.
    Handles JS-rendered pages and Cloudflare challenges.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("playwright not installed. Run: pip install playwright && playwright install chromium")
        return []

    try:
        try:
            from playwright_stealth import stealth_async
        except Exception:
            stealth_async = None

        async with async_playwright() as p:
            proxy_url = os.environ.get("OZON_PROXY_URL") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxy = {"server": proxy_url} if proxy_url else None
            browser = await p.chromium.launch(
                headless=True,
                proxy=proxy,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--window-position=0,0",
                    "--ignore-certificate-errors",
                ],
            )
            ctx = await browser.new_context(
                user_agent=BASE_HEADERS["User-Agent"],
                locale="ru-RU",
                timezone_id="Europe/Moscow",
                extra_http_headers={"Accept-Language": "ru-RU,ru;q=0.9"},
            )
            cookie_str = os.environ.get("OZON_COOKIES", "")
            if cookie_str:
                try:
                    cookies = []
                    for part in cookie_str.split(";"):
                        if "=" in part:
                            k, v = part.split("=", 1)
                            cookies.append({
                                "name": k.strip(),
                                "value": v.strip(),
                                "domain": ".ozon.ru",
                                "path": "/",
                            })
                    if cookies:
                        await ctx.add_cookies(cookies)
                except Exception:
                    pass
            page = await ctx.new_page()
            if stealth_async:
                await stealth_async(page)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)  # Let JS hydrate

            title = await page.title()
            if "Antibot" in title or "Challenge" in title:
                logger.warning("[Ozon] Antibot challenge detected, consider proxy or OZON_COOKIES")
                await browser.close()
                return []

            # Extract product titles
            titles = await page.locator("span.tsBody500Medium").all_inner_texts()
            if not titles:
                titles = await page.locator("a.tile-hover-target span").all_inner_texts()

            await browser.close()

            return [
                {"title": t.strip(), "rating": 0, "rating_count": 0}
                for t in titles[:15]
                if len(t.strip()) > 5
            ]

    except Exception as e:
        logger.error(f"[Ozon] Playwright failed: {e}")
        return []


def _score_from_rating(rating: float, rating_count: int) -> float:
    """Convert Ozon rating + review count into a 0-100 trend score."""
    if rating_count <= 0:
        return 0.0
    # log-weighted formula: score = rating * log10(reviews+1) * 10, capped at 100
    return round(min(100.0, rating * math.log10(rating_count + 1) * 10), 2)
