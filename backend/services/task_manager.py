import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Coroutine
from sqlalchemy.orm import Session

from backend.agents.linguistic_agent import LinguisticAgent
from backend.agents.creative_agent import CreativeAgent
from backend.models.ai_asset import AIAsset
from backend.services.providers import generate_media_flux
from backend.core.database import SessionLocal
from backend.services.websocket_manager import manager as ws_manager


class TaskStatus:
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskManager:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.linguistic_agent = LinguisticAgent()
        self.creative_agent = CreativeAgent()

    def create_task(self, task_id: str, asset_type: str) -> AIAsset:
        now = datetime.utcnow()
        asset = AIAsset(
            task_id=task_id,
            asset_type=asset_type,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def update_task(self, asset: AIAsset, status: str, payload: Optional[Dict[str, Any]] = None) -> AIAsset:
        asset.status = status
        asset.updated_at = datetime.utcnow()
        if payload:
            asset.title_seo = payload.get("title_seo") or asset.title_seo
            asset.short_description = payload.get("short_description") or asset.short_description
            asset.bullet_points_ru = payload.get("bullet_points_ru") or asset.bullet_points_ru
            asset.tags = payload.get("tags") or asset.tags
            asset.urls = payload.get("urls") or asset.urls
            asset.prompt_text = payload.get("prompt_text") or asset.prompt_text
            asset.error_message = payload.get("error_message") or asset.error_message
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    @staticmethod
    async def run_seo(task_id: str, payload: Dict[str, Any]) -> None:
        with SessionLocal() as session:
            manager = TaskManager(session)
            asset = session.query(AIAsset).filter_by(task_id=task_id).first()
            if not asset:
                return
            manager.update_task(asset, TaskStatus.GENERATING)
            await ws_manager.broadcast({
                "type": "log",
                "task_id": task_id,
                "agent": "Linguistic",
                "message": f"Starting SEO optimization for {payload.get('product_name')}..."
            })
            try:
                await ws_manager.broadcast({
                    "type": "log",
                    "task_id": task_id,
                    "agent": "Linguistic",
                    "message": "Analyzing top keywords and competitor listings..."
                })
                result = await manager.linguistic_agent.run(payload, db=session)
                manager.update_task(asset, TaskStatus.COMPLETED, result)
                await ws_manager.broadcast({
                    "type": "completion",
                    "task_id": task_id,
                    "agent": "Linguistic",
                    "status": "success",
                    "result": result
                })
            except Exception as exc:
                manager.update_task(asset, TaskStatus.FAILED, {"error_message": str(exc)})
                await ws_manager.broadcast({
                    "type": "error",
                    "task_id": task_id,
                    "agent": "Linguistic",
                    "message": str(exc)
                })

    @staticmethod
    async def run_media(task_id: str, payload: Dict[str, Any]) -> None:
        with SessionLocal() as session:
            manager = TaskManager(session)
            asset = session.query(AIAsset).filter_by(task_id=task_id).first()
            if not asset:
                return
            manager.update_task(asset, TaskStatus.GENERATING)
            await ws_manager.broadcast({
                "type": "log",
                "task_id": task_id,
                "agent": "Creative",
                "message": f"Starting media generation for {payload.get('product_name')}..."
            })
            try:
                prompts = await manager.creative_agent.run(payload, db=session)
                await ws_manager.broadcast({
                    "type": "log",
                    "task_id": task_id,
                    "agent": "Creative",
                    "message": f"Generated prompt: {prompts.get('image_prompt')}"
                })
                await ws_manager.broadcast({
                    "type": "log",
                    "task_id": task_id,
                    "agent": "Creative",
                    "message": "Rendering image with Flux model..."
                })
                urls = await generate_media_flux(prompts["image_prompt"])
                result = {
                    "prompt_text": prompts["image_prompt"],
                    "urls": urls,
                }
                manager.update_task(asset, TaskStatus.COMPLETED, result)
                await ws_manager.broadcast({
                    "type": "completion",
                    "task_id": task_id,
                    "agent": "Creative",
                    "status": "success",
                    "result": result
                })
            except Exception as exc:
                manager.update_task(asset, TaskStatus.FAILED, {"error_message": str(exc)})
                await ws_manager.broadcast({
                    "type": "error",
                    "task_id": task_id,
                    "agent": "Creative",
                    "message": str(exc)
                })

    def schedule(self, coro: Coroutine[Any, Any, None]) -> None:
        asyncio.create_task(coro)
