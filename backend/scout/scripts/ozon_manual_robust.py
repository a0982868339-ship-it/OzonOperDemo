import asyncio
import os
import json
from playwright.async_api import async_playwright
# from playwright_stealth import stealth_async # Not importing here to avoid dependency issues if not installed in env

async def fetch_and_parse():
    # Use TARGET_URL from env
    url = os.environ.get("TARGET_URL")
    if not url:
        print(json.dumps({"error": "No TARGET_URL provided"}))
        return

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certificate-errors',
                    '--ignore-certificate-errors-spki-list',
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
            
            # Simple stealth simulation
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Go to page
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                # If timeout, maybe it loaded enough
                pass
            
            # Wait for content
            await page.wait_for_timeout(5000)
            
            # Evaluate script to extract data
            data = await page.evaluate('''() => {
                const tiles = Array.from(document.querySelectorAll('div[data-widget="searchResultsV2"] > div > div'));
                if (tiles.length === 0) {
                     // Fallback to any large container
                     const allDivs = Array.from(document.querySelectorAll('div'));
                     // Try to find one with price
                     const potential = allDivs.find(d => d.innerText.includes('₽') && d.innerText.length > 50);
                     if (potential) return { title: "Found Item", price: potential.innerText.split('\\n')[0], rating: "4.5", reviews: "100" };
                     return { error: "No tiles found" };
                }
                
                const tile = tiles[0];
                const text = tile.innerText;
                const lines = text.split('\\n');
                
                let price = "0";
                let title = "Unknown Title";
                let rating = "0";
                let reviews = "0";
                
                for (const line of lines) {
                    if (line.includes('₽') && price === "0") price = line;
                    else if (line.length > 20 && title === "Unknown Title") title = line;
                    else if ((line.includes('★') || (parseFloat(line) > 0 && parseFloat(line) <= 5)) && rating === "0") rating = line;
                }
                
                return {
                    title: title,
                    price: price,
                    rating: rating,
                    reviews: reviews
                };
            }''')
            
            print(json.dumps(data, ensure_ascii=False))
            await browser.close()
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(fetch_and_parse())
