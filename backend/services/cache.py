import os
import json
from typing import Optional, Dict, Any
from redis import Redis


def get_redis() -> Optional[Redis]:
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    try:
        return Redis(host=host, port=port, decode_responses=True)
    except Exception:
        return None


def cache_set(key: str, value: Dict[str, Any], ttl: int = 300) -> None:
    redis = get_redis()
    if not redis:
        return
    redis.setex(key, ttl, json.dumps(value, default=str))


def cache_get(key: str) -> Optional[Dict[str, Any]]:
    redis = get_redis()
    if not redis:
        return None
    payload = redis.get(key)
    if not payload:
        return None
    return json.loads(payload)


def cache_delete(key: str) -> None:
    redis = get_redis()
    if not redis:
        return
    redis.delete(key)
