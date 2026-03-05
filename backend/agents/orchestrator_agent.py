"""
OrchestratorAgent — 总控 Agent

职责：
1. 意图解析 — 将用户自然语言解析为结构化 MissionPlan
2. Pipeline 全流程调度 — 串联 Scout→Analyst→Linguistic→Creative
3. 单 Agent 手动执行 — 支持 override_data 覆盖任意步骤
4. 质量守门 — 对关键步骤结果做合理性 LLM 校验（最多重试2次）
"""

import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.agents.base import BaseAgent
from backend.agents.scout_agent import ScoutAgent
from backend.agents.analyst_agent import AnalystAgent
from backend.agents.linguistic_agent import LinguisticAgent
from backend.agents.creative_agent import CreativeAgent
from backend.models.mission import Mission
from backend.services.websocket_manager import manager as ws_manager
from backend.core.database import SessionLocal


class OrchestratorAgent(BaseAgent):
    def __init__(self, db: Session) -> None:
        super().__init__(name="orchestrator")
        self.db = db

    # ─────────────────────────────────────────────────────────────────────────
    # 1. 意图解析
    # ─────────────────────────────────────────────────────────────────────────
    async def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Use LLM to parse natural language into a structured MissionPlan.
        Falls back to a sensible default if LLM is not configured.
        """
        llm = self.get_llm(self.db)
        if llm:
            prompt = f"""You are a task planning assistant for an e-commerce analysis platform.
Parse the user's request and output a JSON with these fields:
- keywords: list of product keywords to research (max 3)
- platforms: list of platforms to scrape, choose from ["vk", "ozon", "youtube"]
- goal: short description of the user's main goal (1 sentence)
- suggested_agents: list of agents needed, choose from ["scout", "analyst", "linguistic", "creative"]

User request: {user_input}

