# Base Crawler Template for Scout Agent
# Uses: httpx, beautifulsoup4
# The agent will inject {selectors}
# URL is provided via environment variable TARGET_URL

BASE_CRAWLER_TEMPLATE = """
import sys
import json
import asyncio
import httpx
import os
from bs4 import BeautifulSoup

# Use TARGET_URL from env or fallback for testing
URL = os.environ.get("TARGET_URL", "")
SELECTORS = {selectors}  # Expected dict: {{"title": "h1", "price": ".price", ...}}

async def fetch_and_parse():
    if not URL:
        print(json.dumps({{"error": "No TARGET_URL provided"}}))
        return

    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }}
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            resp = await client.get(URL, headers=headers)
            resp.raise_for_status()
            html = resp.text
            
            soup = BeautifulSoup(html, "html.parser")
            result = {{}}
            
            for field, selector in SELECTORS.items():
                element = soup.select_one(selector)
                if element:
                    result[field] = element.get_text(strip=True)
                else:
                    result[field] = None
            
            # Special logic for structured data if selector is generic
            # e.g. finding JSON-LD
            if not any(result.values()):
                json_ld = soup.find("script", type="application/ld+json")
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        result["_json_ld"] = data
                    except:
                        pass

            print(json.dumps(result))
            return result

    except Exception as e:
        # Print error to stderr but also print empty result to avoid crash
        print(f"ERROR: {{str(e)}}", file=sys.stderr)
        # sys.exit(1) # Don't exit, just return empty so agent knows it failed
        print(json.dumps({{}}))

if __name__ == "__main__":
    asyncio.run(fetch_and_parse())
"""
