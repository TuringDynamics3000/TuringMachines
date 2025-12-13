# turing-orchestrate/main.py

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from db import init_db, close_db
from routers.events import router as events_router
from routers.workflows import router as workflows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("=" * 60)
    print("TuringOrchestrateâ„¢ Starting...")
    print("=" * 60)
    
    await init_db()
    print("âœ… Database initialized")
    
    yield
    
    await close_db()
    print("âœ… Database connections closed")


app = FastAPI(
    title="TuringOrchestrate",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(events_router, prefix="/v1/orchestrate", tags=["events"])
app.include_router(workflows_router, prefix="/v1/orchestrate", tags=["workflows"])
app.include_router(investigator_decisions.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "TuringOrchestrateâ„¢",
        "description": "Event-Driven Identity Verification Workflow Engine",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "TuringOrchestrate",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8102, reload=True)