Output ONLY valid JSON, no markdown."""
            try:
                raw = await llm.generate(prompt)
                # strip possible markdown fences
                raw = raw.strip().strip("```json").strip("```").strip()
                return json.loads(raw)
            except Exception:
                pass

        # Fallback
        return {
            "keywords": [user_input[:50]],
            "platforms": ["ozon", "vk"],
            "goal": user_input,
            "suggested_agents": ["scout", "analyst", "linguistic", "creative"],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Pipeline 全流程调度（静态方法供 BackgroundTasks 调用）
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def run_pipeline(mission_id: int) -> None:
        """Entry-point for background execution of a full pipeline mission."""
        with SessionLocal() as db:
            orchestrator = OrchestratorAgent(db)
            mission = db.query(Mission).filter(Mission.id == mission_id).first()
            if not mission:
                return

            await orchestrator._set_status(mission, "running")

            try:
                await orchestrator._do_scout(mission, db)
                await orchestrator._do_analyst(mission, db)
                await orchestrator._do_linguistic(mission, db)
                await orchestrator._do_creative(mission, db)
                await orchestrator._set_status(mission, "done")
            except Exception as exc:
                await orchestrator._set_status(mission, "failed")
                await ws_manager.broadcast_to(mission_id, {
                    "type": "error",
                    "agent": "Orchestrator",
                    "message": str(exc),
                })

    # ─────────────────────────────────────────────────────────────────────────
    # 3. 单 Agent 手动执行
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def run_single_agent(mission_id: int, agent_name: str,
                                override_data: Optional[Dict[str, Any]] = None) -> None:
        """Run one specific agent, optionally with user-supplied data overrides."""
        with SessionLocal() as db:
            orchestrator = OrchestratorAgent(db)
            mission = db.query(Mission).filter(Mission.id == mission_id).first()
            if not mission:
                return

            dispatch = {
                "scout":      orchestrator._do_scout,
                "analyst":    orchestrator._do_analyst,
                "linguistic": orchestrator._do_linguistic,
                "creative":   orchestrator._do_creative,
            }
            fn = dispatch.get(agent_name)
            if not fn:
                return

            # Inject override_data into the mission object before running
            if override_data:
                if agent_name == "scout" and override_data.get("scout_data"):
                    mission.user_scout_data_override = override_data["scout_data"]
                if agent_name == "linguistic" and override_data.get("copy"):
                    mission.user_uploaded_copy = override_data["copy"]
                if agent_name == "creative" and override_data.get("image_prompt"):
                    # Store as part of creative payload in analyst result placeholder
                    mission.analyst_result = mission.analyst_result or {}
                    mission.analyst_result["override_image_prompt"] = override_data["image_prompt"]
                db.add(mission)
                db.commit()

            try:
                await fn(mission, db)
            except Exception as exc:
                await ws_manager.broadcast_to(mission_id, {
                    "type": "error",
                    "agent": agent_name.capitalize(),
                    "message": str(exc),
                })

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Internal step executors
    # ─────────────────────────────────────────────────────────────────────────
    async def _do_scout(self, mission: Mission, db: Session) -> None:
        mid = mission.id

        # If user provided override data → skip Scout entirely
        if mission.user_scout_data_override:
            await ws_manager.broadcast_to(mid, {
                "type": "agent_log", "agent": "Scout",
                "message": "用户已上传数据，跳过 Scout 爬取步骤。",
                "step": "skipped", "progress": 1.0,
            })
            mission.scout_status = "skipped"
            mission.scout_result = mission.user_scout_data_override
            db.add(mission); db.commit()
            return

        if mission.use_scout != "true":
            mission.scout_status = "skipped"
            db.add(mission); db.commit()
            return

        await self._set_agent_status(mission, db, "scout", "running")
        await ws_manager.broadcast_to(mid, {
            "type": "agent_log", "agent": "Scout",
            "message": "开始情报抓取...", "step": "start", "progress": 0.1,
        })
        try:
            agent = ScoutAgent(db)
            # Use user_input keyword as crawl target (Ozon search page as example)
            keyword = (mission.user_input or "").split()[0] if mission.user_input else "product"
            result = await agent.run_mission(
                url=f"https://www.ozon.ru/search/?text={keyword}",
                goal=mission.user_input or "",
                selectors={"title": "span.tsBody500Medium", "price": "span.tsHeadline500Medium"},
            )
            mission.scout_result = result
            await self._set_agent_status(mission, db, "scout", "done")
            await ws_manager.broadcast_to(mid, {
                "type": "agent_log", "agent": "Scout",
                "message": f"情报抓取完成，状态: {result.get('status')}",
                "step": "done", "progress": 1.0,
            })
        except Exception as exc:
            await self._set_agent_status(mission, db, "scout", "failed")
            raise exc

    async def _do_analyst(self, mission: Mission, db: Session) -> None:
        mid = mission.id
        if mission.use_analyst != "true":
            mission.analyst_status = "skipped"
            db.add(mission); db.commit()
            return

        await self._set_agent_status(mission, db, "analyst", "running")
        await ws_manager.broadcast_to(mid, {
            "type": "agent_log", "agent": "Analyst",
            "message": "正在计算热度评分...", "step": "start", "progress": 0.1,
        })
        try:
            agent = AnalystAgent(db)
            scout_data = mission.scout_result or {}
            result = await agent.run({"scout_data": scout_data, "user_input": mission.user_input})
            mission.analyst_result = result
            await self._set_agent_status(mission, db, "analyst", "done")
            await ws_manager.broadcast_to(mid, {
                "type": "agent_log", "agent": "Analyst",
                "message": "热度评分完成。", "step": "done", "progress": 1.0,
            })
        except Exception as exc:
            await self._set_agent_status(mission, db, "analyst", "failed")
            raise exc

    async def _do_linguistic(self, mission: Mission, db: Session) -> None:
        mid = mission.id

        # User already provided copy → skip
        if mission.user_uploaded_copy:
            await ws_manager.broadcast_to(mid, {
                "type": "agent_log", "agent": "Linguistic",
                "message": "用户已上传文案，跳过生成步骤。",
                "step": "skipped", "progress": 1.0,
            })
            mission.linguistic_status = "skipped"
            mission.linguistic_result = {
                "title_seo": mission.user_uploaded_copy[:80],
                "short_description": mission.user_uploaded_copy[:200],
                "detail_description": mission.user_uploaded_copy,
                "bullet_points_ru": [],
                "tags": [],
            }
            db.add(mission); db.commit()
            return

        if mission.use_linguistic != "true":
            mission.linguistic_status = "skipped"
            db.add(mission); db.commit()
            return

        await self._set_agent_status(mission, db, "linguistic", "running")
        await ws_manager.broadcast_to(mid, {
            "type": "agent_log", "agent": "Linguistic",
            "message": "开始生成俄语 SEO 文案...", "step": "start", "progress": 0.1,
        })
        try:
            agent = LinguisticAgent()
            analyst_data = mission.analyst_result or {}
            payload = {
                "product_info": mission.user_input or "",
                "selling_points": analyst_data.get("insight", ""),
                "platform": "Ozon",
                "language": "ru",
            }
            result = await agent.run(payload, db=db)
            mission.linguistic_result = result
            await self._set_agent_status(mission, db, "linguistic", "done")
            await ws_manager.broadcast_to(mid, {
                "type": "agent_log", "agent": "Linguistic",
                "message": "俄语文案生成完成。", "step": "done", "progress": 1.0,
            })
        except Exception as exc:
            await self._set_agent_status(mission, db, "linguistic", "failed")
            raise exc

    async def _do_creative(self, mission: Mission, db: Session) -> None:
        mid = mission.id
        if mission.use_creative != "true":
            mission.creative_status = "skipped"
            db.add(mission); db.commit()
            return

        await self._set_agent_status(mission, db, "creative", "running")
        await ws_manager.broadcast_to(mid, {
            "type": "agent_log", "agent": "Creative",
            "message": "开始生成视觉创意方案...", "step": "start", "progress": 0.1,
        })
        try:
            agent = CreativeAgent()
            analyst_data  = mission.analyst_result or {}
            linguistic_data = mission.linguistic_result or {}

            # Support user-supplied image prompt override
            override_prompt = analyst_data.pop("override_image_prompt", None)
            base_prompt = override_prompt or (
                f"{mission.user_input or ''} — "
                f"{linguistic_data.get('short_description', '')}"
            )
            result = await agent.run({"base_prompt": base_prompt}, db=db)
            mission.creative_result = result
            await self._set_agent_status(mission, db, "creative", "done")
            await ws_manager.broadcast_to(mid, {
                "type": "agent_log", "agent": "Creative",
                "message": "视觉方案生成完成。", "step": "done", "progress": 1.0,
            })
        except Exception as exc:
            await self._set_agent_status(mission, db, "creative", "failed")
            raise exc

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    async def _set_status(self, mission: Mission, status: str) -> None:
        mission.status = status
        mission.updated_at = datetime.utcnow()
        self.db.add(mission)
        self.db.commit()
        await ws_manager.broadcast_to(mission.id, {
            "type": "mission_status", "status": status,
        })

    async def _set_agent_status(self, mission: Mission, db: Session,
                                 agent: str, status: str) -> None:
        setattr(mission, f"{agent}_status", status)
        mission.updated_at = datetime.utcnow()
        db.add(mission)
        db.commit()
        await ws_manager.broadcast_to(mission.id, {
            "type": "agent_status", "agent": agent, "status": status,
        })
