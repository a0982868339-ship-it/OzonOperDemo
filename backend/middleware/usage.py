from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.usage_log import UsageLog


def estimate_cost(provider_name: str, model_id: str, tokens_input: int, tokens_output: int) -> float:
    rates = {
        "openai": 0.02,
        "deepseek": 0.006,
        "gemini": 0.01,
    }
    rate = rates.get(provider_name.lower(), 0.01)
    total_tokens = tokens_input + tokens_output
    return round(rate * total_tokens / 1000, 6)


async def usage_logging_middleware(request: Request, call_next: Callable) -> Response:
    response = await call_next(request)
    agent_name = request.headers.get("X-Agent-Name", "unknown")
    provider_name = request.headers.get("X-Provider-Name", "unknown")
    model_id = request.headers.get("X-Model-Id", "unknown")
    tokens_input = int(request.headers.get("X-Token-Input", "0"))
    tokens_output = int(request.headers.get("X-Token-Output", "0"))
    cost = estimate_cost(provider_name, model_id, tokens_input, tokens_output)
    log = UsageLog(
        agent_name=agent_name,
        provider_name=provider_name,
        model_id=model_id,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost_estimate=cost,
        request_path=str(request.url.path),
        created_at=datetime.utcnow(),
    )
    with SessionLocal() as session:
        session.add(log)
        session.commit()
    return response
