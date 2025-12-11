# turing-orchestrate/routers/events.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow_service import dispatch_event

router = APIRouter()


class OrchestrateEvent(BaseModel):
    event: str = Field(..., description="Event type, e.g. selfie_uploaded")
    payload: Dict[str, Any]


@router.post("/event", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(ev: OrchestrateEvent):
    """
    Generic event ingestion endpoint.

    Called by:
      - TuringCapture (selfie_uploaded, match_completed)
      - Internal systems (risk_evaluate)
    """
    if "tenant_id" not in ev.payload:
        raise HTTPException(400, "payload.tenant_id is required")

    result = await dispatch_event(ev.model_dump())
    return result
