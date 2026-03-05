"""
VideoAgent — 独立视频提示词增强 Agent

职责：
  接收用户的简单视频描述，用 LLM 增强为专业级视频 Prompt（适配 Runway / Sora / Kling）
  同时输出分镜脚本和旁白建议

agent_name in Config table: "video"
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent


class VideoAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="video")

    async def run(self, payload: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        base_prompt = str(payload.get("base_prompt", "")).strip()
        duration = str(payload.get("duration", "15s"))
        style = str(payload.get("style", "cinematic"))
        platform = str(payload.get("platform", "Ozon"))

        enhanced_prompt = ""
        shot_list = []
        narration = ""

        if db:
            llm = self.get_llm(db)
            if llm:
                # Step 1: 增强主 Prompt
                enhance_prompt = f"""You are a professional video director AI for e-commerce.
Transform this simple description into a professional video generation prompt for AI video tools (Runway Gen-3 / Sora / Kling).

Product/Scene: {base_prompt}
Duration: {duration}
Visual Style: {style}
Platform: {platform} (Russian e-commerce)

Output a professional video prompt in English that includes:
- Camera movement (pan, zoom, dolly, etc.)
- Lighting description
- Color grading style  
- Atmosphere/mood
- Key visual elements

Output ONLY the enhanced prompt, no explanations."""

                enhanced_prompt = await llm.generate(enhance_prompt)

                # Step 2: 生成分镜脚本
                shot_prompt = f"""Based on this video concept: "{base_prompt}" for a {duration} video.
Create a shot list with 3-4 shots. For each shot output:
SHOT 1: [duration] | [camera angle] | [action description]
SHOT 2: [duration] | [camera angle] | [action description]
...
Output ONLY the shot list, no other text."""

                shot_raw = await llm.generate(shot_prompt)
                shot_list = [s.strip() for s in shot_raw.strip().split("\n") if s.strip()]

                # Step 3: 旁白建议（俄语）
                narration_prompt = f"""Write a short, compelling Russian voiceover script (2-3 sentences) for this product video:
Product: {base_prompt}
Style: {style}
Platform: Ozon (Russian e-commerce)

Output ONLY the Russian text, no translations."""

                narration = await llm.generate(narration_prompt)

        # Fallback：LLM 未配置时的基础增强
        if not enhanced_prompt:
            enhanced_prompt = (
                f"{base_prompt}, {style} cinematography, "
                f"professional product photography, "
                f"warm studio lighting, shallow depth of field, "
                f"4K ultra HD, Russian market aesthetic, "
                f"e-commerce showcase style"
            )
        if not shot_list:
            shot_list = [
                f"SHOT 1: 3s | Overhead wide | Product reveal from packaging",
                f"SHOT 2: 5s | Close-up dolly in | Key feature highlight",
                f"SHOT 3: 4s | 360° orbit | Full product showcase",
                f"SHOT 4: 3s | Pull back | Lifestyle context shot",
            ]
        if not narration:
            narration = f"Представляем {base_prompt} — ваш лучший выбор на Ozon."

        return {
            "enhanced_prompt": enhanced_prompt,
            "shot_list": shot_list,
            "narration_ru": narration,
            "duration": duration,
            "style": style,
        }
