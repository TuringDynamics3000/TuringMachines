"""
TuringOrchestrate™ Workflow State Machine
==========================================

State transition logic for identity verification workflows.

State Flow:
pending → selfie_uploaded → id_uploaded → verified_match/verified_no_match → complete
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models import IdentityWorkflow


async def transition(
    session: AsyncSession,
    session_id: str,
    new_state: str,
    extra: Optional[Dict[str, Any]] = None
) -> IdentityWorkflow:
    """
    Transition a workflow to a new state.
    
    Args:
        session: Database session
        session_id: Workflow session ID
        new_state: Target state
        extra: Additional data to merge into workflow.data
    
    Returns:
        Updated IdentityWorkflow object
    """
    # Try to get existing workflow
    wf = await session.get(IdentityWorkflow, session_id)
    
    if not wf:
        # Create new workflow
        wf = IdentityWorkflow(
            session_id=session_id,
            state=new_state,
            tenant_id=extra.get("tenant_id") if extra else None,
            data=extra or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(wf)
    else:
        # Update existing workflow
        wf.state = new_state
        wf.updated_at = datetime.utcnow()
        
        # Merge extra data
        if extra:
            if wf.data is None:
                wf.data = {}
            wf.data.update(extra)
            
            # Extract specific fields if present
            if "liveness" in extra:
                liveness = extra["liveness"]
                if isinstance(liveness, dict):
                    wf.liveness_score = liveness.get("score")
                    wf.is_live = liveness.get("is_live")
            
            if "match" in extra:
                wf.is_match = extra.get("match")
            
            if "fused_score" in extra:
                wf.match_score = extra.get("fused_score")
            
            if "risk" in extra:
                risk = extra["risk"]
                if isinstance(risk, dict):
                    wf.risk_score = risk.get("score")
                    wf.risk_decision = risk.get("decision")
    
    await session.commit()
    await session.refresh(wf)
    
    return wf


async def get_workflow(session: AsyncSession, session_id: str) -> Optional[IdentityWorkflow]:
    """Get workflow by session ID."""
    return await session.get(IdentityWorkflow, session_id)


async def list_workflows(
    session: AsyncSession,
    tenant_id: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 100
) -> list[IdentityWorkflow]:
    """
    List workflows with optional filters.
    
    Args:
        session: Database session
        tenant_id: Filter by tenant
        state: Filter by state
        limit: Maximum results
    
    Returns:
        List of workflows
    """
    from sqlalchemy import select
    
    stmt = select(IdentityWorkflow)
    
    if tenant_id:
        stmt = stmt.where(IdentityWorkflow.tenant_id == tenant_id)
    
    if state:
        stmt = stmt.where(IdentityWorkflow.state == state)
    
    stmt = stmt.limit(limit).order_by(IdentityWorkflow.created_at.desc())
    
    result = await session.execute(stmt)
    return result.scalars().all()
