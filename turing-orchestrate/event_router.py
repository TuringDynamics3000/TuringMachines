"""
TuringOrchestrate™ Event Router
================================

Handles incoming events from TuringCapture and other services,
routing them to appropriate workflow state transitions.

Events:
- selfie_uploaded: Selfie received with liveness check
- embeddings_ready: Face embeddings generated
- id_uploaded: ID document uploaded
- match_completed: Face matching completed
"""

import logging
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from db import get_session
from workflow import transition

# Configure logging
logger = logging.getLogger("turing.orchestrate")
logger.setLevel(logging.INFO)

# RiskBrain integration
RISK_URL = os.getenv("RISK_URL", "http://localhost:8103")

# Create router
router = APIRouter(prefix="/v1/orchestrate")


class EventRequest(BaseModel):
    """Event notification from external services."""
    event: str
    payload: Dict[str, Any]


@router.post("/event")
async def handle_event(request: EventRequest):
    """
    Handle incoming event and transition workflow state.
    
    Args:
        request: Event with type and payload
    
    Returns:
        Status response
    """
    event_type = request.event
    payload = request.payload
    
    logger.info(f"📨 Received event: {event_type}")
    
    # Extract session_id from payload
    session_id = (
        payload.get("session_id") or
        payload.get("selfie_session_id")  # For match events
    )
    
    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Missing session_id in payload"
        )
    
    # Route event to appropriate handler
    async with get_session() as db:
        if event_type == "selfie_uploaded":
            await handle_selfie_uploaded(db, session_id, payload)
        
        elif event_type == "embeddings_ready":
            await handle_embeddings_ready(db, session_id, payload)
        
        elif event_type == "id_uploaded":
            await handle_id_uploaded(db, session_id, payload)
        
        elif event_type == "match_completed":
            await handle_match_completed(db, session_id, payload)
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown event type: {event_type}"
            )
    
    logger.info(f"✅ Event processed: {event_type} for session {session_id}")
    
    return {
        "status": "ok",
        "processed": event_type,
        "session_id": session_id,
    }


async def handle_selfie_uploaded(db, session_id: str, payload: Dict[str, Any]):
    """Handle selfie_uploaded event."""
    await transition(db, session_id, "selfie_uploaded", payload)
    logger.info(f"  → State: selfie_uploaded")


async def handle_embeddings_ready(db, session_id: str, payload: Dict[str, Any]):
    """Handle embeddings_ready event."""
    # Update workflow data with embedding info
    await transition(db, session_id, "selfie_uploaded", {
        "embeddings": {
            "mobile_dim": payload.get("mobile_dim"),
            "arc_dim": payload.get("arc_dim"),
        }
    })
    logger.info(f"  → Embeddings ready: {payload.get('mobile_dim')}D + {payload.get('arc_dim')}D")


async def handle_id_uploaded(db, session_id: str, payload: Dict[str, Any]):
    """Handle id_uploaded event."""
    await transition(db, session_id, "id_uploaded", payload)
    logger.info(f"  → State: id_uploaded")


async def call_riskbrain(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Call TuringRiskBrain for risk assessment."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{RISK_URL}/v1/risk/evaluate",
                json=payload
            )
            resp.raise_for_status()
            risk_result = resp.json()
            logger.info(f"  🧠 RiskBrain: {risk_result.get('decision', 'unknown')} (score: {risk_result.get('score', 0):.3f})")
            return risk_result
    except Exception as e:
        logger.warning(f"  ⚠️  RiskBrain unavailable: {e}")
        return {"error": "riskbrain_unavailable", "decision": "manual_review"}


async def handle_match_completed(db, session_id: str, payload: Dict[str, Any]):
    """Handle match_completed event."""
    is_match = payload.get("match", False)
    
    # Call RiskBrain for risk assessment
    risk_result = await call_riskbrain(payload)
    
    # Determine new state based on match result
    new_state = "verified_match" if is_match else "verified_no_match"
    
    # Merge risk results into payload
    enhanced_payload = {
        **payload,
        "risk": risk_result,
    }
    
    await transition(db, session_id, new_state, enhanced_payload)
    logger.info(f"  → State: {new_state} (score: {payload.get('fused_score', 0):.3f})")
    
    # Log risk decision
    if risk_result:
        decision = risk_result.get("decision", "unknown")
        logger.info(f"  → Risk Decision: {decision}")


@router.get("/workflow/{session_id}")
async def get_workflow_status(session_id: str):
    """
    Get current workflow status.
    
    Args:
        session_id: Workflow session ID
    
    Returns:
        Workflow details
    """
    from workflow import get_workflow
    
    async with get_session() as db:
        wf = await get_workflow(db, session_id)
        
        if not wf:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow not found: {session_id}"
            )
        
        return {
            "session_id": wf.session_id,
            "state": wf.state,
            "tenant_id": wf.tenant_id,
            "created_at": wf.created_at.isoformat() if wf.created_at else None,
            "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
            "liveness_score": wf.liveness_score,
            "is_live": wf.is_live,
            "match_score": wf.match_score,
            "is_match": wf.is_match,
            "risk_score": wf.risk_score,
            "risk_decision": wf.risk_decision,
            "data": wf.data,
        }


@router.get("/workflows")
async def list_workflows(tenant_id: str = None, state: str = None, limit: int = 100):
    """
    List workflows with optional filters.
    
    Args:
        tenant_id: Filter by tenant
        state: Filter by state
        limit: Maximum results
    
    Returns:
        List of workflows
    """
    from workflow import list_workflows as list_wf
    
    async with get_session() as db:
        workflows = await list_wf(db, tenant_id=tenant_id, state=state, limit=limit)
        
        return {
            "count": len(workflows),
            "workflows": [
                {
                    "session_id": wf.session_id,
                    "state": wf.state,
                    "tenant_id": wf.tenant_id,
                    "created_at": wf.created_at.isoformat() if wf.created_at else None,
                    "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
                    "is_live": wf.is_live,
                    "is_match": wf.is_match,
                }
                for wf in workflows
            ]
        }
