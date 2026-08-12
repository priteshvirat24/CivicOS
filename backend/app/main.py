from fastapi import FastAPI
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CivicOS Agent Runtime & API",
    description="Backend API and Agent Orchestrator for CivicOS",
    version="0.1.0",
)

from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import prs, agents, activity, dataset, demo

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prs.router)
app.include_router(agents.router)
app.include_router(activity.router)
app.include_router(dataset.router)
app.include_router(demo.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up CivicOS Agent Runtime...")
    from app.agents.orchestrator import setup_orchestrator
    setup_orchestrator()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "CivicOS Agent Runtime is active"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/healthz")
def liveness_probe():
    """Kubernetes liveness probe"""
    return {"status": "ok"}

@app.get("/api/readiness")
async def readiness_probe():
    """Kubernetes readiness probe checking database connection"""
    from app.db.database import engine
    try:
        # Check DB connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service Unavailable")
