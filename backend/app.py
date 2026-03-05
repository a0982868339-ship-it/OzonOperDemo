from fastapi import FastAPI, Query, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from backend.seed import generate_mock_dataset


app = FastAPI(title="Ozon Demo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = Path(__file__).resolve().parent.parent
frontend_dir = base_dir / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


class ImageRequest(BaseModel):
    name: str
    material: Optional[str] = None
    function: Optional[str] = None
    scenario: Optional[str] = None
    style: Optional[str] = None
    size: Optional[str] = None
    copy: Optional[str] = None


class VideoRequest(BaseModel):
    description: str
    steps: Optional[List[str]] = None
    scenario: Optional[str] = None
    duration: int
    subtitles: Optional[str] = None
    voiceover: Optional[str] = None


class CopyRequest(BaseModel):
    name: str
    selling_points: List[str]
    platform: str
    language: str


class ScoreWeights(BaseModel):
    search: float = 0.6
    social: float = 0.3
    growth: float = 0.1


class ScoreRequest(BaseModel):
    search_volume: float
    social_mentions: float
    growth_rate: float
    product_count: float
    weights: Optional[ScoreWeights] = None


tasks: Dict[str, Dict[str, Any]] = {}


@app.get("/")
def serve_index():
    index_file = frontend_dir / "index.html"
    return FileResponse(index_file)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def generate_date_series(days: int):
    today = datetime.utcnow().date()
    return [(today - timedelta(days=i)).isoformat() for i in range(days)][::-1]


def build_hot_keywords():
    base = [
        {"keyword": "宠物自动饮水机", "source": "Ozon", "pos": "名词", "search": 8200, "social": 2600, "growth": 0.23},
        {"keyword": "猫砂盆防臭", "source": "VK", "pos": "需求词", "search": 6400, "social": 3100, "growth": 0.19},
        {"keyword": "宠物理毛手套", "source": "YouTube", "pos": "场景词", "search": 5400, "social": 2800, "growth": 0.27},
        {"keyword": "犬用止吠器", "source": "Wildberries", "pos": "名词", "search": 4700, "social": 1500, "growth": 0.12},
        {"keyword": "宠物旅行背包", "source": "Yandex.Market", "pos": "场景词", "search": 3900, "social": 1700, "growth": 0.21},
    ]
    result = []
    for item in base:
        heat = item["search"] * 0.6 + item["social"] * 0.3 + item["growth"] * 10000 * 0.1
        result.append(
            {
                "keyword": item["keyword"],
                "heat": round(heat, 2),
                "growth": item["growth"],
                "source": item["source"],
                "pos": item["pos"],
            }
        )
    return result


def demand_supply_index(search_volume: float, social_mentions: float, growth_rate: float, product_count: float, weights: ScoreWeights):
    heat = search_volume * weights.search + social_mentions * weights.social + growth_rate * 10000 * weights.growth
    supply_demand = heat / (product_count + 0.0001)
    return round(heat, 2), round(supply_demand, 4)


@app.get("/api/keywords/hot")
def hot_keywords(range: str = Query("7d"), category: Optional[str] = Query(None)):
    return {"range": range, "category": category, "items": build_hot_keywords()}


@app.get("/api/keywords/competition")
def keyword_competition(keyword: str):
    seed = abs(hash(keyword)) % 10000
    random.seed(seed)
    search_index = random.randint(2000, 12000)
    product_count = random.randint(200, 5000)
    heat, supply_demand = demand_supply_index(search_index, random.randint(800, 3400), random.random() * 0.3, product_count, ScoreWeights())
    if supply_demand > 3:
        level = "低"
    elif supply_demand > 1.2:
        level = "中"
    else:
        level = "高"
    return {
        "keyword": keyword,
        "search_index": search_index,
        "product_count": product_count,
        "supply_demand": supply_demand,
        "level": level,
    }


@app.post("/api/score/demand-supply")
def score_demand_supply(payload: ScoreRequest):
    weights = payload.weights or ScoreWeights()
    heat, supply_demand = demand_supply_index(
        payload.search_volume,
        payload.social_mentions,
        payload.growth_rate,
        payload.product_count,
        weights,
    )
    return {
        "heat": heat,
        "supply_demand": supply_demand,
        "weights": weights.model_dump(),
    }


@app.get("/api/analysis/quadrant")
def quadrant_analysis():
    items = []
    base = build_hot_keywords()
    for item in base:
        seed = abs(hash(item["keyword"])) % 10000
        random.seed(seed)
        supply = random.randint(500, 6000)
        demand = random.randint(2000, 12000)
        heat, index = demand_supply_index(demand, random.randint(1000, 4000), item["growth"], supply, ScoreWeights())
        items.append(
            {
                "keyword": item["keyword"],
                "demand": demand,
                "supply": supply,
                "index": index,
                "heat": heat,
            }
        )
    demand_list = sorted([i["demand"] for i in items])
    supply_list = sorted([i["supply"] for i in items])
    median_demand = demand_list[len(demand_list) // 2]
    median_supply = supply_list[len(supply_list) // 2]
    for item in items:
        if item["demand"] >= median_demand and item["supply"] <= median_supply:
            quadrant = "高需求低供给"
        elif item["demand"] >= median_demand and item["supply"] > median_supply:
            quadrant = "高需求高供给"
        elif item["demand"] < median_demand and item["supply"] <= median_supply:
            quadrant = "低需求低供给"
        else:
            quadrant = "低需求高供给"
        item["quadrant"] = quadrant
    return {"items": items, "median_demand": median_demand, "median_supply": median_supply}


@app.get("/api/analysis/heatmap")
def social_heatmap():
    x_labels = generate_date_series(7)
    y_labels = ["VK", "OK", "YouTube", "Ozon", "Wildberries", "Yandex.Market"]
    values = []
    random.seed(42)
    for x_index, _ in enumerate(x_labels):
        for y_index, _ in enumerate(y_labels):
            values.append([x_index, y_index, random.randint(10, 100)])
    return {"x_labels": x_labels, "y_labels": y_labels, "values": values}


@app.get("/api/keywords/cloud")
def keyword_cloud():
    words = [
        {"word": "宠物饮水", "weight": 86},
        {"word": "防臭猫砂", "weight": 74},
        {"word": "宠物旅行", "weight": 62},
        {"word": "清洁护理", "weight": 58},
        {"word": "智能喂食", "weight": 53},
        {"word": "宠物玩具", "weight": 48},
        {"word": "健康监测", "weight": 42},
        {"word": "猫抓板", "weight": 39},
    ]
    return {"items": words}


@app.get("/api/shop/category-dashboard")
def category_dashboard(range: str = Query("7d")):
    dates = generate_date_series(7 if range == "7d" else 30)
    trend = []
    base = 320
    for i, d in enumerate(dates):
        trend.append({"date": d, "sales": base + i * 12 + (i % 3) * 8})
    categories = [
        {"category": "宠物用品", "share": 0.42, "sales": 2240, "revenue": 68400, "profit": 21400, "trend": trend},
        {"category": "家居清洁", "share": 0.26, "sales": 1320, "revenue": 39600, "profit": 11200, "trend": trend},
        {"category": "智能设备", "share": 0.18, "sales": 760, "revenue": 51200, "profit": 16800, "trend": trend},
        {"category": "户外用品", "share": 0.14, "sales": 520, "revenue": 28600, "profit": 8200, "trend": trend},
    ]
    return {"range": range, "categories": categories}


@app.get("/api/shop/subcategory-ranking")
def subcategory_ranking(metric: str = Query("profit")):
    items = [
        {"category": "猫砂盆", "sales": 620, "revenue": 18600, "profit": 6200, "growth": 0.28},
        {"category": "宠物饮水机", "sales": 540, "revenue": 32400, "profit": 9800, "growth": 0.31},
        {"category": "宠物背包", "sales": 460, "revenue": 20700, "profit": 5400, "growth": 0.18},
        {"category": "宠物理毛手套", "sales": 420, "revenue": 12600, "profit": 3600, "growth": 0.22},
        {"category": "止吠器", "sales": 360, "revenue": 28800, "profit": 8200, "growth": 0.12},
    ]
    return {"metric": metric, "items": items}


@app.get("/api/shop/hot-cold")
def hot_cold():
    hot = [
        {"product": "智能喂食器", "sales_7d": 320, "growth": 0.36, "profit": 8600},
        {"product": "宠物饮水机", "sales_7d": 280, "growth": 0.29, "profit": 7200},
    ]
    cold = [
        {"product": "普通猫砂盆", "sales_30d": 38, "profit": 420},
        {"product": "塑料宠物玩具", "sales_30d": 26, "profit": 180},
    ]
    return {"hot": hot, "cold": cold}


@app.get("/api/shop/new-product-plan")
def new_product_plan():
    return {
        "recommend": [
            {"category": "宠物饮水", "quantity": 6, "priority": "高"},
            {"category": "智能喂食", "quantity": 4, "priority": "高"},
            {"category": "清洁护理", "quantity": 3, "priority": "中"},
        ],
        "avoid": [
            {"category": "低端宠物玩具", "reason": "高竞争低需求"},
            {"category": "普通猫砂盆", "reason": "利润低且销量下滑"},
        ],
    }


@app.get("/api/shop/pricing-strategy")
def pricing_strategy():
    return {
        "items": [
            {"product": "宠物饮水机", "price_index": 0.92, "competitor_range": "24-32", "suggestion": "小幅提价至28-30"},
            {"product": "智能喂食器", "price_index": 1.08, "competitor_range": "38-46", "suggestion": "降价到40附近"},
            {"product": "宠物旅行背包", "price_index": 0.98, "competitor_range": "22-28", "suggestion": "保持价格并提升赠品"},
        ]
    }


async def complete_task(task_id: str, result: Dict[str, Any]):
    for progress in [20, 40, 60, 80]:
        tasks[task_id]["progress"] = progress
        await asyncio.sleep(0.4)
    tasks[task_id]["status"] = "done"
    tasks[task_id]["progress"] = 100
    tasks[task_id]["result"] = result


@app.post("/api/ai/image")
def ai_image(payload: ImageRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "type": "image", "progress": 0}
    images = [
        f"https://picsum.photos/seed/{task_id[:8]}1/800/800",
        f"https://picsum.photos/seed/{task_id[:8]}2/800/800",
        f"https://picsum.photos/seed/{task_id[:8]}3/800/800",
    ]
    background_tasks.add_task(complete_task, task_id, {"images": images})
    return {"task_id": task_id, "status": "processing"}


@app.get("/api/ai/image/{task_id}")
def ai_image_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return {"task_id": task_id, "status": "not_found"}
    result = task.get("result")
    return {"task_id": task_id, "status": task["status"], "result": result}


@app.post("/api/ai/video")
def ai_video(payload: VideoRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "type": "video", "progress": 0}
    result = {
        "video_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "cover": f"https://picsum.photos/seed/{task_id[:8]}4/640/360",
        "duration": payload.duration,
        "format": "mp4",
    }
    background_tasks.add_task(complete_task, task_id, result)
    return {"task_id": task_id, "status": "processing"}


@app.get("/api/ai/video/{task_id}")
def ai_video_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return {"task_id": task_id, "status": "not_found"}
    result = task.get("result")
    return {"task_id": task_id, "status": task["status"], "result": result}


@app.post("/api/ai/copy")
def ai_copy(payload: CopyRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "type": "copy", "progress": 0}
    points = "、".join(payload.selling_points)
    result = {
        "seo_titles": [
            f"{payload.name} 高效实用 {payload.platform} 热搜推荐",
            f"{payload.name} 热门卖点 {points}",
        ],
        "short_desc": f"{payload.name} 解决日常需求，卖点：{points}",
        "detail_desc": f"{payload.name} 适用于{payload.platform}平台，突出{points}，适合俄罗斯用户使用场景。",
        "social_copy": f"{payload.name} 热销推荐，{points}，现在下单更优惠。",
        "language": payload.language,
    }
    background_tasks.add_task(complete_task, task_id, result)
    return {"task_id": task_id, "status": "processing"}


@app.get("/api/ai/copy/{task_id}")
def ai_copy_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return {"task_id": task_id, "status": "not_found"}
    result = task.get("result")
    return {"task_id": task_id, "status": task["status"], "result": result}


@app.websocket("/ws/ai/{task_id}")
async def ai_task_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    while True:
        task = tasks.get(task_id)
        if not task:
            await websocket.send_json({"task_id": task_id, "status": "not_found"})
            await websocket.close()
            return
        await websocket.send_json(
            {
                "task_id": task_id,
                "status": task["status"],
                "progress": task.get("progress", 0),
                "result": task.get("result"),
            }
        )
        if task["status"] == "done":
            await websocket.close()
            return
        await asyncio.sleep(0.8)


@app.get("/api/mock/seed")
def seed_mock(days: int = Query(180), seed: int = Query(42)):
    return generate_mock_dataset(days=days, seed=seed)
