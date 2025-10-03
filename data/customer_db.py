import aiosqlite
from typing import List, Optional
from model import Customer
from .util import get_database


async def create_customer(customer: Customer) -> int:
    """Create a new customer and return the customer ID."""
    async with await get_database() as db:
        cursor = await db.execute("""
            INSERT INTO customers (name, date_of_birth, email, address, state)
            VALUES (?, ?, ?, ?, ?)
        """, (customer.name, customer.date_of_birth.isoformat(), customer.email, customer.address, customer.state))
        await db.commit()
        return cursor.lastrowid


async def get_customer_by_id(customer_id: int) -> Optional[Customer]:
    """Retrieve a customer by ID."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, name, date_of_birth, email, address, state
            FROM customers WHERE id = ?
        """, (customer_id,))
        row = await cursor.fetchone()
        if row:
            from datetime import date
            return Customer(
                id=row[0],
                name=row[1],
                date_of_birth=date.fromisoformat(row[2]),
                email=row[3],
                address=row[4],
                state=row[5]
            )
        return None


async def get_customer_by_email(email: str) -> Optional[Customer]:
    """Retrieve a customer by email."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, name, date_of_birth, email, address, state
            FROM customers WHERE email = ?
        """, (email,))
        row = await cursor.fetchone()
        if row:
            from datetime import date
            return Customer(
                id=row[0],
                name=row[1],
                date_of_birth=date.fromisoformat(row[2]),
                email=row[3],
                address=row[4],
                state=row[5]
            )
        return None


async def get_all_customers() -> List[Customer]:
    """Retrieve all customers."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, name, date_of_birth, email, address, state
            FROM customers
        """)
        rows = await cursor.fetchall()
        customers = []
        for row in rows:
            from datetime import date
            customers.append(Customer(
                id=row[0],
                name=row[1],
                date_of_birth=date.fromisoformat(row[2]),
                email=row[3],
                address=row[4],
                state=row[5]
            ))
        return customers


async def get_customers_by_state(state: str) -> List[Customer]:
    """Retrieve all customers in a specific state."""
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT id, name, date_of_birth, email, address, state
            FROM customers WHERE state = ?
        """, (state,))
        rows = await cursor.fetchall()
        customers = []
        for row in rows:
            from datetime import date
            customers.append(Customer(
                id=row[0],
                name=row[1],
                date_of_birth=date.fromisoformat(row[2]),
                email=row[3],
                address=row[4],
                state=row[5]
            ))
        return customers


async def update_customer(customer_id: int, customer: Customer) -> bool:
    """Update a customer by ID. Returns True if successful, False if customer not found."""
    async with await get_database() as db:
        cursor = await db.execute("""
            UPDATE customers 
            SET name = ?, date_of_birth = ?, email = ?, address = ?, state = ?
            WHERE id = ?
        """, (customer.name, customer.date_of_birth.isoformat(), customer.email, 
              customer.address, customer.state, customer_id))
        await db.commit()
        return cursor.rowcount > 0


async def delete_customer(customer_id: int) -> bool:
    """Delete a customer by ID. Returns True if successful, False if customer not found."""
    async with await get_database() as db:
        cursor = await db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        await db.commit()
        return cursor.rowcount > 0