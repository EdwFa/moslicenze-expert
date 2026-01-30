import asyncio
import sys
import os

# Добавление корня проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from moslicenzia.agents.agent6_mcp.server import search_fias_portal, check_address_fias

async def test_scraper():
    print("--- Testing FIAS Scraper ---")
    
    addresses = [
        "г Москва, ул Автозаводская, д 18",  # Должен переключиться на МОК, если портал недоступен
        "Несуществующий адрес 999",         # Должен вернуть NOT_FOUND (все эндпоинты вернут 404)
    ]
    
    for addr in addresses:
        print(f"\nSearching for: {addr}")
        # Тестирование проверки на уровне инструмента (с переходом на мок)
        res_tool = await check_address_fias(addr)
        print(f"Tool Result Status: {res_tool['status']}")
        
        if res_tool['status'] == 'VALID':
            print(f"  Normalized Address: {res_tool['normalized_address']}")
            print(f"  FIAS ID: {res_tool['fias_id']}")
            if res_tool.get('details', {}).get('is_mock'):
                print("  (Подтверждено: использован Fallback на мок)")
        else:
            print(f"  Result: {res_tool.get('status')}")
            print(f"  Comment: {res_tool.get('comment')}")

if __name__ == "__main__":
    asyncio.run(test_scraper())
