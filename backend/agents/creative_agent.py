from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent


class CreativeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="creative")
        self.modifiers: List[str] = [
            "Cyrillic UI labels",
            "Winter lighting",
            "Modern Russian interior",
            "Soft snow ambience",
            "High-end retail aesthetic",
        ]

    async def run(self, payload: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        base_prompt = str(payload.get("base_prompt", "")).strip()
        
        # Dynamic LLM generation if DB session is provided
        if db:
            llm = self.get_llm(db)
            if llm:
                # Use the configured LLM to enhance the prompt
                enhanced_prompt = await llm.generate(f"Enhance this product prompt for Russian market: {base_prompt}")
                if enhanced_prompt:
                    base_prompt = enhanced_prompt

        extra = ", ".join(self.modifiers)
        prompt = f"{base_prompt}, {extra}".strip(", ")
        return {
            "image_prompt": prompt,
            "video_prompt": f"{prompt}, cinematic product rotation",
        }
