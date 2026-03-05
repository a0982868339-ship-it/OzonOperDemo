import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.models.scout_raw import ScoutRaw
from backend.models.scout_item import ScoutItem
from backend.schemas.scout import ScoutRunRequest, ScoutRunResponse, ScoutItemInput, ScoutSourcePayload
from backend.services.cache import cache_get, cache_set
from backend.scout.platforms import PLATFORM_CONFIGS
from backend.agents.scout_agent import ScoutAgent


class ScoutService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.agent = ScoutAgent(db)

    async def run_keyword_mission(self, keyword: str, platform: str = "ozon") -> Dict[str, Any]:
        """
        Triggers a live crawl mission for a keyword on a specific platform.
        Uses predefined configs if available.
        """
        config = PLATFORM_CONFIGS.get(platform.lower())
        if not config:
            return {"error": f"Platform {platform} not supported yet."}
            
        url = config["url_template"].format(keyword=keyword)
        goal = config["goal"]
        selectors = config["selectors"]
        
        # Call Agent
        result = await self.agent.run_mission(url, goal, selectors)
        
        if result.get("status") in ["success", "healed"]:
            # Ingest result into DB
            data = result.get("data", {})
            
            # Map result to ScoutItemInput
            # The agent returns a single dict if it's a single item page, 
            # or we might need to adjust the crawler to return a list of items for search pages.
            # For now, let's assume the agent returns a single object or list.
            # If the crawler returns a list of items, we should handle it.
            # But base_crawler template currently returns a single dict of found elements.
            # To support search results (list), the selector needs to be list-aware (e.g. using `select` instead of `select_one`).
            # For this MVP, let's treat the result as a single "summary" or try to map it.
            
            # TODO: Improve base_crawler to support list extraction
            # For now, we create a single "Snapshot" item from the result
            
            item_input = ScoutItemInput(
                title=data.get("title", f"{keyword} Result"),
                price=self._parse_price(data.get("price")),
                currency="RUB",
                rating=self._parse_float(data.get("rating")),
                reviews=self._parse_int(data.get("reviews")),
                sales_estimate=0, # Hard to get from search page directly without deep parsing
                platform=platform,
                category=None
            )
            
            # Create a ScoutRunRequest internally to reuse ingest logic
            run_req = ScoutRunRequest(
                keyword=keyword,
                category="General",
                platform=platform,
                sources=[
                    ScoutSourcePayload(
                        source=platform,
                        url=url,
                        raw_payload=data,
                        items=[item_input]
                    )
                ]
            )
            self.ingest(run_req)
            return {"status": "success", "items_count": 1, "details": result}
            
        return {"status": "failed", "details": result}

    def _parse_price(self, price_str: Any) -> float:
        if not price_str:
            return 0.0
        try:
            # Remove non-numeric chars except dot/comma
            clean = "".join(c for c in str(price_str) if c.isdigit() or c in ".,")
            clean = clean.replace(",", ".")
            return float(clean)
        except:
            return 0.0

    def _parse_float(self, val: Any) -> float:
        try:
            return float(val)
        except:
            return 0.0

    def _parse_int(self, val: Any) -> int:
        try:
            return int("".join(filter(str.isdigit, str(val))))
        except:
            return 0

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _default_items(self, keyword: str, category: Optional[str], platform: Optional[str]) -> List[ScoutItemInput]:
        return [
            ScoutItemInput(
                title=f"{keyword} 标准款",
                price=2490.0,
                currency="RUB",
                rating=4.6,
                reviews=128,
                sales_estimate=520,
                category=category,
                subcategory=None,
                platform=platform,
            )
        ]

    def ingest(self, payload: ScoutRunRequest) -> ScoutRunResponse:
        now = datetime.utcnow()
        raw_count = 0
        item_count = 0
        cached_items: List[Dict[str, Any]] = []

        for source in payload.sources:
            payload_hash = self._hash_payload(source.raw_payload)
            raw_record = ScoutRaw(
                keyword=payload.keyword,
                source=source.source,
                url=source.url,
                payload_hash=payload_hash,
                raw_payload=json.dumps(source.raw_payload, ensure_ascii=False),
                fetched_at=now,
            )
            self.db.add(raw_record)
            self.db.flush()
            raw_count += 1

            items = source.items or self._default_items(payload.keyword, payload.category, payload.platform)
            for item in items:
                record = ScoutItem(
                    raw_id=raw_record.id,
                    keyword=payload.keyword,
                    title=item.title,
                    price=item.price,
                    currency=item.currency,
                    rating=item.rating,
                    reviews=item.reviews,
                    sales_estimate=item.sales_estimate,
                    category=item.category or payload.category,
                    subcategory=item.subcategory,
                    platform=item.platform or payload.platform or source.source,
                    captured_at=now,
                )
                self.db.add(record)
                item_count += 1
                cached_items.append(self._serialize_item(record))

        self.db.commit()

        cache_key = self._cache_key(payload.keyword, payload.category, payload.platform, 50)
        cache_set(cache_key, {"items": cached_items}, ttl=300)

        return ScoutRunResponse(keyword=payload.keyword, raw_count=raw_count, item_count=item_count)

    def _serialize_item(self, item: ScoutItem) -> Dict[str, Any]:
        return {
            "id": item.id,
            "raw_id": item.raw_id,
            "keyword": item.keyword,
            "title": item.title,
            "price": item.price,
            "currency": item.currency,
            "rating": item.rating,
            "reviews": item.reviews,
            "sales_estimate": item.sales_estimate,
            "category": item.category,
            "subcategory": item.subcategory,
            "platform": item.platform,
            "captured_at": item.captured_at,
        }

    def _cache_key(self, keyword: Optional[str], category: Optional[str], platform: Optional[str], limit: int) -> str:
        return f"scout:items:{keyword or 'all'}:{category or 'all'}:{platform or 'all'}:{limit}"

    def list_items(
        self,
        keyword: Optional[str],
        category: Optional[str],
        platform: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        cache_key = self._cache_key(keyword, category, platform, limit)
        cached = cache_get(cache_key)
        if cached and "items" in cached:
            return cached["items"]

        query = self.db.query(ScoutItem)
        if keyword:
            query = query.filter(ScoutItem.keyword == keyword)
        if category:
            query = query.filter(ScoutItem.category == category)
        if platform:
            query = query.filter(ScoutItem.platform == platform)
        records = query.order_by(ScoutItem.id.desc()).limit(limit).all()
        items = [self._serialize_item(r) for r in records]
        cache_set(cache_key, {"items": items}, ttl=300)
        return items
