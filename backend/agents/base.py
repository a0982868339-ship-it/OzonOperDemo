from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.services.model_provider_factory import ModelProviderFactory
from backend.services.llm_gateway import LLMInterface


class BaseAgent:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    async def run(self, payload: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        raise NotImplementedError()

    def get_llm(self, db: Session) -> Optional[LLMInterface]:
        factory = ModelProviderFactory(db)
        return factory.get_provider(self.name)
