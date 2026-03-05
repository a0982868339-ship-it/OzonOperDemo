from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.config import Config
from backend.models.usage_log import UsageLog
from backend.services.crypto import decrypt_value
from backend.services.cache import cache_get, cache_set, cache_delete
from backend.services.llm_gateway import LLMInterface, OpenAIProvider, DeepSeekProvider, GeminiProvider


class LoggedLLMProvider:
    def __init__(self, provider: LLMInterface, db: Session, agent_name: str):
        self.provider = provider
        self.db = db
        self.agent_name = agent_name
        self.provider_name = provider.provider_name
        self.model_id = provider.model_id

    async def generate(self, prompt: str, meta: Optional[Dict[str, Any]] = None) -> str:
        # 1. Generate
        result = await self.provider.generate(prompt, meta)
        
        # 2. Estimate tokens (simple approximation)
        tokens_input = int(len(prompt.split()) * 1.3)
        tokens_output = int(len(result.split()) * 1.3)
        
        # 3. Calculate cost
        cost = self._estimate_cost(self.provider_name, self.model_id, tokens_input, tokens_output)

        # 4. Log to DB
        log = UsageLog(
            agent_name=self.agent_name,
            provider_name=self.provider_name,
            model_id=self.model_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_estimate=cost,
            request_path="internal/llm",
            created_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        
        return result

    def _estimate_cost(self, provider_name: str, model_id: str, tokens_input: int, tokens_output: int) -> float:
        rates = {"openai": 0.02, "deepseek": 0.006, "gemini": 0.01}
        rate = rates.get(provider_name.lower(), 0.01)
        total_tokens = tokens_input + tokens_output
        return round(rate * total_tokens / 1000, 6)


class ModelProviderFactory:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _cache_key(self, agent_name: str) -> str:
        return f"ai_config:{agent_name}"

    def get_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        cached = cache_get(self._cache_key(agent_name))
        if cached:
            return cached
        record = (
            self.db.query(Config)
            .filter(Config.agent_name == agent_name, Config.is_active.is_(True))
            .order_by(Config.updated_at.desc())
            .first()
        )
        if not record:
            return None
        payload = {
            "agent_name": record.agent_name,
            "provider_name": record.provider_name,
            "base_url": record.base_url,
            "model_id": record.model_id,
            "api_key": decrypt_value(record.api_key_encrypted),
        }
        cache_set(self._cache_key(agent_name), payload)
        return payload

    def refresh_cache(self, agent_name: str) -> None:
        cache_delete(self._cache_key(agent_name))
        self.get_config(agent_name)

    def get_provider(self, agent_name: str) -> Optional[LLMInterface]:
        config = self.get_config(agent_name)
        if not config:
            return None
        provider = config["provider_name"].lower()
        provider_instance = None
        
        if provider == "openai":
            provider_instance = OpenAIProvider(config["base_url"], config["api_key"], config["model_id"])
        elif provider == "deepseek":
            provider_instance = DeepSeekProvider(config["base_url"], config["api_key"], config["model_id"])
        elif provider == "gemini":
            provider_instance = GeminiProvider(config["base_url"], config["api_key"], config["model_id"])
            
        if provider_instance:
            return LoggedLLMProvider(provider_instance, self.db, agent_name)
        return None
