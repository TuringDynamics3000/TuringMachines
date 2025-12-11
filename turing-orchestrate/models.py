# turing-orchestrate/models.py

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class IdentityWorkflow(Base):
    __tablename__ = "identity_workflow"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # workflow_id
    tenant_id: Mapped[str] = mapped_column(String, index=True)

    # Core state
    state: Mapped[str] = mapped_column(String, index=True)  # pending/selfie/id/match/risk/complete

    # Linked biometric sessions
    selfie_session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    id_session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Risk/decision info
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_band: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    decision: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # allow/review/restrict/freeze
    requires_human: Mapped[bool] = mapped_column(Boolean, default=False)

    # Arbitrary extra
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class WorkflowEvent(Base):
    __tablename__ = "identity_workflow_event"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String, index=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)

    event_type: Mapped[str] = mapped_column(String, index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ManualDecision(Base):
    __tablename__ = "identity_manual_decision"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String, index=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)

    decision: Mapped[str] = mapped_column(String)  # allow/reject/escalate/close
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    actor: Mapped[str] = mapped_column(String)  # user id / operator id

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
