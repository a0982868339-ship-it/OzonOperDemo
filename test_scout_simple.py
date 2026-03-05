import asyncio
import json
import logging
from backend.core.database import SessionLocal
from backend.agents.scout_agent import ScoutAgent

# Configure logging to see agent output
logging.basicConfig(level=logging.INFO)

async def test_scout_books():
    print("Initializing Scout Agent...")
    db = SessionLocal()
    agent = ScoutAgent(db)
    
    # Target: A specific book page on books.toscrape.com (Sandbox for scrapers)
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    goal = "Extract book title, price, rating, and description."
    selectors = {
        "title": "h1",
        "price": "p.price_color",
        "rating": "p.star-rating", # Note: rating is often in class attribute, might need special logic
        "description": "#product_description + p"
    }
    
    print(f"Starting mission for {url}...")
    try:
        # Run the mission directly via Agent
        result = await agent.run_mission(url, goal, selectors)
        
        print("\n--- Crawled Data ---")
        if result.get("status") in ["success", "healed"]:
            print(json.dumps(result.get("data"), ensure_ascii=False, indent=2))
            
            if result.get("status") == "healed":
                print("\n✨ The agent successfully HEALED the crawler script!")
                print("\n--- Generated Python Code ---")
                print(result.get("code"))
        else:
            print("\n❌ Failed. Details:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_scout_books())
