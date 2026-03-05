import random
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.services.rag_store import top_ozon_titles, russian_selling_points


class LinguisticAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="linguistic")

    def select_hook(self, product_name: str, hooks: List[str]) -> str:
        tokens = set(product_name.lower().split())
        best = hooks[0]
        best_score = -1
        for hook in hooks:
            score = len(tokens.intersection(set(hook.lower().split())))
            if score > best_score:
                best = hook
                best_score = score
        return best

    async def run(self, payload: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        product_info = str(payload.get("product_info", ""))
        selling_points = str(payload.get("selling_points", ""))
        platform = str(payload.get("platform", "Ozon"))
        language = str(payload.get("language", "ru"))
        
        # Dynamic LLM generation if DB session is provided
        seo_titles = []
        short_desc = ""
        detail_desc = ""
        ad_copy = ""

        if db:
            llm = self.get_llm(db)
            if llm:
                prompt_base = f"Product: {product_info}\nSelling Points: {selling_points}\nPlatform: {platform}\nLanguage: {language}"
                
                seo_titles_raw = await llm.generate(f"{prompt_base}\nGenerate 3 SEO optimized titles. Return as a list.")
                seo_titles = [t.strip() for t in seo_titles_raw.split('\n') if t.strip()]

                short_desc = await llm.generate(f"{prompt_base}\nGenerate a short description (max 200 chars).")
                detail_desc = await llm.generate(f"{prompt_base}\nGenerate a detailed product description with HTML formatting.")
                ad_copy = await llm.generate(f"{prompt_base}\nGenerate a social media ad copy for VK/Instagram.")

        # Fallback if LLM fails or not configured
        if not seo_titles:
            seo_titles = [f"{product_info} - Best Choice", f"Buy {product_info} on {platform}"]
        if not short_desc:
            short_desc = f"High quality {product_info} with {selling_points}."
        
        return {
            "seo_title": seo_titles,
            "short_description": short_desc,
            "detail_description": detail_desc,
            "ad_copy": ad_copy,
        }
