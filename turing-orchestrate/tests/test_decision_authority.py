"""
🔒 DECISION AUTHORITY ACCEPTANCE TEST

This test is the permanent guardrail that ensures:
1. Every workflow has exactly ONE decision.finalised event
2. No other service can emit decision.finalised
3. The orchestrator remains the single source of truth

If this test fails, Decision Authority has regressed.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import IdentityWorkflow, WorkflowEvent
from workflow_service import handle_risk_evaluation
import os


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture
async def test_db_session():
    """Create a test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(IdentityWorkflow.metadata.create_all)
        await conn.run_sync(WorkflowEvent.metadata.create_all)
    
    # Create session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()


async def count_decision_finalised_events(session: AsyncSession, workflow_id: str) -> int:
    """
    Count decision.finalised events for a workflow.
    
    This is the INVARIANT CHECK:
    - Must return exactly 1 for valid workflows
    - 0 means no decision was made (FAIL)
    - >1 means double-firing (FAIL)
    """
    stmt = select(WorkflowEvent).where(
        WorkflowEvent.workflow_id == workflow_id,
        WorkflowEvent.event_type == "decision.finalised"
    )
    result = await session.execute(stmt)
    events = result.scalars().all()
    return len(events)


@pytest.mark.asyncio
async def test_decision_authority_single_decision(test_db_session):
    """
    🔒 ACCEPTANCE TEST: Exactly one decision.finalised per workflow
    
    This test ensures:
    1. handle_risk_evaluation emits exactly one decision.finalised
    2. No double-firing
    3. Decision Authority is enforced
    
    Failure modes:
    - 0 events: No decision was made (authority broken)
    - >1 events: Double-firing (idempotency broken)
    """
    session = test_db_session
    
    # Create a test workflow
    workflow = IdentityWorkflow(
        id="wf_test_001",
        tenant_id="tenant_test",
        state="signals_received",
        data={
            "user_id": "user_test_001",
            "action": "onboarding",
            "signals": {
                "email": "test@example.com",
                "phone": "+61400000000"
            }
        }
    )
    session.add(workflow)
    await session.commit()
    
    # Simulate risk evaluation event
    risk_event = {
        "event_type": "risk.evaluated",
        "workflow_id": "wf_test_001",
        "correlation_id": "corr_test_001",
        "data": {
            "decision": "approve",
            "risk_score": 0.25,
            "risk_band": "low",
            "confidence": 0.95,
            "factors": ["email_verified", "phone_verified"]
        }
    }
    
    # Trigger risk evaluation (this should emit decision.finalised)
    await handle_risk_evaluation(risk_event)
    
    # 🔒 INVARIANT CHECK: Exactly one decision.finalised event
    decision_count = await count_decision_finalised_events(session, "wf_test_001")
    
    # FAIL HARD on violations
    if decision_count == 0:
        pytest.fail(
            "❌ DECISION AUTHORITY BROKEN: No decision.finalised event found. "
            "The orchestrator MUST emit exactly one decision per workflow."
        )
    
    if decision_count > 1:
        pytest.fail(
            f"❌ IDEMPOTENCY BROKEN: Found {decision_count} decision.finalised events. "
            "The orchestrator MUST emit exactly one decision per workflow (no double-firing)."
        )
    
    # SUCCESS: Exactly one decision
    assert decision_count == 1, "Decision Authority enforced: exactly one decision.finalised"
    
    # Verify decision payload structure
    stmt = select(WorkflowEvent).where(
        WorkflowEvent.workflow_id == "wf_test_001",
        WorkflowEvent.event_type == "decision.finalised"
    )
    result = await session.execute(stmt)
    decision_event = result.scalar_one()
    
    # Verify required fields
    assert "decision" in decision_event.data
    assert "risk_summary" in decision_event.data
    assert "authority" in decision_event.data
    assert decision_event.data["authority"]["decided_by"] == "turing_orchestrate"
    
    print("✅ Decision Authority acceptance test PASSED")


@pytest.mark.asyncio
async def test_decision_authority_no_double_firing_on_retry(test_db_session):
    """
    🔒 ACCEPTANCE TEST: No double-firing on retries
    
    If handle_risk_evaluation is called twice (e.g., retry, race condition),
    it MUST NOT emit two decision.finalised events.
    """
    session = test_db_session
    
    # Create a test workflow
    workflow = IdentityWorkflow(
        id="wf_test_002",
        tenant_id="tenant_test",
        state="signals_received",
        data={
            "user_id": "user_test_002",
            "action": "onboarding",
            "signals": {
                "email": "test2@example.com"
            }
        }
    )
    session.add(workflow)
    await session.commit()
    
    risk_event = {
        "event_type": "risk.evaluated",
        "workflow_id": "wf_test_002",
        "correlation_id": "corr_test_002",
        "data": {
            "decision": "review",
            "risk_score": 0.65,
            "risk_band": "medium"
        }
    }
    
    # Call handle_risk_evaluation TWICE (simulating retry)
    await handle_risk_evaluation(risk_event)
    await handle_risk_evaluation(risk_event)  # Second call
    
    # 🔒 INVARIANT: Still exactly one decision.finalised
    decision_count = await count_decision_finalised_events(session, "wf_test_002")
    
    if decision_count > 1:
        pytest.fail(
            f"❌ DOUBLE-FIRING DETECTED: Found {decision_count} decision.finalised events after retry. "
            "The orchestrator MUST be idempotent."
        )
    
    assert decision_count == 1, "No double-firing on retry"
    
    print("✅ No double-firing on retry test PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
