# turing-orchestrate/workflow_service.py

import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import IdentityWorkflow, WorkflowEvent
from db import async_session

RISK_BRAIN_URL = os.getenv("RISK_BRAIN_URL", "http://localhost:8103")


# ---------- helpers ----------

def _new_id() -> str:
    return str(uuid.uuid4())


async def append_event(
    session: AsyncSession,
    workflow: IdentityWorkflow,
    event_type: str,
    payload: Dict[str, Any],
):
    ev = WorkflowEvent(
        id=_new_id(),
        workflow_id=workflow.id,
        tenant_id=workflow.tenant_id,
        event_type=event_type,
        payload=payload,
    )
    session.add(ev)



async def emit_decision_finalised(
    *,
    session: AsyncSession,
    wf: IdentityWorkflow,
    risk_result: Dict[str, Any],
    correlation_id: Optional[str] = None
) -> None:
    """
    🔒 DECISION AUTHORITY: Single source of truth for final decisions.
    
    This function MUST be the ONLY place in the system that emits decision.finalised.
    
    Guardrails:
    - Called exactly once per workflow after risk evaluation
    - No other service may emit decision.finalised
    - Overrides must emit a new decision.finalised with lineage
    """
    decision_payload = {
        "event_id": f"evt_decision_{uuid.uuid4()}",
        "event_type": "decision.finalised",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        
        "decision_id": f"dec_{wf.id}",
        "correlation_id": correlation_id or f"corr_{uuid.uuid4()}",
        "tenant_id": wf.tenant_id,
        
        "subject": {
            "subject_type": "user",
            "subject_id": wf.data.get("user_id"),
            "action": wf.data.get("action", "onboarding")
        },
        
        "decision": {
            "outcome": wf.decision,              # approve | review | decline
            "confidence": risk_result.get("confidence", 0.0),
            "requires_human": wf.requires_human,
            "can_proceed": wf.decision in ["approve", "review"]
        },
        
        "policy": {
            "jurisdiction": risk_result.get("jurisdiction", "AU"),
            "policy_pack": "au-core",
            "policy_version": risk_result.get("policy_version", "1.0.0")
        },
        
        "risk_summary": {
            "overall_risk": risk_result.get("final_risk", {}).get("band"),
            "risk_score": wf.risk_score,
            "scores": {
                "fraud": risk_result.get("fraud_score"),
                "aml": risk_result.get("aml_score"),
                "credit": risk_result.get("credit_score"),
                "liquidity": risk_result.get("liquidity_score")
            }
        },
        
        "reason_codes": risk_result.get("factors", []),
        
        "models": risk_result.get("models", {}),
        
        "evidence": wf.data.get("evidence_hashes", {}),
        
        "lineage": {
            "supersedes_decision_id": None,
            "overridden_by": None
        },
        
        "authority": {
            "decided_by": "turing_orchestrate",
            "service_version": "1.0.0"
        }
    }
    
    # 🔒 SINGLE SOURCE OF TRUTH: Record to decision ledger
    # Future: This will also publish to Kafka with one additional line
    await append_event(
        session,
        wf,
        "decision.finalised",
        decision_payload
    )

async def get_or_create_workflow(
    session: AsyncSession,
    workflow_id: str,
    tenant_id: str,
) -> IdentityWorkflow:
    wf = await session.get(IdentityWorkflow, workflow_id)
    if wf:
        return wf

    wf = IdentityWorkflow(
        id=workflow_id,
        tenant_id=tenant_id,
        state="pending",
        data={},
    )
    session.add(wf)
    await session.flush()
    return wf


# ---------- risk brain ----------

