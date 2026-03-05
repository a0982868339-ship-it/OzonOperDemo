import random
import sys
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Iterable, TypeVar, List, Tuple

root_path = Path(__file__).resolve().parents[2]
sys.path.append(str(root_path))

from backend.core.database import SessionLocal, engine, Base
from backend.models.market_trend import MarketTrend
from backend.models.shop_performance import ShopPerformance
from backend.services.analyst_service import AnalystService


def build_keywords() -> List[str]:
    return [
        "автопоилка для животных",
        "зимняя куртка",
        "термобелье",
        "когтеточка",
        "лежанка для собак",
        "сушилка для обуви",
        "умная кормушка",
        "снегоступы",
    ]


def build_categories() -> List[Tuple[str, List[str]]]:
    return [
        ("Pet Supplies", ["Auto Waterer", "Smart Feeder", "Cat Litter Box", "Grooming Glove"]),
        ("Winter Apparel", ["Thermal Jacket", "Snow Boots", "Wool Gloves", "Thermal Pants"]),
        ("Home Cleaning", ["Odor Spray", "Floor Cleaner", "UV Sterilizer"]),
        ("Smart Devices", ["Smart Camera", "Air Quality Sensor", "Smart Plug"]),
    ]


def build_platforms() -> List[str]:
    return ["Ozon", "Wildberries", "Yandex.Market", "VK", "OK"]


def generate_market_trends(start_date: date, days: int) -> List[MarketTrend]:
    keywords = build_keywords()
    categories = build_categories()
    platforms = build_platforms()
    trends: List[MarketTrend] = []
    for day in range(days):
        current_date = start_date - timedelta(days=day)
        for keyword in keywords:
            category = random.choice(categories)[0]
            platform = random.choice(platforms)
            search_volume = random.randint(1200, 15000)
            social_mentions = random.randint(300, 4200)
            growth_rate = round(random.uniform(0.02, 0.35), 4)
            product_count = random.randint(100, 6000)
            score = AnalystService.supply_demand_score(
                float(search_volume),
                float(social_mentions),
                float(growth_rate),
                float(product_count),
            )
            trends.append(
                MarketTrend(
                    keyword=keyword,
                    category=category,
                    platform=platform,
                    time_range="7d",
                    search_volume=search_volume,
                    social_mentions=social_mentions,
                    growth_rate=growth_rate,
                    product_count=product_count,
                    supply_demand_score=float(round(score, 4)),
                    created_at=datetime.combine(current_date, datetime.min.time()),
                )
            )
    return trends


def generate_shop_performance(start_date: date, days: int) -> List[ShopPerformance]:
    categories = build_categories()
    platforms = build_platforms()
    records: List[ShopPerformance] = []
    for day in range(days):
        current_date = start_date - timedelta(days=day)
        for category, subcategories in categories:
            for sub in subcategories:
                sales_units = random.randint(12, 220)
                price = round(random.uniform(12, 65), 2)
                revenue = round(sales_units * price, 2)
                profit = round(revenue * random.uniform(0.2, 0.45), 2)
                exposure = random.randint(800, 12000)
                conversion_rate = round(random.uniform(0.01, 0.08), 4)
                competitor_avg_price = round(price * random.uniform(0.85, 1.2), 2)
                price_index = AnalystService.price_index(price, competitor_avg_price)
                supply_demand = AnalystService.supply_demand_score(
                    float(exposure),
                    float(random.randint(200, 2600)),
                    float(random.uniform(0.01, 0.3)),
                    float(random.randint(100, 5000)),
                )
                records.append(
                    ShopPerformance(
                        shop_id=f"S-{platforms.index(random.choice(platforms)) + 1:02d}",
                        category=category,
                        subcategory=sub,
                        record_date=current_date,
                        sales_units=sales_units,
                        revenue=revenue,
                        profit=profit,
                        exposure=exposure,
                        conversion_rate=conversion_rate,
                        price=price,
                        competitor_avg_price=competitor_avg_price,
                        price_index=float(round(price_index, 4)),
                        supply_demand_score=float(round(supply_demand, 4)),
                    )
                )
    return records


ItemType = TypeVar("ItemType")


def chunked(items: Iterable[ItemType], size: int) -> Iterable[List[ItemType]]:
    batch: List[ItemType] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def run(seed: int = 42, days: int = 60) -> None:
    random.seed(seed)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.query(MarketTrend).delete()
        session.query(ShopPerformance).delete()
        start_date = datetime.utcnow().date()
        trends = generate_market_trends(start_date, days)
        records = generate_shop_performance(start_date, max(14, days // 2))
        for batch in chunked(trends, 500):
            session.add_all(batch)
            session.commit()
        for batch in chunked(records, 500):
            session.add_all(batch)
            session.commit()


if __name__ == "__main__":
    run()
