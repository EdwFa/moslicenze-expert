import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def verify_agent6():
    # Parameters for the Agent 6 server
    server_params = StdioServerParameters(
        command="py",
        args=["moslicenzia/agents/agent6_mcp/server.py"]
    )

    print("--- Verifying Agent 6 (MCP FIAS) ---")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. List tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # 2. Test address check (Mock mode)
            print("\nTesting: check_address_fias ('ул. Автозаводская, 18')")
            res_addr = await session.call_tool("check_address_fias", {"address_query": "ул. Автозаводская, 18"})
            print(f"Result: {res_addr.content[0].text if res_addr.content else 'None'}")
            
            # 3. Test KPP lookup
            print("\nTesting: get_subdivision_kpp ('fias-123')")
            res_kpp = await session.call_tool("get_subdivision_kpp", {"fias_id": "fias-123"})
            print(f"Result: {res_kpp.content[0].text if res_kpp.content else 'None'}")

if __name__ == "__main__":
    asyncio.run(verify_agent6())
