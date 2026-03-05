import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from backend.agents.base import BaseAgent
from backend.services.model_provider_factory import ModelProviderFactory
from backend.scout.templates.base_crawler import BASE_CRAWLER_TEMPLATE
from backend.scout.executor import CodeExecutor
from backend.models.scout_script import ScoutScript


class ScoutAgent(BaseAgent):
    def __init__(self, db: Session, agent_name: str = "scout"):
        super().__init__(name=agent_name)
        self.db = db
        self.provider = ModelProviderFactory(db).get_provider(agent_name)
        self.executor = CodeExecutor()

    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "")
        except:
            return url

    def _get_stored_script(self, domain: str) -> Optional[str]:
        script = self.db.query(ScoutScript).filter(ScoutScript.domain == domain).first()
        return script.script_code if script else None

    def _save_stored_script(self, domain: str, code: str) -> None:
        now = datetime.utcnow()
        script = self.db.query(ScoutScript).filter(ScoutScript.domain == domain).first()
        if script:
            script.script_code = code
            script.updated_at = now
        else:
            script = ScoutScript(domain=domain, script_code=code, created_at=now, updated_at=now)
            self.db.add(script)
        self.db.commit()

    async def run_mission(self, url: str, goal: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Runs a crawling mission with self-healing capabilities.
        1. Check for stored script for this domain.
        2. If none, use template.
        3. If result empty/error -> Agent analyzes and modifies code.
        4. Retry (max 3 times).
        5. If successful after modification, save script.
        """
        domain = self._get_domain(url)
        env = {"TARGET_URL": url}
        
        # 1. Try Stored Script or Template
        stored_code = self._get_stored_script(domain)
        if stored_code:
            print(f"[Scout] Using stored script for {domain}")
            code = stored_code
        else:
            print(f"[Scout] Using default template for {domain}")
            code = self._generate_code(selectors)

        success, result, error = await self.executor.run_code(code, env=env)

        if success and self._is_result_valid(result):
            return {"status": "success", "data": result}
        
        # If stored script failed, maybe we should fallback to template first before healing?
        # But let's assume we want to heal the current best knowledge (which is stored script or template).
        
        # 2. Self-Healing Loop
        max_retries = 3
        for attempt in range(max_retries):
            print(f"[Scout] Healing attempt {attempt+1}/{max_retries} for {url}")
            
            # Construct Prompt for LLM
            prompt = self._construct_healing_prompt(url, goal, code, error, result)
            
            if not self.provider:
                return {"status": "failed", "error": "No LLM provider configured for Scout"}
            
            # Get new code from LLM
            response = await self.provider.generate(prompt)
            new_code = self._extract_code_block(response)
            
            if not new_code:
                print(f"[Scout] LLM failed to generate valid code: {response}")
                continue

            # Execute New Code
            success, new_result, new_error = await self.executor.run_code(new_code, env=env)
            
            if success and self._is_result_valid(new_result):
                # Save the successful script!
                print(f"[Scout] Healing successful! Saving script for {domain}")
                self._save_stored_script(domain, new_code)
                return {"status": "healed", "data": new_result, "code": new_code}
            
            # Update context for next loop
            code = new_code
            error = new_error
            result = new_result

        return {"status": "failed", "error": f"Failed after {max_retries} attempts. Last error: {error}"}

    def _generate_code(self, selectors: Dict[str, str]) -> str:
        # Inject selectors, URL comes from env
        return BASE_CRAWLER_TEMPLATE.format(selectors=json.dumps(selectors))

    def _is_result_valid(self, result: Any) -> bool:
        if not result:
            return False
        if isinstance(result, dict):
            # Check if error key exists
            if "error" in result:
                return False
            # Check if all values are None (failed extraction)
            if all(v is None for v in result.values()):
                return False
            # Check if empty dict
            if not result:
                return False
        return True

    def _construct_healing_prompt(self, url: str, goal: str, code: str, error: str, result: Any) -> str:
        return f"""
        You are an expert Python Web Scraper.
        The following script failed to extract data from {url}.
        Goal: {goal}
        
        Current Code:
        ```python
        {code}
        ```
        
        Execution Error:
        {error}
        
        Execution Output:
        {result}
        
        Task:
        Fix the code to correctly extract the data.
        - IMPORTANT: Use `os.environ.get("TARGET_URL")` to get the URL. Do not hardcode the URL.
        - If the error is a network issue, add retries or headers.
        - If 'httpx' fails due to Cloudflare or dynamic content, USE 'playwright'.
        - Example Playwright setup:
          ```python
          import asyncio
          import json
          import os
          from playwright.async_api import async_playwright

          async def fetch_and_parse():
              url = os.environ.get("TARGET_URL")
              async with async_playwright() as p:
                  browser = await p.chromium.launch(headless=True)
                  page = await browser.new_page()
                  # Add stealth or headers if needed
                  await page.goto(url, wait_until="domcontentloaded")
                  
                  # Extract data using page.locator or page.content()
                  # ...
                  
                  # Example output
                  result = {{...}}
                  print(json.dumps(result))
                  await browser.close()

          if __name__ == "__main__":
              asyncio.run(fetch_and_parse())
          ```
        - If the extraction failed (None values), try different selectors or JSON-LD parsing.
        - Print the final result as JSON to stdout.
        - Return ONLY the full corrected Python code.
        """

    def _extract_code_block(self, text: str) -> Optional[str]:
        # Simple extraction of code between ```python and ```
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return None
