"""
PromptEngineerAgent — 提示词工程师 Agent

职责：
  接收用户的原始需求描述，根据场景模式（SEO / 视频 / 广告 / 角色扮演），
  输出专业优化的 Prompt + 解释 + 可替换变量列表

agent_name in Config table: "prompt_engineer"
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent


# 各模式的系统提示词（即"提示词的提示词"，meta-prompt）
MODE_SYSTEM_PROMPTS = {
    "seo": """You are an expert SEO copywriter and prompt engineer for e-commerce platforms (especially Ozon, the Russian marketplace).
Your task: Transform a raw user need into a professional LLM prompt that generates high-converting SEO product listings in Russian.
The output prompt should instruct an LLM to write: Russian SEO title, product description, bullet points, and tags.""",

    "video": """You are a professional video director and AI prompt engineer specializing in e-commerce video content for Russian platforms.
Your task: Transform a raw user need into a professional prompt for AI video generation tools (Runway, Sora, Kling).
The output prompt should include: camera movements, lighting, color grading, atmosphere, and Russian market aesthetic requirements.""",

    "ad": """You are an expert advertising copywriter and prompt engineer for Russian social media (VK, Telegram, Instagram).
Your task: Transform a raw user need into a professional LLM prompt that generates compelling ad copy.
The output prompt should instruct an LLM to write: attention-grabbing headline, body copy, CTA, and hashtags in Russian.""",

    "roleplay": """You are an expert AI character designer and prompt engineer.
Your task: Transform a raw user need into a professional system prompt for creating an AI assistant persona.
The output prompt should define: personality, expertise, communication style, boundaries, and example interactions.""",
}

MODE_NAMES = {
    "seo": "SEO 电商文案",
    "video": "视频生成脚本",
    "ad": "社媒广告文案",
    "roleplay": "AI 角色扮演",
}


class PromptEngineerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="prompt_engineer")

    async def run(self, payload: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        raw_input = str(payload.get("raw_input", "")).strip()
        mode = str(payload.get("mode", "seo")).lower()

        if mode not in MODE_SYSTEM_PROMPTS:
            mode = "seo"

        optimized_prompt = ""
        explanation = ""
        variables = []

        if db:
            llm = self.get_llm(db)
            if llm:
                system_ctx = MODE_SYSTEM_PROMPTS[mode]

                # Step 1: 生成优化后的 Prompt
                meta_prompt = f"""{system_ctx}

User's raw need: "{raw_input}"

Generate a professional, detailed LLM prompt (in English) that will produce excellent results.
The prompt should:
1. Include clear role definition
2. Specify output format requirements
3. Include relevant constraints and quality requirements
4. Use {{variable_name}} placeholders for reusable parts

Output ONLY the optimized prompt text, no other content."""

                optimized_prompt = await llm.generate(meta_prompt)

                # Step 2: 解释为什么这么优化
                explain_prompt = f"""I created this optimized prompt:
---
{optimized_prompt}
---

Original user need: "{raw_input}"

Explain in Chinese (3-5 bullet points) why this prompt is better than the original description.
Focus on: what techniques were used, why they improve output quality.
Format: bullet points starting with •"""

                explanation = await llm.generate(explain_prompt)

                # Step 3: 提取变量列表
                import re
                variables = re.findall(r'\{(\w+)\}', optimized_prompt)
                variables = list(dict.fromkeys(variables))  # 去重保序

        # Fallback
        if not optimized_prompt:
            optimized_prompt = self._fallback_prompt(raw_input, mode)
        if not explanation:
            explanation = (
                f"• 添加了明确的角色定义，让 LLM 更专注于{MODE_NAMES[mode]}场景\n"
                f"• 指定了输出格式，减少幻觉和格式不一致\n"
                f"• 加入了质量约束条件，提升输出专业性\n"
                f"• 使用变量占位符，方便复用"
            )

        return {
            "mode": mode,
            "mode_name": MODE_NAMES.get(mode, mode),
            "original_input": raw_input,
            "optimized_prompt": optimized_prompt,
            "explanation": explanation,
            "variables": variables,
        }

    def _fallback_prompt(self, raw_input: str, mode: str) -> str:
        """LLM 未配置时的模板回退"""
        templates = {
            "seo": f"""You are an expert SEO copywriter for Ozon (Russian e-commerce platform).

Product information: {{{{"product_name"}}}} - {raw_input}
Target language: Russian
Platform requirements: Ozon marketplace standards

Please generate:
1. SEO-optimized title (max 200 characters, include main keywords)
2. Short description (max 300 characters, highlight key benefits)
3. Detailed description with HTML formatting
4. 5-7 search tags

Output as structured JSON.""",

            "video": f"""You are a professional video director creating content for Russian e-commerce.

Product/Scene: {raw_input}
Duration: {{duration}}
Style: {{style}} (e.g., cinematic, minimal, energetic)

Generate a professional video prompt including:
- Camera movements and angles
- Lighting setup
- Color grading style
- Key visual elements
- Atmosphere and mood

Also provide a 3-shot shot list and a Russian voiceover script.""",

            "ad": f"""You are an expert advertising copywriter for Russian social media (VK, Telegram).

Product: {raw_input}
Target audience: {{target_audience}}
Platform: {{platform}}

Generate:
1. Attention-grabbing headline (Russian, max 10 words)
2. Body copy (Russian, 2-3 sentences)
3. CTA button text (Russian)
4. 5 relevant hashtags

Tone: compelling and urgent without being spammy.""",

            "roleplay": f"""You are an AI assistant designer.

Create a system prompt for an AI assistant with this role: {raw_input}

The system prompt should define:
- Persona name and background
- Core expertise and capabilities
- Communication style and tone
- Hard limits and what to refuse
- 2-3 example interaction patterns""",
        }
        return templates.get(mode, templates["seo"])
