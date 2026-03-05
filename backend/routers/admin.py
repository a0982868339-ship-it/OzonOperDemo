from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.config import Config, PlatformWeight
from backend.schemas.admin import (
    AgentConfigUpdate, AgentConfigResponse, 
    PlatformWeightUpdate, PlatformWeightResponse,
    ScoreCalculationRequest, ScoreCalculationResponse
)
from backend.services.crypto import encrypt_api_key

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Agent Configs ---

@router.get("/agents", response_model=List[AgentConfigResponse])
def get_agents(db: Session = Depends(get_db)):
    agents = db.query(Config).all()
    # Ensure default agents exist if DB is empty
    if not agents:
        default_agents = ["Scout", "Analyst", "Linguist", "Creative", "Orchestrator"]
        for name in default_agents:
            new_agent = Config(
                agent_name=name,
                provider_name="OpenAI",
                model_id="gpt-4",
                api_key_encrypted="mock_encrypted_key",
                temperature=0.7,
                system_prompt="You are an expert agent."
            )
            db.add(new_agent)
        db.commit()
        agents = db.query(Config).all()
    return agents

@router.put("/agents/{agent_name}", response_model=AgentConfigResponse)
def update_agent(agent_name: str, config: AgentConfigUpdate, db: Session = Depends(get_db)):
    agent = db.query(Config).filter(Config.agent_name == agent_name).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.provider_name = config.provider_name
    agent.model_id = config.model_id
    agent.temperature = config.temperature
    agent.system_prompt = config.system_prompt
    
    if config.api_key:
        agent.api_key_encrypted = encrypt_api_key(config.api_key)
        
    db.commit()
    db.refresh(agent)
    return agent

@router.post("/agents/sync-provider")
def sync_provider_to_all(
    provider_name: str, 
    api_key: str, 
    db: Session = Depends(get_db)
):
    agents = db.query(Config).all()
    encrypted_key = encrypt_api_key(api_key)
    for agent in agents:
        agent.provider_name = provider_name
        agent.api_key_encrypted = encrypted_key
    db.commit()
    return {"status": "success", "message": f"Synced {provider_name} to all agents"}

# --- Platform Weights ---

@router.get("/weights", response_model=List[PlatformWeightResponse])
def get_weights(db: Session = Depends(get_db)):
    weights = db.query(PlatformWeight).all()
    if not weights:
        platforms = ["VK", "OK", "YouTube", "Ozon", "WB", "Yandex"]
        for p in platforms:
            db.add(PlatformWeight(platform_name=p, weight=1.0))
        db.commit()
        weights = db.query(PlatformWeight).all()
    return weights

@router.put("/weights", response_model=PlatformWeightResponse)
def update_weight(weight_update: PlatformWeightUpdate, db: Session = Depends(get_db)):
    platform = db.query(PlatformWeight).filter(PlatformWeight.platform_name == weight_update.platform_name).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    platform.weight = weight_update.weight
    db.commit()
    db.refresh(platform)
    return platform

# --- Scoring Engine ---

@router.post("/score/calculate", response_model=ScoreCalculationResponse)
def calculate_score(request: ScoreCalculationRequest, db: Session = Depends(get_db)):
    # Fetch latest weights
    weights_db = db.query(PlatformWeight).all()
    weight_map = {w.platform_name: w.weight for w in weights_db}
    
    weighted_sum = 0.0
    breakdown = {}
    
    for platform, volume in request.volumes.items():
        weight = weight_map.get(platform, 1.0) # Default to 1.0 if not found
        contribution = volume * weight
        weighted_sum += contribution
        breakdown[platform] = contribution
        
    # Formula: Sum * (1 + GrowthRate)
    unified_score = weighted_sum * (1 + request.growth_rate)
    
    return ScoreCalculationResponse(
        unified_score=round(unified_score, 2),
        breakdown=breakdown
    )
