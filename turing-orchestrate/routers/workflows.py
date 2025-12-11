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
import uuid
from datetime import datetime

router = APIRouter()


class WorkflowDTO(BaseModel):
    id: str
    tenant_id: str
    state: str
    selfie_session_id: Optional[str]
    id_session_id: Optional[str]
    risk_score: Optional[float]
    risk_band: Optional[str]
    decision: Optional[str]
    requires_human: bool
    data: dict

    class Config:
        from_attributes = True


class ManualDecisionRequest(BaseModel):
    decision: str
    reason: Optional[str] = None
    actor: str


@router.get("/workflows/{workflow_id}", response_model=WorkflowDTO)
async def get_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session),
):
    wf = await session.get(IdentityWorkflow, workflow_id)
    if not wf:
        raise HTTPException(404, "workflow not found")
    return wf


@router.get("/workflows", response_model=List[WorkflowDTO])
async def list_workflows(
    tenant_id: str,
    state: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(IdentityWorkflow).where(IdentityWorkflow.tenant_id == tenant_id)
    if state:
        stmt = stmt.where(IdentityWorkflow.state == state)
    stmt = stmt.order_by(IdentityWorkflow.created_at.desc()).limit(limit)

    result = await session.execute(stmt)
    workflows = result.scalars().all()
    return workflows


@router.post("/workflows/{workflow_id}/manual-decision")
async def set_manual_decision(
    workflow_id: str,
    body: ManualDecisionRequest,
    session: AsyncSession = Depends(get_session),
):
    wf = await session.get(IdentityWorkflow, workflow_id)
    if not wf:
        raise HTTPException(404, "workflow not found")

    md = ManualDecision(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        tenant_id=wf.tenant_id,
        decision=body.decision,
        reason=body.reason,
        actor=body.actor,
        created_at=datetime.utcnow(),
    )
    session.add(md)

    # Optionally update workflow state/decision
    wf.decision = body.decision
    wf.requires_human = False
    wf.state = "manual_decision"
    wf.updated_at = datetime.utcnow()

    await session.commit()

    return {"status": "ok"}
