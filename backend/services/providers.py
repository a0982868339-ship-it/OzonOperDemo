from typing import List


async def generate_text_openai(prompt: str) -> str:
    return f"OpenAI mock response: {prompt}"


async def generate_text_deepseek(prompt: str) -> str:
    return f"DeepSeek mock response: {prompt}"


async def generate_media_flux(prompt: str) -> List[str]:
    return [
        "https://picsum.photos/seed/flux1/800/800",
        "https://picsum.photos/seed/flux2/800/800",
    ]


async def generate_media_kling(prompt: str) -> List[str]:
    return [
        "https://storage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    ]
