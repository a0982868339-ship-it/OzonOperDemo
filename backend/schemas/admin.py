from typing import List, Optional, Dict
from pydantic import BaseModel

class AgentConfigUpdate(BaseModel):
    agent_name: str
    provider_name: str
    model_id: str
    temperature: float
    system_prompt: Optional[str] = None
    api_key: Optional[str] = None

class AgentConfigResponse(BaseModel):
    id: int
    agent_name: str
    provider_name: str
    model_id: str
    temperature: float
    system_prompt: Optional[str] = None
    # Don't return API Key

class PlatformWeightUpdate(BaseModel):
    platform_name: str
    weight: float

class PlatformWeightResponse(BaseModel):
    platform_name: str
    weight: float

class ScoreCalculationRequest(BaseModel):
    growth_rate: float
    volumes: Dict[str, float] # Platform -> Volume mapping

class ScoreCalculationResponse(BaseModel):
    unified_score: float
    breakdown: Dict[str, float]

class ConfigCreate(BaseModel):
    agent_name: str
    provider_name: str
    base_url: Optional[str] = None
    model_id: str
    api_key: str
    is_active: bool = False
    notes: Optional[str] = None

class ConfigUpdate(BaseModel):
    provider_name: Optional[str] = None
    base_url: Optional[str] = None
    model_id: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class ConfigResponse(BaseModel):
    id: int
    agent_name: str
    provider_name: str
    base_url: Optional[str] = None
    model_id: str
    is_active: bool
    masked_api_key: Optional[str] = None
    notes: Optional[str] = None

class TestConnectionRequest(BaseModel):
    provider_name: str
    api_key: str

class TestConnectionResponse(BaseModel):
    ok: bool
    message: str

class UserCreate(BaseModel):
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    
    class Config:
        from_attributes = True

from typing import Dict, Any
class TokenUsageStats(BaseModel):
    agent_name: str
    total_tokens: int
    total_cost: float
    request_count: int
    model_breakdown: Dict[str, Any]
