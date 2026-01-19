from typing import Optional, Union, List
import asyncpg
from datetime import datetime


class Database:
    def __init__(self, dsn: str):
        """
        Database wrapper for async PostgreSQL operations.

        :param dsn: PostgreSQL connection string
        """
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

    # ===================== CONNECTION =====================

    async def connect(self):
        """Create a connection pool to the database"""
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def disconnect(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()

    # ===================== CORE EXECUTOR =====================

    async def execute(
        self,
        query: str,
        *args,
        fetch: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ) -> Union[List[asyncpg.Record], asyncpg.Record, str, None]:
        """
        Universal SQL executor.

        Use flags to define expected result:
        - fetch=True     → returns list of rows
        - fetchrow=True  → returns single row
        - execute=True   → executes query without returning rows
        """
        async with self.pool.acquire() as conn:
            if fetch:
                return await conn.fetch(query, *args)
            elif fetchrow:
                return await conn.fetchrow(query, *args)
            elif execute:
                return await conn.execute(query, *args)
        return None

    # ===================== TABLE CREATION =====================

    async def create_tables(self):
        """Create all required tables if they do not exist"""

        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name TEXT,
                username TEXT,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            execute=True,
        )

        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name TEXT,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            execute=True,
        )

        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS calculations (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                coord_a TEXT NOT NULL,
                coord_b TEXT NOT NULL,
                segments INT NOT NULL,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            execute=True,
        )

    # ===================== USERS =====================

    async def add_user(
        self,
        telegram_id: int,
        full_name: str,
        username: Optional[str] = None,
    ):
        """Insert a new user if not exists"""
        query = """
            INSERT INTO users (telegram_id, full_name, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING;
        """
        await self.execute(query, telegram_id, full_name, username, execute=True)

    async def get_user(self, telegram_id: int):
        """Get user by Telegram ID"""
        query = "SELECT * FROM users WHERE telegram_id = $1;"
        return await self.execute(query, telegram_id, fetchrow=True)

    async def get_users_count(self) -> int:
        """Return total number of users"""
        query = "SELECT COUNT(*) AS count FROM users;"
        row = await self.execute(query, fetchrow=True)
        return row["count"] if row else 0

    # ===================== ADMINS =====================

    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user is an admin"""
        query = "SELECT EXISTS(SELECT 1 FROM admins WHERE telegram_id = $1);"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, telegram_id)

    async def add_admin(
        self,
        telegram_id: int,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
    ):
        """Add new admin (if not exists)"""
        query = """
            INSERT INTO admins (telegram_id, full_name, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING;
        """
        await self.execute(query, telegram_id, full_name, username, execute=True)

    # ===================== CALCULATIONS =====================

    async def add_calculation(
        self,
        user_id: int,
        coord_a: str,
        coord_b: str,
        segments: int,
        result: str,
    ):
        """Save calculation result"""
        query = """
            INSERT INTO calculations (user_id, coord_a, coord_b, segments, result)
            VALUES ($1, $2, $3, $4, $5);
        """
        await self.execute(
            query,
            user_id,
            coord_a,
            coord_b,
            segments,
            result,
            execute=True,
        )

    async def get_last_calculations(self, user_id: int, limit: int = 3):
        """Get last N calculation results for a user"""
        query = """
            SELECT result
            FROM calculations
            WHERE user_id = $1
            ORDER BY id DESC
            LIMIT $2;
        """
        return await self.execute(query, user_id, limit, fetch=True)

    # ===================== UTILS =====================

    async def drop_table(self, table_name: str):
        """
        Drop a table (admin-only operation).
        ⚠️ Dangerous operation!
        """
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        async with self.pool.acquire() as conn:
            await conn.execute(query)

        print(f"🗑 Table dropped: {table_name}")
