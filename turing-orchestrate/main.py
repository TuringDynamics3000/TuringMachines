"""
TuringOrchestrate™ - Event-Driven Workflow Engine
==================================================

Identity verification orchestration with state machine and event routing.

Architecture:
- Event-driven: Receives events from TuringCapture
- State machine: Tracks workflow progression
- Risk integration: Calls TuringRiskBrain for decisions
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from event_router import router as event_router
from db import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("turing.orchestrate")


# ============================================================================
# FastAPI Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("=" * 60)
    logger.info("TuringOrchestrate™ Starting...")
    logger.info("=" * 60)
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Cleanup
    await close_db()
    logger.info("✅ Database connections closed")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="TuringOrchestrate™",
    description="Event-Driven Identity Verification Workflow Engine",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include event router
app.include_router(event_router, tags=["orchestration"])


# ============================================================================
# Health Endpoints
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "TuringOrchestrate",
        "version": "2.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "TuringOrchestrate™",
        "description": "Event-Driven Identity Verification Workflow Engine",
        "version": "2.0.0",
        "docs": "/docs",
    }


# ============================================================================
# Startup
# ============================================================================

logger.info("=" * 60)
logger.info("TuringOrchestrate™ Ready")
logger.info("Event Router: /v1/orchestrate/event")
logger.info("Workflow Status: /v1/orchestrate/workflow/{session_id}")
logger.info("=" * 60)
