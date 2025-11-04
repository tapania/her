"""
Add logbook_path column to existing memories table.

Run this once to migrate existing database.
"""

import asyncio
import aiosqlite
from pathlib import Path


async def add_logbook_column():
    """Add logbook_path column to memories table."""
    db_path = Path.home() / ".sable" / "consciousness.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return

    conn = await aiosqlite.connect(db_path)

    try:
        # Check if column already exists
        cursor = await conn.execute("PRAGMA table_info(memories)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "logbook_path" in column_names:
            print("✓ logbook_path column already exists")
            return

        # Add the column
        await conn.execute("""
            ALTER TABLE memories
            ADD COLUMN logbook_path TEXT
        """)
        await conn.commit()

        print("✓ Added logbook_path column to memories table")

    except Exception as e:
        print(f"✗ Error: {e}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_logbook_column())
