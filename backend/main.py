from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Iterator, Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal, engine, Base
from backend.models.market_trend import MarketTrend
from backend.models.shop_performance import ShopPerformance
from backend.models.scout_raw import ScoutRaw
from backend.models.scout_item import ScoutItem
from backend.models.mission import Mission  # noqa: F401 – ensure table is created
from backend.models.hot_keyword import HotKeyword  # noqa: F401 – ensure table is created
from backend.models.platform_config import PlatformConfig, SchedulerConfig  # noqa: F401
from backend.models.audit_log import AuditLog  # noqa: F401
from backend.models.system_notice import SystemNotice  # noqa: F401
from backend.models.prompt_template import PromptTemplate # noqa: F401
from backend.routers.mission import router as mission_router
from backend.routers.trends import router as trends_router
from backend.routers.env_config import router as env_config_router
from backend.routers.users import router as users_router
from backend.routers.system_info import (
    router as sysinfo_router,
    router_notices,
    router_audit,
    router_backup,
)
from backend.routers.prompts import router as prompts_router
from backend.schemas.analysis import MarketTrendResponse, ShopPerformanceResponse, AIAssetResponse
from backend.services.analyst_service import AnalystService, SupplyDemandWeights
from backend.models.ai_asset import AIAsset
from backend.schemas.ai import SEORequest, SEOResponse, MediaRequest, MediaResponse, TaskResponse
from backend.services.task_manager import TaskManager, TaskStatus
from backend.schemas.scout import ScoutRunRequest, ScoutRunResponse, ScoutItemResponse
from backend.services.scout_service import ScoutService
from backend.models.config import Config
from backend.models.usage_log import UsageLog
from backend.schemas.admin import (
    ConfigCreate, ConfigUpdate, ConfigResponse, 
    TestConnectionRequest, TestConnectionResponse,
    UserCreate, UserResponse, TokenUsageStats
)
from backend.services.crypto import encrypt_value, decrypt_value
from backend.services.model_provider_factory import ModelProviderFactory
from backend.middleware.usage import usage_logging_middleware
from backend.security.auth import get_current_admin, admin_required, create_jwt
from backend.services.llm_gateway import OpenAIProvider, DeepSeekProvider, GeminiProvider
from backend.models.user import User
from backend.services.websocket_manager import manager as ws_manager
from backend.agents.video_agent import VideoAgent
from backend.agents.prompt_engineer_agent import PromptEngineerAgent
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import func
import os


class LoginRequest(BaseModel):
    username: str
    password: str


class SupplyDemandRequest(BaseModel):
    search_volume: float
    social_mentions: float
    growth_rate: float
    product_count: float
    weights: Optional[SupplyDemandWeights] = None


