from mcp.server.fastmcp import FastMCP
from typing import List
from datetime import date
from model import Customer, Policy
from data import get_all_customers, get_customer_by_id, get_customers_by_state, get_all_policies, get_policy_by_id, get_policies_by_customer_id, init_database, init_sample_data, ensure_fresh_sample_data

# Create an MCP server
mcp = FastMCP("insurance-mcp")

@mcp.tool()
async def get_customers():
    await ensure_fresh_sample_data()
    return await get_all_customers()

@mcp.tool()
def echo(message: str) -> str:
    """Echo tool that returns the message sent to it.

    Args:
        message: The message to echo back

    Returns:
        The same message that was sent
    """
    message = "Echo: " + message
    return message

async def startup():
    """Initialize database on startup"""
    await init_database()
    await init_sample_data()

if __name__ == "__main__":
    import asyncio
    asyncio.run(startup())
    mcp.run(transport="streamable-http")