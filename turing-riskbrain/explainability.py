"""
Explainability Module - Risk Decision Transparency

Provides interpretable explanations for risk assessments, including
factor attribution, decision trees, and audit trails.

Renamed from: risk_brain.explainability
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExplanationFactor:
    """Represents a single contributing factor to risk assessment."""
    name: str
    weight: float
    contribution: float
    description: str


class RiskExplainer:
    """Generates human-readable explanations for risk decisions."""
    
    def __init__(self):
        """Initialize the risk explainer."""
        self.logger = logging.getLogger(f"{__name__}.RiskExplainer")
    
    def explain(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a risk assessment.
        
        Args:
            assessment: Risk assessment data
            
        Returns:
            Explanation dictionary with factors, narrative, and audit trail
        """
        self.logger.debug(f"Generating explanation for assessment")
        
        factors = self._extract_factors(assessment)
        narrative = self._generate_narrative(assessment, factors)
        audit_trail = self._create_audit_trail(assessment)
        
        return {
            "narrative": narrative,
            "factors": factors,
            "audit_trail": audit_trail,
            "confidence": self._calculate_confidence(factors)
        }
    
    def _extract_factors(self, assessment: Dict[str, Any]) -> List[ExplanationFactor]:
        """Extract and rank contributing factors."""
        factors = []
        
        fraud_score = assessment.get("fraud_score", 0)
        if fraud_score > 0.3:
            factors.append(ExplanationFactor(
                name="fraud_risk",
                weight=0.35,
                contribution=fraud_score,
                description="Fraud detection model signals"
            ))
        
        aml_score = assessment.get("aml_score", 0)
        if aml_score > 0.2:
            factors.append(ExplanationFactor(
                name="aml_risk",
                weight=0.30,
                contribution=aml_score,
                description="AML and sanctions screening results"
            ))
        
        credit_score = assessment.get("credit_score", 0)
        if credit_score > 0.25:
            factors.append(ExplanationFactor(
                name="credit_risk",
                weight=0.20,
                contribution=credit_score,
                description="Credit scoring and bureau data"
            ))
        
        liquidity_score = assessment.get("liquidity_score", 0)
        if liquidity_score > 0.15:
            factors.append(ExplanationFactor(
                name="liquidity_risk",
                weight=0.15,
                contribution=liquidity_score,
                description="Liquidity and transaction pattern analysis"
            ))
        
        # Sort by contribution
        factors.sort(key=lambda f: f.contribution, reverse=True)
        return factors
    
    def _generate_narrative(self, assessment: Dict[str, Any],
                           factors: List[ExplanationFactor]) -> str:
        """Generate narrative explanation."""
        risk_level = assessment.get("overall_risk", "unknown")
        jurisdiction = assessment.get("jurisdiction", "unknown")
        
        narrative = f"Risk Assessment: {risk_level} for {jurisdiction} jurisdiction. "
        
        if factors:
            top_factors = [f.name for f in factors[:3]]
            narrative += f"Primary risk factors: {', '.join(top_factors)}. "
        
        narrative += "This assessment is based on comprehensive analysis of fraud, "
        narrative += "AML, credit, and liquidity dimensions using machine learning models "
        narrative += "and regulatory compliance rules."
        
        return narrative
    
    def _create_audit_trail(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create audit trail for compliance and review."""
        return [
            {
                "timestamp": assessment.get("timestamp", "unknown"),
                "event_id": assessment.get("event_id", "unknown"),
                "user_id": assessment.get("user_id", "unknown"),
                "action": "risk_assessment_completed",
                "result": assessment.get("overall_risk", "unknown")
            }
        ]
    
    def _calculate_confidence(self, factors: List[ExplanationFactor]) -> float:
        """Calculate confidence score for the assessment."""
        if not factors:
            return 0.5
        
        # Higher confidence with more factors and stronger signals
        avg_contribution = sum(f.contribution for f in factors) / len(factors)
        return min(0.95, 0.5 + (avg_contribution * 0.45))


def explain(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to generate risk explanation.
    
    Renamed from: risk_brain.explainability.explain
    
    Args:
        assessment: Risk assessment data
        
    Returns:
        Explanation dictionary with narrative and factors
    """
    explainer = RiskExplainer()
    return explainer.explain(assessment)