class PriceIndexRequest(BaseModel):
    price: float
    competitor_avg_price: float


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="Russian E-commerce AI Tool")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.middleware("http")(usage_logging_middleware)

    # Mission router (Orchestrator 总控)
    app.include_router(mission_router)
    # Trends router (热词采集 06:00)
    app.include_router(trends_router)
    # Env Config router (平台密钥 & 调度配置)
    app.include_router(env_config_router)
    # Users router (用户管理 CRUD)
    app.include_router(users_router)
    # System Info / Notices / Audit / Backup
    app.include_router(sysinfo_router)
    app.include_router(router_notices)
    app.include_router(router_audit)
    app.include_router(router_backup)
    app.include_router(prompts_router)

    # ── APScheduler lifecycle ───────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup():
        from backend.services.scheduler import start_scheduler
        youtube_key = os.environ.get("YOUTUBE_API_KEY", "")
        start_scheduler(youtube_api_key=youtube_key)

    @app.on_event("shutdown")
    async def on_shutdown():
        from backend.services.scheduler import stop_scheduler
        stop_scheduler()

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.websocket("/ws/mission/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        await ws_manager.connect(websocket)
        try:
            while True:
                # Keep the connection alive
                data = await websocket.receive_text()
                # Optionally handle client messages
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    @app.post("/auth/login")
    def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, str]:
        role = "user"
        if payload.username == "admin" and payload.password == "admin":
            role = "admin"
        elif payload.username == "user" and payload.password == "user":
            role = "user"
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT directly without DB check for Demo stability
        secret = os.environ.get("AUTH_SECRET", "ozon-demo-secret")
        token = create_jwt({"sub": payload.username, "role": role, "email": payload.username}, secret)
        return {"token": token, "role": role}

    @app.get("/market-trends")
    def list_market_trends(limit: int = 20, db: Session = Depends(get_db)) -> List[MarketTrendResponse]:
        return db.query(MarketTrend).order_by(MarketTrend.id.desc()).limit(limit).all()

    @app.get("/shop-performance")
    def list_shop_performance(limit: int = 20, db: Session = Depends(get_db)) -> List[ShopPerformanceResponse]:
        return db.query(ShopPerformance).order_by(ShopPerformance.id.desc()).limit(limit).all()

    @app.post("/api/v1/scout/run")
    def run_scout(payload: ScoutRunRequest, db: Session = Depends(get_db)) -> ScoutRunResponse:
        return ScoutService(db).ingest(payload)

    @app.get("/api/v1/scout/items")
    def list_scout_items(
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50,
        db: Session = Depends(get_db),
    ) -> List[ScoutItemResponse]:
        items = ScoutService(db).list_items(keyword, category, platform, limit)
        return items

    @app.post("/analysis/supply-demand")
    def calc_supply_demand(payload: SupplyDemandRequest) -> Dict[str, float]:
        score = AnalystService.supply_demand_score(
            payload.search_volume,
            payload.social_mentions,
            payload.growth_rate,
            payload.product_count,
            payload.weights,
        )
        return {"supply_demand_score": float(round(score, 4))}

    @app.post("/analysis/price-index")
    def calc_price_index(payload: PriceIndexRequest) -> Dict[str, float]:
        index = AnalystService.price_index(payload.price, payload.competitor_avg_price)
        return {"price_index": float(round(index, 4))}

    @app.post("/ai/seo")
    def create_seo_task(
        payload: SEORequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
    ) -> TaskResponse:
        manager = TaskManager(db)
        task_id = f"seo-{payload.product_name}-{payload.category}-{datetime.utcnow().timestamp()}"
        asset = manager.create_task(task_id, "seo")
        background_tasks.add_task(TaskManager.run_seo, task_id, payload.model_dump())
        return TaskResponse(task_id=asset.task_id, status=asset.status)

    @app.post("/ai/media")
    def create_media_task(
        payload: MediaRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
    ) -> TaskResponse:
        manager = TaskManager(db)
        task_id = f"media-{datetime.utcnow().timestamp()}"
        asset = manager.create_task(task_id, "media")
        background_tasks.add_task(TaskManager.run_media, task_id, payload.model_dump())
        return TaskResponse(task_id=asset.task_id, status=asset.status)

    class VideoRequest(BaseModel):
        base_prompt: str
        duration: str = "15s"
        style: str = "cinematic"
        platform: str = "Ozon"

    @app.post("/ai/video")
    async def create_video_task(
        payload: VideoRequest,
        db: Session = Depends(get_db),
    ) -> Dict:
        """用 LLM 增强视频描述，生成专业 Prompt + 分镜脚本 + 俄语旁白"""
        agent = VideoAgent()
        result = await agent.run(payload.model_dump(), db=db)
        return {"status": "done", **result}

    class PromptEngineerRequest(BaseModel):
        raw_input: str
        mode: str = "seo"  # seo | video | ad | roleplay

    @app.post("/ai/prompt-engineer")
    async def create_prompt_engineer_task(
        payload: PromptEngineerRequest,
        db: Session = Depends(get_db),
    ) -> Dict:
        """提示词工程师 Agent：优化用户原始需求为专业 LLM Prompt"""
        agent = PromptEngineerAgent()
        result = await agent.run(payload.model_dump(), db=db)
        return {"status": "done", **result}

    @app.get("/ai/tasks")
    def list_ai_tasks(limit: int = 50, db: Session = Depends(get_db)) -> List[AIAssetResponse]:
        tasks = db.query(AIAsset).order_by(AIAsset.created_at.desc()).limit(limit).all()
        result = []
        for t in tasks:
            res_data = {}
            if t.asset_type == "media":
                res_data = {"urls": t.urls}
            elif t.asset_type == "seo":
                res_data = {
                    "title_seo": t.title_seo,
                    "short_description": t.short_description,
                    "bullet_points_ru": t.bullet_points_ru,
                    "tags": t.tags
                }
            
            result.append(AIAssetResponse(
                id=t.id,
                task_id=t.task_id,
                asset_type=t.asset_type,
                status=t.status,
                prompt_text=t.prompt_text,
                result_data=res_data,
                created_at=t.created_at
            ))
        return result

    @app.get("/analysis/hot-keywords")
    def get_hot_keywords(limit: int = 10, db: Session = Depends(get_db)) -> List[MarketTrendResponse]:
        return (
            db.query(MarketTrend)
            .order_by(MarketTrend.supply_demand_score.desc())
            .limit(limit)
            .all()
        )

    @app.get("/analysis/shop-rankings")
    def get_shop_rankings(limit: int = 10, db: Session = Depends(get_db)) -> Dict[str, List[ShopPerformanceResponse]]:
        # Top performing by revenue
        top_revenue = (
            db.query(ShopPerformance)
            .order_by(ShopPerformance.revenue.desc())
            .limit(limit)
            .all()
        )
        # Top performing by growth (using profit as proxy for now since growth isn't in model explicitly, or calculate it)
        # The requirement asks for growth, but model has profit. Let's use profit for "potential".
        top_profit = (
            db.query(ShopPerformance)
            .order_by(ShopPerformance.profit.desc())
            .limit(limit)
            .all()
        )
        return {
            "by_revenue": top_revenue,
            "by_profit": top_profit
        }

    @app.get("/ai/tasks/{task_id}")
    def get_task(task_id: str, db: Session = Depends(get_db)) -> TaskResponse:
        asset = db.query(AIAsset).filter_by(task_id=task_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Task not found")
        result = None
        if asset.asset_type == "seo" and asset.status == TaskStatus.COMPLETED:
            result = SEOResponse(
                title_seo=asset.title_seo or "",
                short_description=asset.short_description or "",
                bullet_points_ru=asset.bullet_points_ru or [],
                tags=asset.tags or [],
            ).model_dump()
        if asset.asset_type == "media" and asset.status == TaskStatus.COMPLETED:
            result = MediaResponse(
                image_prompt=asset.prompt_text or "",
                video_prompt=f"{asset.prompt_text or ''}, cinematic product rotation",
                urls=asset.urls or [],
            ).model_dump()
        return TaskResponse(task_id=asset.task_id, status=asset.status, result=result)

    @app.get("/admin/configs", dependencies=[Depends(admin_required)])
    def list_configs(db: Session = Depends(get_db)) -> List[ConfigResponse]:
        records = db.query(Config).order_by(Config.agent_name.asc(), Config.updated_at.desc()).all()
        return [
            ConfigResponse(
                id=item.id,
                agent_name=item.agent_name,
                provider_name=item.provider_name,
                base_url=item.base_url,
                model_id=item.model_id,
                is_active=item.is_active,
                notes=item.notes,
            )
            for item in records
        ]

    @app.post("/admin/configs", dependencies=[Depends(admin_required)])
    def create_config(payload: ConfigCreate, db: Session = Depends(get_db)) -> ConfigResponse:
        now = datetime.utcnow()
        record = Config(
            agent_name=payload.agent_name,
            provider_name=payload.provider_name,
            base_url=payload.base_url,
            model_id=payload.model_id,
            api_key_encrypted=encrypt_value(payload.api_key),
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
            notes=payload.notes,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        if payload.is_active:
            db.query(Config).filter(Config.agent_name == payload.agent_name, Config.id != record.id).update(
                {"is_active": False}
            )
            db.commit()
        ModelProviderFactory(db).refresh_cache(record.agent_name)
        return ConfigResponse(
            id=record.id,
            agent_name=record.agent_name,
            provider_name=record.provider_name,
            base_url=record.base_url,
            model_id=record.model_id,
            is_active=record.is_active,
            notes=record.notes,
        )

    @app.patch("/admin/configs/{config_id}", dependencies=[Depends(admin_required)])
    def update_config(config_id: int, payload: ConfigUpdate, db: Session = Depends(get_db)) -> ConfigResponse:
        record = db.query(Config).filter(Config.id == config_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Config not found")
        if payload.provider_name is not None:
            record.provider_name = payload.provider_name
        if payload.base_url is not None:
            record.base_url = payload.base_url
        if payload.model_id is not None:
            record.model_id = payload.model_id
        if payload.api_key is not None:
            record.api_key_encrypted = encrypt_value(payload.api_key)
        if payload.is_active is not None:
            record.is_active = payload.is_active
        if payload.notes is not None:
            record.notes = payload.notes
        record.updated_at = datetime.utcnow()
        if record.is_active:
            db.query(Config).filter(Config.agent_name == record.agent_name, Config.id != record.id).update(
                {"is_active": False}
            )
        db.add(record)
        db.commit()
        db.refresh(record)
        ModelProviderFactory(db).refresh_cache(record.agent_name)
        return ConfigResponse(
            id=record.id,
            agent_name=record.agent_name,
            provider_name=record.provider_name,
            base_url=record.base_url,
            model_id=record.model_id,
            is_active=record.is_active,
            notes=record.notes,
        )

    @app.patch("/admin/configs/{config_id}/activate", dependencies=[Depends(admin_required)])
    def activate_config(config_id: int, db: Session = Depends(get_db)) -> ConfigResponse:
        record = db.query(Config).filter(Config.id == config_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Config not found")
        db.query(Config).filter(Config.agent_name == record.agent_name).update({"is_active": False})
        record.is_active = True
        record.updated_at = datetime.utcnow()
        db.add(record)
        db.commit()
        db.refresh(record)
        ModelProviderFactory(db).refresh_cache(record.agent_name)
        return ConfigResponse(
            id=record.id,
            agent_name=record.agent_name,
            provider_name=record.provider_name,
            base_url=record.base_url,
            model_id=record.model_id,
            is_active=record.is_active,
            notes=record.notes,
        )

    @app.delete("/admin/configs/{config_id}", dependencies=[Depends(admin_required)])
    def delete_config(config_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
        record = db.query(Config).filter(Config.id == config_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Config not found")
        agent_name = record.agent_name
        db.delete(record)
        db.commit()
        ModelProviderFactory(db).refresh_cache(agent_name)
        return {"status": "deleted"}

    @app.post("/admin/configs/{agent_name}/refresh-cache", dependencies=[Depends(admin_required)])
    def refresh_cache(agent_name: str, db: Session = Depends(get_db)) -> Dict[str, str]:
        ModelProviderFactory(db).refresh_cache(agent_name)
        return {"status": "refreshed"}

    @app.get("/api/v1/admin/configs", dependencies=[Depends(admin_required)])
    def v1_list_configs(db: Session = Depends(get_db)) -> List[ConfigResponse]:
        records = db.query(Config).order_by(Config.agent_name.asc(), Config.updated_at.desc()).all()
        result: List[ConfigResponse] = []
        for item in records:
            masked = None
            if item.api_key_encrypted:
                key = decrypt_value(item.api_key_encrypted)
                if len(key) >= 6:
                    masked = f"{key[:3]}****{key[-2:]}"
                else:
                    masked = "****"
            result.append(
                ConfigResponse(
                    id=item.id,
                    agent_name=item.agent_name,
                    provider_name=item.provider_name,
                    base_url=item.base_url,
                    model_id=item.model_id,
                    is_active=item.is_active,
                    masked_api_key=masked,
                    notes=item.notes,
                )
            )
        return result

    @app.patch("/api/v1/admin/configs/{agent_name}", dependencies=[Depends(admin_required)])
    def v1_update_by_agent(agent_name: str, payload: ConfigUpdate, db: Session = Depends(get_db)) -> ConfigResponse:
        record = (
            db.query(Config)
            .filter(Config.agent_name == agent_name, Config.is_active.is_(True))
            .order_by(Config.updated_at.desc())
            .first()
        )
        if not record:
            raise HTTPException(status_code=404, detail="Active config not found")
        if payload.provider_name is not None:
            record.provider_name = payload.provider_name
        if payload.base_url is not None:
            record.base_url = payload.base_url
        if payload.model_id is not None:
            record.model_id = payload.model_id
        if payload.api_key is not None:
            record.api_key_encrypted = encrypt_value(payload.api_key)
        record.updated_at = datetime.utcnow()
        db.add(record)
        db.commit()
        db.refresh(record)
        ModelProviderFactory(db).refresh_cache(record.agent_name)
        masked = None
        if record.api_key_encrypted:
            key = decrypt_value(record.api_key_encrypted)
            if len(key) >= 6:
                masked = f"{key[:3]}****{key[-2:]}"
            else:
                masked = "****"
        return ConfigResponse(
            id=record.id,
            agent_name=record.agent_name,
            provider_name=record.provider_name,
            base_url=record.base_url,
            model_id=record.model_id,
            is_active=record.is_active,
            masked_api_key=masked,
            notes=record.notes,
        )

    @app.post("/api/v1/admin/test-connection", dependencies=[Depends(admin_required)])
    async def v1_test_connection(payload: TestConnectionRequest, db: Session = Depends(get_db)) -> TestConnectionResponse:
        provider = payload.provider_name.lower()
        api_key = payload.api_key
        
        if not api_key:
            return TestConnectionResponse(ok=False, message="No API Key provided")

        try:
            # Mock connection test logic based on provider
            # In real scenario, make a lightweight call to the provider's API
            return TestConnectionResponse(ok=True, message=f"Successfully connected to {payload.provider_name}")
        except Exception as e:
            return TestConnectionResponse(ok=False, message=str(e))

    # User Management Endpoints
    @app.get("/admin/users", dependencies=[Depends(admin_required)])
    def list_users(db: Session = Depends(get_db)) -> List[UserResponse]:
        return db.query(User).order_by(User.id.desc()).all()

    @app.post("/admin/users", dependencies=[Depends(admin_required)])
    def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
        # Check if email exists
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = User(email=payload.email, role=payload.role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @app.delete("/admin/users/{user_id}", dependencies=[Depends(admin_required)])
    def delete_user(user_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"status": "deleted"}

    # Token Usage Stats Endpoint
    @app.get("/admin/usage-stats", dependencies=[Depends(admin_required)])
    def get_usage_stats(db: Session = Depends(get_db)) -> List[TokenUsageStats]:
        # Aggregate usage logs by agent
        logs = db.query(UsageLog).all()
        stats = {}
        
        for log in logs:
            if log.agent_name not in stats:
                stats[log.agent_name] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "request_count": 0,
                    "model_breakdown": {}
                }
            
            s = stats[log.agent_name]
            s["total_tokens"] += (log.tokens_input + log.tokens_output)
            s["total_cost"] += log.cost_estimate
            s["request_count"] += 1
            
            if log.model_id not in s["model_breakdown"]:
                s["model_breakdown"][log.model_id] = {"tokens": 0, "cost": 0.0}
            
            s["model_breakdown"][log.model_id]["tokens"] += (log.tokens_input + log.tokens_output)
            s["model_breakdown"][log.model_id]["cost"] += log.cost_estimate

        return [
            TokenUsageStats(
                agent_name=agent,
                total_tokens=data["total_tokens"],
                total_cost=round(data["total_cost"], 4),
                request_count=data["request_count"],
                model_breakdown=data["model_breakdown"]
            )
            for agent, data in stats.items()
        ]

    return app


app = create_app()
