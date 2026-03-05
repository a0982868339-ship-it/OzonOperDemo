import random
import math
from datetime import datetime, timedelta


def generate_mock_dataset(days: int = 180, seed: int = 42):
    random.seed(seed)
    today = datetime.utcnow().date()
    categories = [
        ("宠物用品", "宠物饮水机"),
        ("宠物用品", "智能喂食器"),
        ("宠物用品", "宠物理毛手套"),
        ("家居清洁", "除臭喷雾"),
        ("家居清洁", "地面清洁器"),
        ("智能设备", "智能摄像头"),
        ("户外用品", "旅行背包"),
        ("户外用品", "保温垫"),
    ]
    products = []
    for index, (c1, c2) in enumerate(categories, start=1):
        cost = random.randint(8, 22)
        price = cost + random.randint(10, 30)
        products.append(
            {
                "product_id": f"P{index:03d}",
                "category_l1": c1,
                "category_l2": c2,
                "cost": cost,
                "price": price,
            }
        )
    orders = []
    exchange_rates = []
    for day in range(days):
        date = (today - timedelta(days=day)).isoformat()
        seasonal = 1 + 0.35 * math.sin(2 * math.pi * day / 90)
        fx_rate = round(0.011 + 0.0015 * math.sin(2 * math.pi * day / 60) + random.random() * 0.0005, 6)
        exchange_rates.append({"date": date, "rate": fx_rate})
        daily_orders = int(20 * seasonal) + random.randint(0, 8)
        for _ in range(daily_orders):
            product = random.choice(products)
            quantity = max(1, int(random.random() * 3) + 1)
            amount = round(product["price"] * quantity * (0.9 + random.random() * 0.3), 2)
            orders.append(
                {
                    "order_id": f"O{random.randint(100000, 999999)}",
                    "product_id": product["product_id"],
                    "category_l1": product["category_l1"],
                    "category_l2": product["category_l2"],
                    "quantity": quantity,
                    "amount": amount,
                    "date": date,
                    "fx_rate": fx_rate,
                }
            )
    return {
        "orders": orders,
        "products": products,
        "exchange_rates": exchange_rates,
        "meta": {"days": days, "seed": seed},
    }