async def call_riskbrain(payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(f"{RISK_BRAIN_URL}/v1/risk/evaluate", json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            # don't break orchestration if riskbrain is down
            return {
                "error": "riskbrain_unavailable",
                "exception": str(e),
            }


# ---------- state transitions ----------

async def handle_selfie_uploaded(event: Dict[str, Any]) -> None:
    """
    event payload from TuringCapture:
    {
      "workflow_id": "wf-123" OR "session_id": "...",
      "tenant_id": "cu-001",
      "session_id": "sess-selfie-123",
      "liveness": {...}
    }
    """
    payload = event["payload"]
    tenant_id = payload["tenant_id"]
    workflow_id = payload.get("workflow_id") or payload["session_id"]
    selfie_session_id = payload["session_id"]

    async with async_session() as session:
        async with session.begin():
            wf = await get_or_create_workflow(session, workflow_id, tenant_id)

            wf.selfie_session_id = selfie_session_id
            wf.state = "selfie_uploaded"
            wf.data.setdefault("selfie", {})["liveness"] = payload.get("liveness", {})
            wf.updated_at = datetime.utcnow()

            await append_event(session, wf, "selfie_uploaded", payload)


async def handle_id_uploaded(event: Dict[str, Any]) -> None:
    """
    ID upload event (once you build the ID capture flow):
    {
      "workflow_id": "wf-123",
      "tenant_id": "cu-001",
      "id_session_id": "sess-id-456",
      "document_metadata": {...}
    }
    """
    p = event["payload"]
    tenant_id = p["tenant_id"]
    workflow_id = p["workflow_id"]
    id_session_id = p["id_session_id"]

    async with async_session() as session:
        async with session.begin():
            wf = await get_or_create_workflow(session, workflow_id, tenant_id)
            wf.id_session_id = id_session_id
            wf.state = "id_uploaded"
            wf.data.setdefault("id_document", {})["metadata"] = p.get("document_metadata", {})
            wf.updated_at = datetime.utcnow()
            await append_event(session, wf, "id_uploaded", p)


async def handle_match_completed(event: Dict[str, Any]) -> None:
    """
    From TuringCapture /verify:
    {
      "workflow_id": "wf-123",
      "tenant_id": "cu-001",
      "selfie_session_id": "sessA",
      "id_session_id": "sessB",
      "match": true,
      "fused_score": 0.88,
      "raw": {...}
    }
    """
    p = event["payload"]
    tenant_id = p["tenant_id"]
    workflow_id = p["workflow_id"]
    match = p["match"]
    fused_score = p.get("fused_score")

    async with async_session() as session:
        async with session.begin():
            wf = await get_or_create_workflow(session, workflow_id, tenant_id)

            wf.selfie_session_id = p.get("selfie_session_id", wf.selfie_session_id)
            wf.id_session_id = p.get("id_session_id", wf.id_session_id)
            wf.data.setdefault("match", {})["raw"] = p.get("raw", {})
            wf.data["match"]["fused_score"] = fused_score
            wf.data["match"]["is_match"] = match

            wf.state = "match_verified" if match else "match_failed"
            wf.updated_at = datetime.utcnow()

            await append_event(session, wf, "match_completed", p)


async def handle_risk_evaluation(event: Dict[str, Any]) -> None:
    """
    Internal step: call RiskBrain after successful match.
    Expected event payload:
    {
      "workflow_id": "...",
      "tenant_id": "...",
      "signals": {...}  # aggregated signals for riskbrain
    }
    """
    p = event["payload"]
    tenant_id = p["tenant_id"]
    workflow_id = p["workflow_id"]
    signals = p.get("signals", {})

    # call riskbrain
    risk_result = await call_riskbrain(signals)

    async with async_session() as session:
        async with session.begin():
            wf = await get_or_create_workflow(session, workflow_id, tenant_id)

            if "final_risk" in risk_result:
                wf.risk_score = risk_result["final_risk"].get("score")
                wf.risk_band = risk_result["final_risk"].get("band")
                decision = risk_result.get("decision", {})
                wf.decision = decision.get("recommendation")
                wf.requires_human = bool(decision.get("requires_human", False))
                wf.state = "risk_evaluated"
            else:
                # degraded behaviour if riskbrain failed
                wf.data.setdefault("risk_error", risk_result)
                wf.state = "risk_failed"

            wf.data["risk_result"] = risk_result
            wf.updated_at = datetime.utcnow()

            # 🔒 DECISION AUTHORITY: Emit the final decision
            await emit_decision_finalised(
                session=session,
                wf=wf,
                risk_result=risk_result,
                correlation_id=event.get("correlation_id")
            )

            await append_event(session, wf, "risk_evaluated", {"signals": signals, "result": risk_result})


# ---------- dispatcher ----------

EVENT_HANDLERS = {
    "selfie_uploaded": handle_selfie_uploaded,
    "id_uploaded": handle_id_uploaded,
    "match_completed": handle_match_completed,
    "risk_evaluate": handle_risk_evaluation,
}


async def dispatch_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic dispatcher, called by the FastAPI route.
    """
    event_type = event.get("event")
    handler = EVENT_HANDLERS.get(event_type)

    if not handler:
        return {"status": "ignored", "reason": f"unknown_event_type:{event_type}"}

    await handler(event)
    return {"status": "ok", "processed": event_type}
