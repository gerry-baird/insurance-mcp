from mcp.server.fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import List
from datetime import date
from model import Customer, Policy
from data import get_all_customers, get_customer_by_id, get_customers_by_state, get_all_policies, get_policy_by_id, get_policies_by_customer_id, init_database, init_sample_data, ensure_fresh_sample_data
import os
from dotenv import load_dotenv

load_dotenv()


PORT = os.environ.get("PORT", 8000)


# Create an MCP server
mcp = FastMCP(host="0.0.0.0", port=PORT)

@mcp.tool(name="Get all customers",
          description="Retrieves all customers.")
async def get_customers():
    await ensure_fresh_sample_data()
    return await get_all_customers()

@mcp.tool(name="Get customer by ID",
          description="Retrieves a customer using the customer ID.")
async def get_customer(customer_id: int):
    await ensure_fresh_sample_data()
    customer = await get_customer_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@mcp.tool(name="Get customer policies",
          description="Retrieves a customers policies using the customer ID.")
async def get_customer_policies(customer_id: int):
    await ensure_fresh_sample_data()
    policies = await get_policies_by_customer_id(customer_id)
    return policies

@mcp.tool(name="Get customer in state",
          description="Retrieves customers in a specific state.")
async def get_customers_in_state(state: str):
    await ensure_fresh_sample_data()
    customers = await get_customers_by_state(state)
    return customers

@mcp.tool(name="Calculate total customer premium",
          description="Sums all the policy premiums of a customer.")
async def get_customer_total_premium(customer_id: int):
    await ensure_fresh_sample_data()
    
    customer = await get_customer_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    policies = await get_policies_by_customer_id(customer_id)
    total_premium = sum(policy.premium for policy in policies)
    
    return {"customer_id": customer_id, "total_premium": total_premium}

@mcp.tool(name="Calculate days until policy end",
          description="Calculate the number of days until the policy ends.")
async def get_policy_days_to_end(policy_id: int):
    await ensure_fresh_sample_data()

    policy = await get_policy_by_id(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    today = date.today()
    days_to_end = (policy.end_date - today).days

    return {
        "policy_id": policy_id,
        "days_to_end": days_to_end
    }

async def startup():
    """Initialize database on startup"""
    await init_database()
    await init_sample_data()



if __name__ == "__main__":
    import asyncio
    asyncio.run(startup())
    mcp.run(transport="sse")
