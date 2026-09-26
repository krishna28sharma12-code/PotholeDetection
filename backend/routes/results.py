from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from typing import Optional
from backend.services.db import get_results, get_result_by_id

router = APIRouter()

@router.get("/api/results")
async def fetch_results(
    request: Request,
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    since: Optional[str] = Query(None, description="ISO 8601 timestamp string"),
    limit: Optional[int] = Query(None, description="Limit rows returned")
):
    pool = request.app.state.db_pool
    rows = await get_results(pool, severity=severity, since=since, limit=limit)
    
    # We need to ensure date objects are converted to strings
    # asyncpg datetime objects might not be directly serialized by FastAPI if wrapped in dicts
    # FastAPI usually handles it when returning pydantic models, but with raw dicts we might need to convert
    results = []
    for r in rows:
        r["captured_at"] = r["captured_at"].isoformat() if r.get("captured_at") else None
        # Rename lat/lon to match API spec
        r["lat"] = r.pop("latitude")
        r["lon"] = r.pop("longitude")
        results.append(r)
        
    return results

@router.get("/api/results/{id}")
async def fetch_result_by_id(request: Request, id: int):
    pool = request.app.state.db_pool
    row = await get_result_by_id(pool, id)
    if not row:
        return JSONResponse(status_code=404, content={"error": "Detection not found"})
        
    row["captured_at"] = row["captured_at"].isoformat() if row.get("captured_at") else None
    row["lat"] = row.pop("latitude")
    row["lon"] = row.pop("longitude")
    
    return row
