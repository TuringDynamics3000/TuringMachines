# turing-orchestrate/routers/workflows.py

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import get_session
from models import IdentityWorkflow, ManualDecision
from workflow_service import get_latest_decision

import uuid
from datetime import datetime

router = APIRouter()


class ManualDecisionBody(BaseModel):
    decision: str
    reason: Optional[str] = None


@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str, session: AsyncSession = Depends(get_session)):
    """
    🔒 DECISION AUTHORITY: Read decision from decision.finalised events.
    
    This endpoint now reads the latest decision from decision.finalised events,
    not from the wf.decision database column.
    """
    stmt = select(IdentityWorkflow).where(IdentityWorkflow.id == workflow_id)
    result = await session.execute(stmt)
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(404, "workflow not found")

    # 🔒 Read decision from decision.finalised event (single source of truth)
    latest_decision = await get_latest_decision(session, workflow_id)
    
    # Extract decision details from event
    decision_outcome = None
    decision_confidence = None
    decision_requires_human = None
    
    if latest_decision:
        decision_outcome = latest_decision.get("decision", {}).get("outcome")
        decision_confidence = latest_decision.get("decision", {}).get("confidence")
        decision_requires_human = latest_decision.get("decision", {}).get("requires_human")

    return {
        "id": wf.id,
        "tenant_id": wf.tenant_id,
        "state": wf.state,
        
        # 🔒 Decision from decision.finalised event (not wf.decision)
        "decision": decision_outcome,
        "decision_confidence": decision_confidence,
        "requires_human": decision_requires_human,
        
        # Risk info (still from workflow for now)
        "risk_score": wf.risk_score,
        "risk_band": wf.risk_band,
        
        "data": wf.data,
        "created_at": wf.created_at.isoformat() if wf.created_at else None,
        "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
        
        # Include latest decision event for full context
        "latest_decision_event": latest_decision,
    }


@router.post("/workflow/{workflow_id}/manual-decision")
async def apply_manual_decision(
    workflow_id: str,
    body: ManualDecisionBody,
    session: AsyncSession = Depends(get_session)
):
    """
    Apply a manual decision override.
    
    Note: This still writes to wf.decision for backward compatibility,
    but the override handler will emit a new decision.finalised event.
    """
    stmt = select(IdentityWorkflow).where(IdentityWorkflow.id == workflow_id)
    result = await session.execute(stmt)
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(404, "workflow not found")

    # Store the manual decision
    manual_dec = ManualDecision(
        id=f"md_{uuid.uuid4().hex[:12]}",
        workflow_id=workflow_id,
        decision=body.decision,
        reason=body.reason,
        decided_by="manual_reviewer",
        decided_at=datetime.utcnow()
    )
    session.add(manual_dec)

    # Update workflow (for backward compatibility)
    wf.decision = body.decision
    wf.state = "manual_decision_applied"
    wf.updated_at = datetime.utcnow()

    await session.commit()

    return {"status": "ok", "decision_id": manual_dec.id}


@router.get("/workflow/{workflow_id}/decisions")
async def get_workflow_decisions(
    workflow_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all manual decisions for a workflow.
    """
    stmt = select(ManualDecision).where(ManualDecision.workflow_id == workflow_id)
    result = await session.execute(stmt)
    decisions = result.scalars().all()

    return [
        {
            "id": d.id,
            "decision": d.decision,
            "reason": d.reason,
            "decided_by": d.decided_by,
            "decided_at": d.decided_at.isoformat() if d.decided_at else None,
        }
        for d in decisions
    ]
