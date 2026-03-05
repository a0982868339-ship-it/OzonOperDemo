# Manual script for Ozon.ru using Playwright + Stealth
# To be injected into ScoutScript DB

OZON_CRAWLER_SCRIPT = """
import asyncio
import json
import os
import random
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def fetch_and_parse():
    url = os.environ.get("TARGET_URL")
    if not url:
        print(json.dumps({"error": "No TARGET_URL provided"}))
        return

    # Randomize viewport and user agent slightly if needed, but stealth handles most
    try:
        async with async_playwright() as p:
            # Use a persistent context or launch with specific args to be more stealthy
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certifcate-errors',
                    '--ignore-certifcate-errors-spki-list',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='ru-RU',
                timezone_id='Europe/Moscow'
            )
            
            page = await context.new_page()
            await stealth_async(page)
            
            # Go to page
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Ozon specific: Wait for product tiles
            # They usually have classes like 'tile-hover-target' or specific data attributes
            # Let's try a generic wait for common container
            try:
                await page.wait_for_selector('div[data-widget="searchResultsV2"]', timeout=15000)
            except:
                # Fallback, maybe it's V1 or just wait a bit
                await asyncio.sleep(5)
            
            # Extract data
            # We will try to find the first product card and extract details
            # This is a simplified extraction for the "Snapshot" goal
            
            # Evaluated in browser context
            data = await page.evaluate('''() => {
                const item = document.querySelector('div.widget-search-result-container > div > div');
                if (!item) return {};
                
                // Helper to get text safely
                const getText = (sel) => {
                    const el = document.querySelector(sel);
                    return el ? el.innerText.trim() : null;
                };

                // Ozon classes are dynamic (random strings like 'tsBody500Medium'), so we might need robust strategy
                // Strategy: Find price by currency symbol or structure
                // Find title by h1 or specific class if on product page, but this is search page
                
                // Let's look for tiles. 
                // A common pattern for Ozon tiles: they contain price, rating, reviews.
                
                // Let's try to grab the first tile's text content and parse it naively if classes fail, 
                // or try known partial classes.
                
                const tiles = Array.from(document.querySelectorAll('div[data-index]'));
                if (tiles.length === 0) return { error: "No tiles found" };
                
                const tile = tiles[0]; // First product
                
                // Title often has 'tsBody500Medium' or is inside an 'a' tag with long text
                // Price often ends with '₽'
                
                const text = tile.innerText;
                const lines = text.split('\\n');
                
                let price = null;
                let title = null;
                let rating = null;
                let reviews = null;
                
                // Naive parsing of visual lines
                for (const line of lines) {
                    if (line.includes('₽') && !price) price = line;
                    else if (line.length > 20 && !title) title = line;
                    else if ((line.includes('★') || parseFloat(line) > 0 && parseFloat(line) <= 5) && !rating) rating = line;
                }
                
                return {
                    title: title || "Unknown Title",
                    price: price || "0",
                    rating: rating,
                    reviews: "0" // hard to parse reliably without specific selector
                };
            }''')
            
            print(json.dumps(data, ensure_ascii=False))
            await browser.close()
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(fetch_and_parse())
"""
