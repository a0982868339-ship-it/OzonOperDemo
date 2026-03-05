"""
Mission Router — /mission endpoints

GET  /mission/history           — list missions
GET  /mission/{id}              — get mission state
POST /mission/pipeline          — start full pipeline
POST /mission/{id}/run-scout    — run Scout only
POST /mission/{id}/run-analyst  — run Analyst only
POST /mission/{id}/run-linguistic — run Linguistic only
POST /mission/{id}/run-creative — run Creative only
WS   /mission/{id}/ws           — subscribe to live logs
"""

from typing import Iterator, List
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime

from backend.core.database import SessionLocal
from backend.models.mission import Mission
from backend.schemas.mission import (
    PipelineRunRequest, SingleAgentRunRequest,
    MissionResponse, MissionCreateResponse, AgentStatusMap,
)
from backend.agents.orchestrator_agent import OrchestratorAgent
from backend.services.websocket_manager import manager as ws_manager

router = APIRouter(prefix="/mission", tags=["mission"])


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _to_response(m: Mission) -> MissionResponse:
    return MissionResponse(
        id=m.id,
        title=m.title,
        mode=m.mode,
        status=m.status,
        user_input=m.user_input,
        agent_status=AgentStatusMap(
            scout=m.scout_status,
            analyst=m.analyst_status,
            linguistic=m.linguistic_status,
            creative=m.creative_status,
        ),
        scout_result=m.scout_result,
        analyst_result=m.analyst_result,
        linguistic_result=m.linguistic_result,
        creative_result=m.creative_result,
    )


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/history", response_model=List[MissionResponse])
def list_missions(limit: int = 20, db: Session = Depends(get_db)):
    missions = db.query(Mission).order_by(Mission.created_at.desc()).limit(limit).all()
    return [_to_response(m) for m in missions]


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    m = db.query(Mission).filter(Mission.id == mission_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found")
    return _to_response(m)


# ── Pipeline启动 ───────────────────────────────────────────────────────────────

@router.post("/pipeline", response_model=MissionCreateResponse)
async def start_pipeline(
    payload: PipelineRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Parse intent and start full pipeline in background."""
    # Parse intent first (quick call)
    orchestrator = OrchestratorAgent(db)
    intent = await orchestrator.parse_intent(payload.user_input)

    cfg = payload.agent_config
    now = datetime.utcnow()
    mission = Mission(
        title=payload.title or payload.user_input[:60],
        mode="pipeline",
        user_input=payload.user_input,
        status="pending",
        use_scout=str(cfg.use_scout).lower(),
        use_analyst=str(cfg.use_analyst).lower(),
        use_linguistic=str(cfg.use_linguistic).lower(),
        use_creative=str(cfg.use_creative).lower(),
        created_at=now,
        updated_at=now,
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)

    background_tasks.add_task(OrchestratorAgent.run_pipeline, mission.id)

    return MissionCreateResponse(
        mission_id=mission.id,
        status="pending",
        message=f"Mission started. Intent: {intent.get('goal', '')}",
    )


# ── 手动单 Agent 执行 ─────────────────────────────────────────────────────────

def _get_or_create_manual(mission_id: int, db: Session) -> Mission:
    m = db.query(Mission).filter(Mission.id == mission_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found")
    return m


@router.post("/{mission_id}/run-scout", response_model=MissionCreateResponse)
async def run_scout(
    mission_id: int,
    payload: SingleAgentRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _get_or_create_manual(mission_id, db)
    background_tasks.add_task(
        OrchestratorAgent.run_single_agent, mission_id, "scout", payload.override_data
    )
    return MissionCreateResponse(mission_id=mission_id, status="running", message="Scout started")


@router.post("/{mission_id}/run-analyst", response_model=MissionCreateResponse)
async def run_analyst(
    mission_id: int,
    payload: SingleAgentRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _get_or_create_manual(mission_id, db)
    background_tasks.add_task(
        OrchestratorAgent.run_single_agent, mission_id, "analyst", payload.override_data
    )
    return MissionCreateResponse(mission_id=mission_id, status="running", message="Analyst started")


@router.post("/{mission_id}/run-linguistic", response_model=MissionCreateResponse)
async def run_linguistic(
    mission_id: int,
    payload: SingleAgentRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    m = _get_or_create_manual(mission_id, db)
    # Allow user to pass their own copy string shorthand
    if payload.override_data and payload.override_data.get("copy"):
        m.user_uploaded_copy = payload.override_data["copy"]
        db.add(m)
        db.commit()
    background_tasks.add_task(
        OrchestratorAgent.run_single_agent, mission_id, "linguistic", payload.override_data
    )
    return MissionCreateResponse(mission_id=mission_id, status="running", message="Linguistic started")


@router.post("/{mission_id}/run-creative", response_model=MissionCreateResponse)
async def run_creative(
    mission_id: int,
    payload: SingleAgentRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _get_or_create_manual(mission_id, db)
    background_tasks.add_task(
        OrchestratorAgent.run_single_agent, mission_id, "creative", payload.override_data
    )
    return MissionCreateResponse(mission_id=mission_id, status="running", message="Creative started")


# ── 手动创建空 Mission（供手动模式前端创建一个 mission_id）────────────────────────

@router.post("/manual", response_model=MissionCreateResponse)
def create_manual_mission(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    mission = Mission(mode="manual", status="pending", created_at=now, updated_at=now)
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return MissionCreateResponse(
        mission_id=mission.id, status="pending", message="Manual mission created"
    )


# ── WebSocket per-mission ─────────────────────────────────────────────────────

@router.websocket("/{mission_id}/ws")
async def mission_ws(mission_id: int, websocket: WebSocket):
    await ws_manager.connect_mission(mission_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        ws_manager.disconnect_mission(mission_id, websocket)
