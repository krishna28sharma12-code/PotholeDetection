import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from backend.routes import upload, results
from backend.services.db import get_db_pool, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    try:
        pool = await get_db_pool()
        app.state.db_pool = pool
        await init_db(pool)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # We don't raise here so the app can start even if DB is misconfigured (for testing)
        # But in production you might want it to fail
    yield
    # Shutdown
    logger.info("Shutting down application...")
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.close()

app = FastAPI(title="Pothole Detection API", lifespan=lifespan)

# Enable CORS for phone client and dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(results.router)

# Mount static files
app.mount("/capture", StaticFiles(directory="static/capture", html=True), name="capture")
app.mount("/dashboard", StaticFiles(directory="static/dashboard", html=True), name="dashboard")

@app.get("/api/health")
async def health_check():
    """
    Uptime/warm-up check
    """
    return {"status": "ok"}

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")
