import aiosqlite
from typing import List, Optional
from decimal import Decimal
from model import Policy
from .util import get_database


async def create_policy(policy: Policy) -> int:
    """Create a new policy and return the policy ID."""
    async with await get_database() as db:
        cursor = await db.execute("""
            INSERT INTO policies (customer_id, start_date, end_date, product, premium)
            VALUES (?, ?, ?, ?, ?)
        """, (policy.customer_id, policy.start_date.isoformat(), policy.end_date.isoformat(), policy.product, str(policy.premium)))
        await db.commit()
        return cursor.lastrowid


async def get_policy_by_id(policy_id: int) -> Optional[Policy]:
    """Retrieve a policy by ID."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, customer_id, start_date, end_date, product, premium
            FROM policies WHERE id = ?
        """, (policy_id,))
        row = await cursor.fetchone()
        if row:
            from datetime import date
            return Policy(
                id=row[0],
                customer_id=row[1],
                start_date=date.fromisoformat(row[2]),
                end_date=date.fromisoformat(row[3]),
                product=row[4],
                premium=Decimal(row[5])
            )
        return None


async def get_all_policies() -> List[Policy]:
    """Retrieve all policies."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, customer_id, start_date, end_date, product, premium
            FROM policies
        """)
        rows = await cursor.fetchall()
        policies = []
        for row in rows:
            from datetime import date
            policies.append(Policy(
                id=row[0],
                customer_id=row[1],
                start_date=date.fromisoformat(row[2]),
                end_date=date.fromisoformat(row[3]),
                product=row[4],
                premium=Decimal(row[5])
            ))
        return policies


async def update_policy(policy_id: int, policy: Policy) -> bool:
    """Update a policy by ID. Returns True if successful, False if policy not found."""
    async with await get_database() as db:
        cursor = await db.execute("""
            UPDATE policies 
            SET customer_id = ?, start_date = ?, end_date = ?, product = ?, premium = ?
            WHERE id = ?
        """, (policy.customer_id, policy.start_date.isoformat(), policy.end_date.isoformat(), 
              policy.product, str(policy.premium), policy_id))
        await db.commit()
        return cursor.rowcount > 0


async def get_policies_by_customer_id(customer_id: int) -> List[Policy]:
    """Retrieve all policies for a specific customer."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, customer_id, start_date, end_date, product, premium
            FROM policies WHERE customer_id = ?
        """, (customer_id,))
        rows = await cursor.fetchall()
        policies = []
        for row in rows:
            from datetime import date
            policies.append(Policy(
                id=row[0],
                customer_id=row[1],
                start_date=date.fromisoformat(row[2]),
                end_date=date.fromisoformat(row[3]),
                product=row[4],
                premium=Decimal(row[5])
            ))
        return policies


async def delete_policy(policy_id: int) -> bool:
    """Delete a policy by ID. Returns True if successful, False if policy not found."""
    async with await get_database() as db:
        cursor = await db.execute("DELETE FROM policies WHERE id = ?", (policy_id,))
        await db.commit()
        return cursor.rowcount > 0