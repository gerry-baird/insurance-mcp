import aiosqlite
import os
from typing import Optional
from datetime import date, timedelta

DATABASE_PATH = "insurance.db"


async def get_database() -> aiosqlite.Connection:
    """Get database connection."""
    return aiosqlite.connect(DATABASE_PATH)


async def init_database():
    """Initialize the database with required tables."""
    async with await get_database() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                product TEXT NOT NULL,
                premium TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sample_data_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_date TEXT NOT NULL,
                customer_count INTEGER NOT NULL,
                policy_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def init_sample_data():
    """Always reinitialize the database with fresh sample customer and policy data."""
    async with await get_database() as db:
        # Clear existing data
        await db.execute("DELETE FROM policies")
        await db.execute("DELETE FROM customers")
        await db.execute("DELETE FROM sample_data_log")
        
        # Reset auto-increment counters
        await db.execute("DELETE FROM sqlite_sequence WHERE name IN ('customers', 'policies', 'sample_data_log')")
        
        # Insert sample customers
        sample_customers = [
            ("John Smith", "1985-06-15", "john.smith@email.com", "123 Main St", "California"),
            ("Sarah Johnson", "1990-03-22", "sarah.johnson@email.com", "456 Oak Ave", "Texas"),
            ("Michael Brown", "1978-11-08", "michael.brown@email.com", "789 Pine Rd", "New York"),
            ("Emily Davis", "1995-01-30", "emily.davis@email.com", "321 Elm St", "Florida"),
            ("David Wilson", "1982-09-12", "david.wilson@email.com", "654 Maple Dr", "Illinois"),
            ("Jessica Martinez", "1987-04-12", "jessica.martinez@email.com", "789 Houston St", "Texas"),
            ("Robert Garcia", "1992-08-25", "robert.garcia@email.com", "234 Austin Ave", "Texas"),
            ("Amanda Rodriguez", "1979-12-03", "amanda.rodriguez@email.com", "567 Dallas Blvd", "Texas"),
            ("Christopher Lee", "1988-01-18", "christopher.lee@email.com", "890 San Antonio Way", "Texas"),
            ("Michelle Thompson", "1993-07-07", "michelle.thompson@email.com", "345 Fort Worth Dr", "Texas"),
            ("James Anderson", "1984-11-29", "james.anderson@email.com", "678 Cedar St", "Iowa"),
            ("Lisa White", "1991-05-14", "lisa.white@email.com", "901 Oak Hill Rd", "Iowa"),
            ("Daniel Miller", "1986-09-22", "daniel.miller@email.com", "432 Prairie View Dr", "Iowa")
        ]
        
        await db.executemany("""
            INSERT INTO customers (name, date_of_birth, email, address, state)
            VALUES (?, ?, ?, ?, ?)
        """, sample_customers)
        
        # Calculate policy dates based on current date
        today = date.today()
        
        # Create sample policies with start dates in the past (within 360 days)
        policy_offsets = [
            (1, -30, "bicycle", "450.00"),     # Started 30 days ago
            (1, -45, "pet", "320.00"),         # Started 45 days ago
            (2, -60, "boat", "1250.00"),       # Started 60 days ago
            (2, -90, "RV", "2100.00"),         # Started 90 days ago
            (3, -120, "equine", "890.00"),     # Started 120 days ago
            (3, -150, "bicycle", "380.00"),    # Started 150 days ago
            (4, -15, "pet", "295.00"),         # Started 15 days ago
            (5, -75, "boat", "1450.00"),       # Started 75 days ago
            (5, -100, "equine", "950.00"),     # Started 100 days ago
            (6, -180, "RV", "1980.00"),        # Started 180 days ago
            (6, -200, "pet", "275.00"),        # Started 200 days ago
            (7, -5, "bicycle", "425.00"),      # Started 5 days ago
            (7, -220, "boat", "1320.00"),      # Started 220 days ago
            (8, -240, "equine", "825.00"),     # Started 240 days ago
            (9, -25, "pet", "340.00"),         # Started 25 days ago
            (9, -270, "bicycle", "395.00"),    # Started 270 days ago
            (10, -50, "boat", "1380.00"),      # Started 50 days ago
            (11, -300, "RV", "2250.00"),       # Started 300 days ago
            (11, -320, "equine", "780.00"),    # Started 320 days ago
            (12, -80, "pet", "310.00"),        # Started 80 days ago
            (13, -350, "bicycle", "460.00"),   # Started 350 days ago
            (13, -360, "boat", "1520.00")      # Started 360 days ago
      ]
        
        sample_policies = []
        for customer_id, start_offset, product, premium in policy_offsets:
            start_date = today + timedelta(days=start_offset)
            end_date = start_date + timedelta(days=364)  # 364-day policies
            sample_policies.append((customer_id, start_date.isoformat(), end_date.isoformat(), product, premium))
        
        # Add special policy for customer 2: started 344 days ago, ends 20 days in future
        special_start = today + timedelta(days=-344)
        special_end = today + timedelta(days=20)
        sample_policies.append((2, special_start.isoformat(), special_end.isoformat(), "pet", "380.00"))

        # Add special policy for customer 6: started 344 days ago, ends 20 days in future
        special_start = today + timedelta(days=-354)
        special_end = today + timedelta(days=10)
        sample_policies.append((6, special_start.isoformat(), special_end.isoformat(), "boat", "450.00"))
        
        await db.executemany("""
            INSERT INTO policies (customer_id, start_date, end_date, product, premium)
            VALUES (?, ?, ?, ?, ?)
        """, sample_policies)
        
        # Record sample data generation info
        await db.execute("""
            INSERT INTO sample_data_log (generation_date, customer_count, policy_count)
            VALUES (?, ?, ?)
        """, (today.isoformat(), len(sample_customers), len(sample_policies)))
        
        await db.commit()


async def ensure_fresh_sample_data():
    """Check if sample data was generated today, regenerate if not."""
    today = date.today()
    async with await get_database() as db:
        cursor = await db.execute("""
            SELECT generation_date FROM sample_data_log 
            ORDER BY created_at DESC LIMIT 1
        """)
        row = await cursor.fetchone()
        
        if row is None:
            # No sample data exists, generate it
            await init_sample_data()
        else:
            last_generation_date = date.fromisoformat(row[0])
            if last_generation_date < today:
                # Sample data is outdated, regenerate it
                await init_sample_data()


async def close_database():
    """Close database connections (for cleanup)."""
    # aiosqlite handles connection cleanup automatically
    pass