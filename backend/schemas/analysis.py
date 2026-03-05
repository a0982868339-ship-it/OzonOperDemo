from pydantic import BaseModel
from typing import List, Optional

class MarketTrendResponse(BaseModel):
    keyword: str
    heat_score: int
    trend_percent: str
    source_platform: str
    word_type: str

class KeywordCompetitionResponse(BaseModel):
    search_index: int
    product_count: int
    supply_demand_ratio: float
    competition_level: str  # low, medium, high

class WordCloudItem(BaseModel):
    text: str
    value: int

class CategorySalesResponse(BaseModel):
    category_name: str
    sales_share: float
    trend_data: List[int]

class ProductPotentialResponse(BaseModel):
    product_name: str
    sales_volume: int
    profit_margin: float
    growth_rate: float
    rank: int

class RestockPlanResponse(BaseModel):
    category: str
    recommended_quantity: int
    priority: str  # high, medium, low
    reason: str

class PricingStrategyResponse(BaseModel):
    product_id: str
    current_price: float
    recommended_price_range: List[float]
    price_index: float
    strategy: str

from datetime import date, datetime
from typing import Dict, Any

class ShopPerformanceResponse(BaseModel):
    id: int
    shop_id: str
    category: str
    subcategory: str
    record_date: date
    sales_units: int
    revenue: float
    profit: float
    exposure: int
    conversion_rate: float
    price: float
    competitor_avg_price: float
    price_index: float
    supply_demand_score: float

class AIAssetResponse(BaseModel):
    id: int
    task_id: str
    asset_type: str
    status: str
    prompt_text: Optional[str]
    result_data: Optional[Dict[str, Any]]
    created_at: datetime
