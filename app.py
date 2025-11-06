from fastapi import FastAPI
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Telegram Bot Analytics API")


async def get_connection():
    return await asyncpg.connect(DB_URL)


@app.get("/top_objects")
async def top_objects(limit: int = 10):
    conn = await get_connection()
    rows = await conn.fetch(
        """
        SELECT object, COUNT(*) AS complaints
        FROM reports
        GROUP BY object
        ORDER BY complaints DESC
        LIMIT $1
        """,
        limit
    )
    await conn.close()
    return [{"object": r["object"], "complaints": r["complaints"]} for r in rows]


@app.get("/priority_distribution")
async def priority_distribution():

    conn = await get_connection()
    rows = await conn.fetch(
        """
        SELECT priority, COUNT(*) AS count
        FROM reports
        GROUP BY priority
        ORDER BY count DESC
        """
    )
    await conn.close()
    return {r["priority"]: r["count"] for r in rows}


@app.get("/aspect_frequency")
async def aspect_frequency():

    conn = await get_connection()
    rows = await conn.fetch(
        """
        SELECT aspect, COUNT(*) AS count
        FROM reports
        GROUP BY aspect
        ORDER BY count DESC
        """
    )
    await conn.close()
    return {r["aspect"]: r["count"] for r in rows}
