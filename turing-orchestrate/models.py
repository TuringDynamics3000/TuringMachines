"""
TuringOrchestrate™ Workflow Models
===================================

SQLAlchemy models for identity verification workflow state machine.

States:
- pending: Initial state
- selfie_uploaded: Selfie received with liveness check
- id_uploaded: ID document uploaded
- verified_match: Face match successful
- verified_no_match: Face match failed
- complete: Workflow finalized
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class IdentityWorkflow(Base):
    """
    Identity verification workflow state machine.
    
    Tracks the progression of an identity verification session through
    various states, capturing all relevant data at each step.
    """
    __tablename__ = "identity_workflow"

    session_id = Column(String, primary_key=True, index=True)
    state = Column(String, nullable=False, index=True)  # Current workflow state
    tenant_id = Column(String, index=True)  # Tenant/customer ID
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Workflow data (JSON)
    data = Column(JSON, default=dict)  # Arbitrary workflow data
    
    # Liveness results
    liveness_score = Column(Float)
    is_live = Column(Boolean)
    
    # Match results
    match_score = Column(Float)
    is_match = Column(Boolean)
    
    # Risk assessment
    risk_score = Column(Float)
    risk_decision = Column(String)  # allow, deny, escalate
    
    def __repr__(self):
        return f"<IdentityWorkflow(session_id={self.session_id}, state={self.state})>"
