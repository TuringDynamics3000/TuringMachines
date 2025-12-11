"""
Fusion Module - Multi-dimensional Risk Score Aggregation

Combines fraud, AML, credit, and liquidity scores into unified risk assessments
using weighted fusion algorithms and jurisdiction-aware logic.

Renamed from: risk_brain.fusion
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ScoreFusion:
    """Fuses multiple risk scores into a unified assessment."""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize score fusion with configurable weights.
        
        Args:
            weights: Dictionary of dimension weights (fraud, aml, credit, liquidity)
        """
        self.weights = weights or {
            "fraud": 0.35,
            "aml": 0.30,
            "credit": 0.20,
            "liquidity": 0.15
        }
        self.logger = logging.getLogger(f"{__name__}.ScoreFusion")
    
    def fuse_scores(self, scores: Dict[str, float], 
                   jurisdiction: str = "default") -> float:
        """
        Fuse multiple risk scores into a single composite score.
        
        Args:
            scores: Dictionary with keys: fraud, aml, credit, liquidity
            jurisdiction: Regulatory jurisdiction for context
            
        Returns:
            Weighted composite risk score (0.0 to 1.0)
        """
        self.logger.debug(f"Fusing scores for jurisdiction: {jurisdiction}")
        
        # Apply jurisdiction-specific adjustments
        adjusted_scores = self._apply_jurisdiction_adjustments(scores, jurisdiction)
        
        # Calculate weighted sum
        composite = sum(
            adjusted_scores.get(dim, 0) * self.weights.get(dim, 0)
            for dim in ["fraud", "aml", "credit", "liquidity"]
        )
        
        # Normalize to 0-1 range
        composite = min(max(composite, 0.0), 1.0)
        
        self.logger.info(f"Composite score: {composite:.3f} for {jurisdiction}")
        return composite
    
    def _apply_jurisdiction_adjustments(self, scores: Dict[str, float],
                                       jurisdiction: str) -> Dict[str, float]:
        """Apply jurisdiction-specific adjustments to scores."""
        adjusted = scores.copy()
        
        # EU: Stricter AML requirements
        if jurisdiction.upper() in ["EU", "EUROPE"]:
            adjusted["aml"] = min(adjusted.get("aml", 0) * 1.2, 1.0)
        
        # AU: Stricter credit checks
        elif jurisdiction.upper() in ["AU", "AUSTRALIA"]:
            adjusted["credit"] = min(adjusted.get("credit", 0) * 1.15, 1.0)
        
        # GCC: Enhanced AML and sanctions screening
        elif jurisdiction.upper() in ["GCC", "GULF"]:
            adjusted["aml"] = min(adjusted.get("aml", 0) * 1.25, 1.0)
        
        return adjusted


def fuse_scores(fraud: float, aml: float, credit: float, 
                liquidity: float, jurisdiction: str = "default") -> float:
    """
    Convenience function to fuse scores without instantiation.
    
    Renamed from: risk_brain.fusion.fuse_scores
    
    Args:
        fraud: Fraud risk score (0.0-1.0)
        aml: AML risk score (0.0-1.0)
        credit: Credit risk score (0.0-1.0)
        liquidity: Liquidity risk score (0.0-1.0)
        jurisdiction: Regulatory jurisdiction
        
    Returns:
        Composite risk score (0.0-1.0)
    """
    fusion = ScoreFusion()
    scores = {
        "fraud": fraud,
        "aml": aml,
        "credit": credit,
        "liquidity": liquidity
    }
    return fusion.fuse_scores(scores, jurisdiction)
