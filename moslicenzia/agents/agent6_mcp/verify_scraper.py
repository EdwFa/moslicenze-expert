import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from moslicenzia.agents.agent6_mcp.server import search_fias_portal, check_address_fias

async def test_scraper():
    print("--- Testing FIAS Scraper ---")
    
    addresses = [
        "г Москва, ул Автозаводская, д 18",  # Should fallback to MOCK if portal fails
        "Несуществующий адрес 999",         # Should return NOT_FOUND (all endpoints 404)
    ]
    
    for addr in addresses:
        print(f"\nSearching for: {addr}")
        # Test tool-level check (with mock fallback)
        res_tool = await check_address_fias(addr)
        print(f"Tool Result Status: {res_tool['status']}")
        
        if res_tool['status'] == 'VALID':
            print(f"  Normalized Address: {res_tool['normalized_address']}")
            print(f"  FIAS ID: {res_tool['fias_id']}")
            if res_tool.get('details', {}).get('is_mock'):
                print("  (Confirmed: Used Mock Fallback)")
        else:
            print(f"  Result: {res_tool.get('status')}")
            print(f"  Comment: {res_tool.get('comment')}")

if __name__ == "__main__":
    asyncio.run(test_scraper())

if __name__ == "__main__":
    asyncio.run(test_scraper())
