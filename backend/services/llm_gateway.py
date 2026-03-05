from typing import Protocol, Dict, Any, Optional
from openai import AsyncOpenAI
import httpx

class LLMInterface(Protocol):
    provider_name: str
    model_id: str

    async def generate(self, prompt: str, meta: Optional[Dict[str, Any]] = None) -> str:
        ...


class OpenAIProvider:
    def __init__(self, base_url: str, api_key: str, model_id: str) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model_id = model_id
        self.provider_name = "openai"
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=httpx.AsyncClient(timeout=60.0)
        )

    async def generate(self, prompt: str, meta: Optional[Dict[str, Any]] = None) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error: {str(e)}"


class DeepSeekProvider:
    def __init__(self, base_url: str, api_key: str, model_id: str) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model_id = model_id
        self.provider_name = "deepseek"
        # DeepSeek is OpenAI compatible
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=httpx.AsyncClient(timeout=60.0)
        )

    async def generate(self, prompt: str, meta: Optional[Dict[str, Any]] = None) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error: {str(e)}"


class GeminiProvider:
    def __init__(self, base_url: str, api_key: str, model_id: str) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model_id = model_id
        self.provider_name = "gemini"
        # Using OpenAI client for Gemini as well (assuming OpenAI-compatible endpoint as provided)
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=httpx.AsyncClient(timeout=60.0)
        )

    async def generate(self, prompt: str, meta: Optional[Dict[str, Any]] = None) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error: {str(e)}"
