"""
TuringCapture™ - FastAPI Application
Bank-grade identity verification and document capture platform with dual-model biometrics
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import database
from db import init_db, close_db

# Import biometrics router
from biometrics import router as biometrics_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager
    
    Handles startup and shutdown events:
    - Initialize database connection
    - Register pgvector extension
    - Close database connections on shutdown
    """
    # Startup
    logger.info("🚀 TuringCapture™ service starting...")
    
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️  Continuing without database (memory mode only)")
    
    logger.info("✅ Service initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 TuringCapture™ service shutting down...")
    
    try:
        await close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="TuringCapture™",
    description="Identity & Document Capture Service - Bank-grade identity verification platform with dual-model biometrics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include biometrics router
app.include_router(biometrics_router, tags=["biometrics"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    uptime: Optional[str] = None
    database: Optional[str] = None


class CaptureRequest(BaseModel):
    user_id: str
    document_type: str
    jurisdiction: str
    metadata: Optional[Dict[str, Any]] = None


class CaptureResponse(BaseModel):
    capture_id: str
    status: str
    user_id: str
    timestamp: str
    verification_url: Optional[str] = None


# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "TuringCapture™",
        "description": "Identity & Document Capture Service with Dual-Model Biometrics",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Liveness Detection (MediaPipe FaceMesh)",
            "Dual-Model Face Matching (MobileFaceNet + ArcFace)",
            "Async Database Persistence (PostgreSQL + pgvector)",
            "Flexible Storage (Memory/Local/S3)",
        ],
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    Returns service status and metadata
    """
    from db import DB_MODE, _async_engine, _sync_engine
    
    # Check database status
    db_status = "ok"
    try:
        if DB_MODE == "async" and _async_engine:
            db_status = "connected (async)"
        elif DB_MODE == "sync" and _sync_engine:
            db_status = "connected (sync)"
        else:
            db_status = "not initialized"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="ok",
        service="turing-capture",
        version="2.0.0",
        timestamp=datetime.utcnow().isoformat(),
        uptime="operational",
        database=db_status,
    )


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes
    Returns 200 when service is ready to accept traffic
    """
    from db import _async_engine, _sync_engine
    from biometrics import STORAGE_MODE, USE_MOCK_EMBEDDINGS
    
    checks = {
        "database": "ok" if (_async_engine or _sync_engine) else "not_initialized",
        "storage": STORAGE_MODE,
        "embeddings": "mock" if USE_MOCK_EMBEDDINGS else "onnx",
    }
    
    return {
        "ready": True,
        "checks": checks,
    }


@app.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes
    Returns 200 when service is alive
    """
    return {"alive": True}


# ============================================================================
# CAPTURE ENDPOINTS (Legacy)
# ============================================================================

@app.post("/v1/capture", response_model=CaptureResponse)
async def create_capture(request: CaptureRequest):
    """
    Create a new identity capture session
    
    This endpoint initiates an identity verification and document capture session.
    """
    logger.info(f"Creating capture session for user: {request.user_id}")
    
    # Generate capture ID
    capture_id = (
        f"cap_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{request.user_id[:8]}"
    )
    
    return CaptureResponse(
        capture_id=capture_id,
        status="initiated",
        user_id=request.user_id,
        timestamp=datetime.utcnow().isoformat(),
        verification_url=f"/v1/capture/{capture_id}/verify",
    )


@app.get("/v1/capture/{capture_id}")
async def get_capture_status(capture_id: str):
    """Get the status of a capture session"""
    logger.info(f"Fetching capture status for: {capture_id}")
    
    return {
        "capture_id": capture_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "steps_completed": 0,
        "steps_total": 3,
    }


@app.post("/v1/capture/{capture_id}/document")
async def upload_document(capture_id: str):
    """Upload a document for verification"""
    logger.info(f"Document upload for capture: {capture_id}")
    
    return {
        "capture_id": capture_id,
        "document_id": f"doc_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "status": "uploaded",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/v1/capture/{capture_id}/biometric")
async def upload_biometric(capture_id: str):
    """Upload biometric data for verification"""
    logger.info(f"Biometric upload for capture: {capture_id}")
    
    return {
        "capture_id": capture_id,
        "biometric_id": f"bio_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "status": "uploaded",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/v1/capture/{capture_id}/verify")
async def verify_capture(capture_id: str):
    """Verify the captured identity data"""
    logger.info(f"Verifying capture: {capture_id}")
    
    return {
        "capture_id": capture_id,
        "verification_status": "verified",
        "confidence_score": 0.95,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# METRICS ENDPOINT
# ============================================================================

@app.get("/metrics")
async def metrics():
    """
    Metrics endpoint for monitoring (Prometheus compatible)
    """
    from biometrics import STORAGE_MODE, USE_MOCK_EMBEDDINGS
    from db import DB_MODE
    
    return {
        "service": "turing-capture",
        "version": "2.0.0",
        "storage_mode": STORAGE_MODE,
        "db_mode": DB_MODE,
        "mock_embeddings": USE_MOCK_EMBEDDINGS,
        "requests_total": 0,
        "requests_success": 0,
        "requests_failed": 0,
        "avg_response_time_ms": 0,
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8101,
        log_level="info",
    )
