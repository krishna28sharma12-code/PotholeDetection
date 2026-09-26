import os
import logging
import asyncpg
from typing import Optional

logger = logging.getLogger(__name__)

async def get_db_pool():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is not set")
    return await asyncpg.create_pool(dsn=db_url)

async def init_db(pool):
    """
    Run the DDL migration if the table doesn't exist.
    """
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id              SERIAL PRIMARY KEY,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
                captured_at     TIMESTAMPTZ NOT NULL,           
                latitude        DOUBLE PRECISION NOT NULL,
                longitude       DOUBLE PRECISION NOT NULL,
                severity        TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
                confidence      REAL NOT NULL,
                bbox_area_pct   REAL,                           
                normal_image    TEXT NOT NULL,                  
                annotated_image TEXT NOT NULL                   
            );
            
            CREATE INDEX IF NOT EXISTS idx_detections_created_at ON detections (created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_detections_severity ON detections (severity);
        """)
        logger.info("Database initialized.")

async def insert_detection(
    pool,
    captured_at: str,
    latitude: float,
    longitude: float,
    severity: str,
    confidence: float,
    bbox_area_pct: Optional[float],
    normal_image: str,
    annotated_image: str
) -> int:
    """
    Inserts a new detection row and returns the inserted ID.
    """
    query = """
        INSERT INTO detections (
            captured_at, latitude, longitude, severity, confidence, 
            bbox_area_pct, normal_image, annotated_image
        ) VALUES (
            $1::timestamptz, $2, $3, $4, $5, $6, $7, $8
        ) RETURNING id;
    """
    async with pool.acquire() as conn:
        row_id = await conn.fetchval(
            query,
            captured_at,
            latitude,
            longitude,
            severity,
            confidence,
            bbox_area_pct,
            normal_image,
            annotated_image
        )
        return row_id

async def get_results(pool, severity: Optional[str] = None, since: Optional[str] = None, limit: Optional[int] = None) -> list:
    """
    Fetches detections with optional filters.
    """
    query = "SELECT id, captured_at, latitude, longitude, severity, confidence, annotated_image FROM detections WHERE 1=1"
    args = []
    
    if severity:
        args.append(severity)
        query += f" AND severity = ${len(args)}"
        
    if since:
        from datetime import datetime
        try:
            parsed_since = datetime.fromisoformat(since.replace('Z', '+00:00'))
            args.append(parsed_since)
            query += f" AND captured_at >= ${len(args)}"
        except Exception:
            pass # Ignore invalid format for since

    query += " ORDER BY created_at DESC"
    
    if limit:
        args.append(limit)
        query += f" LIMIT ${len(args)}"

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]

async def get_result_by_id(pool, detection_id: int) -> Optional[dict]:
    """
    Fetches a single detection by ID.
    """
    query = "SELECT id, captured_at, latitude, longitude, severity, confidence, bbox_area_pct, normal_image, annotated_image FROM detections WHERE id = $1"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, detection_id)
        if row:
            return dict(row)
        return None
