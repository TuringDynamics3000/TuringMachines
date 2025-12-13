# turing-orchestrate/routers/investigator/decisions.py
"""
🔒 DECISION TIMELINE API

Purpose:
Expose the authoritative decision timeline to the Investigator UI.
Reads only from decision.finalised events.

Authority guarantee:
This endpoint cannot lie unless the DB is corrupted.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db import async_session
from models import WorkflowEvent

router = APIRouter(prefix="/v1/investigator", tags=["investigator"])

DECISION_EVENT = "decision.finalised"


@router.get("/workflows/{workflow_id}/decisions")
async def get_decision_timeline(workflow_id: str) -> Dict[str, Any]:
    """
    🔒 DECISION TIMELINE: Authoritative decision history for a workflow.
    
    Returns all decision.finalised events in chronological order.
    
    Use cases:
    - Investigator UI showing decision history
    - Audit trail for compliance
    - Override tracking with lineage
    
    Authority guarantee:
    - Reads ONLY from decision.finalised events
    - Cannot return decisions that weren't emitted
    - Chronological order preserved
    """
    async with async_session() as session:
        result = await session.execute(
            select(WorkflowEvent)
            .where(
                WorkflowEvent.workflow_id == workflow_id,
                WorkflowEvent.event_type == DECISION_EVENT
            )
            .order_by(WorkflowEvent.created_at.asc())
        )
        events = result.scalars().all()

    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"No decisions found for workflow {workflow_id}"
        )

    decisions = []
    for e in events:
        p = e.data  # Use .data instead of .payload based on our model
        
        decisions.append({
            "decision_id": p.get("decision_id"),
            "timestamp": e.created_at.isoformat() if e.created_at else None,
            "outcome": p.get("decision", {}).get("outcome"),
            "confidence": p.get("decision", {}).get("confidence"),
            "requires_human": p.get("decision", {}).get("requires_human"),
            "can_proceed": p.get("decision", {}).get("can_proceed"),
            
            "policy": p.get("policy"),
            "reason_codes": p.get("reason_codes", []),
            "risk_summary": p.get("risk_summary"),
            
            "authority": {
                "decided_by": p.get("authority", {}).get("decided_by"),
                "service_version": p.get("authority", {}).get("service_version"),
                "is_override": p.get("authority", {}).get("override", False)
            },
            
            "lineage": p.get("lineage"),
            
            "subject": p.get("subject"),
        })

    # Determine current decision (latest in timeline)
    current_decision = decisions[-1] if decisions else None

    return {
        "workflow_id": workflow_id,
        "decision_count": len(decisions),
        "current_decision": current_decision,
        "timeline": decisions,
        "has_overrides": any(d["authority"]["is_override"] for d in decisions)
    }


@router.get("/workflows/{workflow_id}/decisions/current")
async def get_current_decision(workflow_id: str) -> Dict[str, Any]:
    """
    🔒 CURRENT DECISION: Get the latest authoritative decision.
    
    Convenience endpoint that returns only the most recent decision.
    """
    async with async_session() as session:
        result = await session.execute(
            select(WorkflowEvent)
            .where(
                WorkflowEvent.workflow_id == workflow_id,
                WorkflowEvent.event_type == DECISION_EVENT
            )
            .order_by(WorkflowEvent.created_at.desc())
        )
        latest_event = result.scalars().first()

    if not latest_event:
        raise HTTPException(
            status_code=404,
            detail=f"No decision found for workflow {workflow_id}"
        )

    p = latest_event.data
    
    return {
        "workflow_id": workflow_id,
        "decision_id": p.get("decision_id"),
        "timestamp": latest_event.created_at.isoformat() if latest_event.created_at else None,
        "outcome": p.get("decision", {}).get("outcome"),
        "confidence": p.get("decision", {}).get("confidence"),
        "requires_human": p.get("decision", {}).get("requires_human"),
        "can_proceed": p.get("decision", {}).get("can_proceed"),
        "policy": p.get("policy"),
        "reason_codes": p.get("reason_codes", []),
        "risk_summary": p.get("risk_summary"),
        "authority": p.get("authority"),
        "lineage": p.get("lineage"),
        "subject": p.get("subject"),
    }
