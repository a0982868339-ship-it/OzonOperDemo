import asyncio
import json
import logging
from backend.core.database import SessionLocal
from backend.services.scout_service import ScoutService

# Configure logging to see agent output
logging.basicConfig(level=logging.INFO)

async def test_scout():
    print("Initializing Scout Service...")
    db = SessionLocal()
    service = ScoutService(db)
    
    keyword = "iphone"
    platform = "ozon"
    
    print(f"Starting mission for '{keyword}' on {platform}...")
    try:
        # Run the mission
        result = await service.run_keyword_mission(keyword, platform)
        
        print("\n--- Mission Result ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get("status") in ["success", "healed"]:
            print("\n✅ Success! Data extracted.")
            if result.get("status") == "healed":
                print("✨ The agent successfully HEALED the crawler script!")
        else:
            print("\n❌ Failed. Check logs for details.")
            
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_scout())
