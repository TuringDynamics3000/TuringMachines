"""
Event Schemas - Shared Library

Provides standardized event schemas and validation for all TuringMachines
services to ensure consistent data flow and interoperability.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json


class EventType(Enum):
    """Standard event types across TuringMachines."""
    USER_CREATED = "user.created"
    USER_VERIFIED = "user.verified"
    TRANSACTION_INITIATED = "transaction.initiated"
    TRANSACTION_COMPLETED = "transaction.completed"
    RISK_ASSESSED = "risk.assessed"
    SETTLEMENT_AUTHORIZED = "settlement.authorized"
    SETTLEMENT_BLOCKED = "settlement.blocked"
    OVERRIDE_APPLIED = "override.applied"


@dataclass
class BaseEvent:
    """Base event structure for all TuringMachines events."""
    event_id: str
    event_type: str
    timestamp: str
    source_service: str
    user_id: Optional[str] = None
    transaction_id: Optional[str] = None
    jurisdiction: str = "default"
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        data = asdict(self)
        if self.metadata is None:
            data.pop("metadata")
        return data
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class RiskAssessmentEvent(BaseEvent):
    """Event for risk assessment completion."""
    risk_level: str = "unknown"
    fraud_score: float = 0.0
    aml_score: float = 0.0
    credit_score: float = 0.0
    liquidity_score: float = 0.0
    decision: str = "pending"


@dataclass
class SettlementEvent(BaseEvent):
    """Event for settlement authorization."""
    amount: float = 0.0
    currency: str = "USD"
    decision: str = "pending"
    reason: str = ""
    authority: str = "unknown"


@dataclass
class OverrideEvent(BaseEvent):
    """Event for override application."""
    override_type: str = "unknown"
    override_reason: str = ""
    authorized_by: str = "unknown"
    original_decision: str = "unknown"
    new_decision: str = "unknown"


class EventValidator:
    """Validates events against schemas."""
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> bool:
        """
        Validate event structure.
        
        Args:
            event: Event dictionary
            
        Returns:
            True if event is valid
        """
        required_fields = ["event_id", "event_type", "timestamp", "source_service"]
        return all(field in event for field in required_fields)
    
    @staticmethod
    def validate_risk_event(event: Dict[str, Any]) -> bool:
        """Validate risk assessment event."""
        if not EventValidator.validate_event(event):
            return False
        
        required_fields = ["risk_level", "fraud_score", "aml_score"]
        return all(field in event for field in required_fields)
    
    @staticmethod
    def validate_settlement_event(event: Dict[str, Any]) -> bool:
        """Validate settlement event."""
        if not EventValidator.validate_event(event):
            return False
        
        required_fields = ["amount", "currency", "decision"]
        return all(field in event for field in required_fields)


__all__ = [
    "EventType",
    "BaseEvent",
    "RiskAssessmentEvent",
    "SettlementEvent",
    "OverrideEvent",
    "EventValidator"
]
