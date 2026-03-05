from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ScoutItemInput(BaseModel):
    title: str
    price: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    sales_estimate: Optional[int] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    platform: Optional[str] = None


class ScoutSourcePayload(BaseModel):
    source: str
    url: Optional[str] = None
    raw_payload: Dict[str, Any]
    items: Optional[List[ScoutItemInput]] = None


class ScoutRunRequest(BaseModel):
    keyword: str
    category: Optional[str] = None
    platform: Optional[str] = None
    sources: List[ScoutSourcePayload]


class ScoutRunResponse(BaseModel):
    keyword: str
    raw_count: int
    item_count: int


class ScoutItemResponse(BaseModel):
    id: int
    raw_id: int
    keyword: str
    title: str
    price: Optional[float]
    currency: Optional[str]
    rating: Optional[float]
    reviews: Optional[int]
    sales_estimate: Optional[int]
    category: Optional[str]
    subcategory: Optional[str]
    platform: Optional[str]
    captured_at: datetime

    class Config:
        from_attributes = True
