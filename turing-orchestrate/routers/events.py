# turing-orchestrate/routers/events.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow_service import dispatch_event

router = APIRouter()


class OrchestrateEvent(BaseModel):
    """
    Event ingestion model.
    
    Supports both:
    - event: "selfie_uploaded" (legacy format)
    - event_type: "override.applied" (new format from Investigator UI)
    """
    event: Optional[str] = Field(None, description="Event type (legacy format)")
    event_type: Optional[str] = Field(None, description="Event type (new format)")
    payload: Dict[str, Any]
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")


@router.post("/event", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(ev: OrchestrateEvent):
    """
    Generic event ingestion endpoint.

    Called by:
      - TuringCapture (selfie_uploaded, match_completed)
      - TuringResolve Investigator UI (override.applied)
      - Internal systems (risk_evaluate)
    
    Accepts both event formats:
    - { "event": "selfie_uploaded", "payload": {...} }
    - { "event_type": "override.applied", "payload": {...} }
    """
    if "tenant_id" not in ev.payload:
        raise HTTPException(400, "payload.tenant_id is required")
    
    # Support both event and event_type fields
    event_type = ev.event_type or ev.event
    
    if not event_type:
        raise HTTPException(400, "Either 'event' or 'event_type' is required")
    
    # Normalize event type: convert dots to underscores
    # "override.applied" → "override_applied"
    normalized_event_type = event_type.replace(".", "_")
    
    # Build event dict for dispatcher
    event_dict = {
        "event": normalized_event_type,
        "payload": ev.payload,
        "correlation_id": ev.correlation_id
    }
    
    result = await dispatch_event(event_dict)
    return result
