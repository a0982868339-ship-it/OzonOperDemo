from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SupplyDemandWeights:
    search_weight: float = 0.6
    social_weight: float = 0.3
    growth_weight: float = 0.1
    epsilon: float = 0.0001


class AnalystService:
    @staticmethod
    def supply_demand_score(
        search_volume: float,
        social_mentions: float,
        growth_rate: float,
        product_count: float,
        weights: Optional[SupplyDemandWeights] = None,
    ) -> float:
        applied = weights or SupplyDemandWeights()
        weighted = (
            search_volume * applied.search_weight
            + social_mentions * applied.social_weight
            + growth_rate * applied.growth_weight * 10000
        )
        return weighted / (product_count + applied.epsilon)

    @staticmethod
    def calculate_competition_level(supply_demand_ratio: float) -> str:
        if supply_demand_ratio > 10:
            return "low"
        elif supply_demand_ratio > 2:
            return "medium"
        return "high"

    @staticmethod
    def generate_restock_plan(sales_velocity: float, current_stock: int, lead_time_days: int) -> dict:
        # Simple heuristic for restocking
        daily_sales = sales_velocity / 30
        needed = daily_sales * (lead_time_days + 14)  # +2 weeks safety stock
        to_order = max(0, needed - current_stock)
        
        priority = "low"
        if to_order > current_stock:
            priority = "high"
        elif to_order > 0:
            priority = "medium"
            
        return {
            "recommended_quantity": int(to_order),
            "priority": priority
        }
