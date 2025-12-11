"""
Decision Module - Risk-based Decision Logic

Applies jurisdiction-aware policies and rules to convert risk assessments
into actionable decisions (approve, review, decline).

Renamed from: risk_brain.decision
"""

from typing import Dict, Any, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Decision(Enum):
    """Risk-based decision outcomes."""
    APPROVE = "approve"
    REVIEW = "review"
    DECLINE = "decline"


class DecisionEngine:
    """Converts risk assessments into decisions based on policies."""
    
    def __init__(self, policy_config: Dict[str, Any] = None):
        """
        Initialize decision engine with policy configuration.
        
        Args:
            policy_config: Policy thresholds and rules
        """
        self.policy_config = policy_config or self._default_policies()
        self.logger = logging.getLogger(f"{__name__}.DecisionEngine")
    
    def decide(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a decision based on risk assessment.
        
        Args:
            assessment: Risk assessment data
            
        Returns:
            Decision with reasoning and confidence
        """
        self.logger.debug(f"Making decision for event: {assessment.get('event_id')}")
        
        risk_level = assessment.get("overall_risk", "unknown")
        jurisdiction = assessment.get("jurisdiction", "default")
        
        decision = self._apply_policies(risk_level, jurisdiction, assessment)
        reasoning = self._generate_reasoning(decision, assessment)
        
        result = {
            "decision": decision.value,
            "reasoning": reasoning,
            "jurisdiction": jurisdiction,
            "risk_level": risk_level,
            "requires_review": decision == Decision.REVIEW,
            "can_proceed": decision in [Decision.APPROVE, Decision.REVIEW]
        }
        
        self.logger.info(
            f"Decision: {decision.value}",
            extra={"event_id": assessment.get("event_id")}
        )
        
        return result
    
    def _apply_policies(self, risk_level: str, jurisdiction: str,
                       assessment: Dict[str, Any]) -> Decision:
        """Apply jurisdiction-specific policies to determine decision."""
        
        # Get jurisdiction-specific policy
        policy = self.policy_config.get(jurisdiction, self.policy_config["default"])
        
        # Map risk level to decision
        if risk_level == "critical":
            return Decision.DECLINE
        elif risk_level == "high":
            return Decision.REVIEW
        elif risk_level == "medium":
            # Check if additional factors warrant review
            if assessment.get("aml_score", 0) > policy.get("aml_threshold", 0.6):
                return Decision.REVIEW
            return Decision.APPROVE
        else:
            return Decision.APPROVE
    
    def _generate_reasoning(self, decision: Decision,
                           assessment: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the decision."""
        reasoning = f"Decision: {decision.value}. "
        
        if decision == Decision.APPROVE:
            reasoning += "Risk profile is acceptable for processing."
        elif decision == Decision.REVIEW:
            reasoning += "Risk factors require manual review before proceeding."
        else:  # DECLINE
            reasoning += "Risk level is too high for approval."
        
        risk_factors = assessment.get("factors", [])
        if risk_factors:
            reasoning += f" Key factors: {', '.join(risk_factors)}."
        
        return reasoning
    
    def _default_policies(self) -> Dict[str, Dict[str, float]]:
        """Return default policy configuration."""
        return {
            "default": {
                "fraud_threshold": 0.7,
                "aml_threshold": 0.6,
                "credit_threshold": 0.65,
                "liquidity_threshold": 0.5
            },
            "au": {
                "fraud_threshold": 0.7,
                "aml_threshold": 0.55,
                "credit_threshold": 0.60,
                "liquidity_threshold": 0.5
            },
            "eu": {
                "fraud_threshold": 0.65,
                "aml_threshold": 0.50,
                "credit_threshold": 0.65,
                "liquidity_threshold": 0.45
            },
            "gcc": {
                "fraud_threshold": 0.65,
                "aml_threshold": 0.45,
                "credit_threshold": 0.70,
                "liquidity_threshold": 0.50
            }
        }


def decide(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to make a risk-based decision.
    
    Renamed from: risk_brain.decision.decide
    
    Args:
        assessment: Risk assessment data
        
    Returns:
        Decision with reasoning and metadata
    """
    engine = DecisionEngine()
    return engine.decide(assessment)
