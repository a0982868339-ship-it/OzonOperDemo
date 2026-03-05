"""
AnalystAgent — 精算 Agent (upgraded from AnalystService)

Combines algorithmic scoring with LLM-powered insight generation.
"""
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.services.analyst_service import AnalystService
from backend.models.prompt_template import PromptTemplate


class AnalystAgent(BaseAgent):
    def __init__(self, db: Optional[Session] = None) -> None:
        super().__init__(name="analyst")
        self.db = db

    async def run(self, payload: Dict[str, Any],
                  db: Optional[Session] = None) -> Dict[str, Any]:
        _db = db or self.db
        scout_data  = payload.get("scout_data", {})
        user_input  = payload.get("user_input", "")

        # ── Algorithmic scoring ───────────────────────────────────────────────
        data = scout_data.get("data", {}) if isinstance(scout_data, dict) else {}

        search_volume    = float(data.get("search_volume",    1000))
        social_mentions  = float(data.get("social_mentions",  500))
        growth_rate      = float(data.get("growth_rate",      0.15))
        product_count    = float(data.get("product_count",    200))

        unified_score = AnalystService.supply_demand_score(
            search_volume, social_mentions, growth_rate, product_count
        )
        competition = AnalystService.calculate_competition_level(unified_score)

        result: Dict[str, Any] = {
            "unified_score": round(unified_score, 4),
            "competition_level": competition,
            "search_volume":   search_volume,
            "social_mentions": social_mentions,
            "growth_rate":     growth_rate,
            "product_count":   product_count,
        }

        # ── LLM insight ──────────────────────────────────────────────────────
        if _db:
            llm = self.get_llm(_db)
            if llm:
                prompt = ""
                # Try fetching active prompt from DB
                pt = _db.query(PromptTemplate).filter(
                    PromptTemplate.owner_agent == "market_analyst",
                    PromptTemplate.is_active == True
                ).first()
                
                if pt:
                    # Replace variable {{ data }} and {{ keyword }} logic
                    # We'll just append data for simplicity if proper variables are missing
                    user_p = pt.user_template
                    user_p = user_p.replace("{{ keyword }}", str(user_input)).replace("{{keyword}}", str(user_input))
                    
                    data_str = f"UnifiedScore: {unified_score:.2f}, Competition: {competition}, Search volume: {search_volume}, Social mentions: {social_mentions}, Growth rate: {growth_rate:.0%}, Products: {product_count}"
                    user_p = user_p.replace("{{ data }}", data_str).replace("{{data}}", data_str)
                    
                    messages = [
                        {"role": "system", "content": pt.system_prompt},
                        {"role": "user", "content": user_p}
                    ]
                else:
                    messages = [{"role": "user", "content": f"""You are a Russian e-commerce market analyst.
Based on this data, write a 2-sentence market insight in English:
- User query: {user_input}
- UnifiedScore: {unified_score:.2f} (higher = better demand-to-supply ratio)
- Competition: {competition}
- Search volume: {search_volume}, Social mentions: {social_mentions}
- Growth rate: {growth_rate:.0%}, Products in market: {product_count}

Focus on whether this is a blue-ocean opportunity or red-ocean saturated market."""}]
                try:
                    if pt:
                        params_to_pass = {k:v for k,v in pt.parameters.items() if k != "model_id"}
                        insight = await llm.generate(messages, **params_to_pass)
                    else:
                        insight = await llm.generate(messages[0]["content"])
                    result["insight"] = insight.strip()
                except Exception:
                    result["insight"] = f"Score {unified_score:.2f} — {competition} competition market."
            else:
                result["insight"] = f"Score {unified_score:.2f} — {competition} competition market."
        else:
            result["insight"] = f"Score {unified_score:.2f} — {competition} competition market."

        return result
