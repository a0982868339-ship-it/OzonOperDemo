from typing import Optional, Dict, Any
from pydantic import BaseModel


class AgentConfig(BaseModel):
    use_scout:      bool = True
    use_analyst:    bool = True
    use_linguistic: bool = True
    use_creative:   bool = True


# ── Requests ────────────────────────────────────────────────────────────────

class PipelineRunRequest(BaseModel):
    """Start a full pipeline mission."""
    user_input:   str
    title:        Optional[str] = None
    agent_config: AgentConfig = AgentConfig()


class SingleAgentRunRequest(BaseModel):
    """Run a single agent within an existing mission.
    override_data is merged into the agent's context so the user can
    supply their own copy / image prompt / raw data and skip generation.
    """
    override_data: Optional[Dict[str, Any]] = None


# ── Responses ────────────────────────────────────────────────────────────────

class AgentStatusMap(BaseModel):
    scout:      str
    analyst:    str
    linguistic: str
    creative:   str


class MissionResponse(BaseModel):
    id:               int
    title:            Optional[str]
    mode:             str
    status:           str
    user_input:       Optional[str]
    agent_status:     AgentStatusMap
    scout_result:     Optional[Dict[str, Any]]
    analyst_result:   Optional[Dict[str, Any]]
    linguistic_result: Optional[Dict[str, Any]]
    creative_result:  Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class MissionCreateResponse(BaseModel):
    mission_id: int
    status:     str
    message:    str
