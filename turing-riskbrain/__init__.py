"""
TuringRiskBrain™ - Enterprise Risk Intelligence Engine

A comprehensive risk assessment platform providing fused fraud, AML, credit,
and liquidity intelligence with GNN-powered graph analysis and jurisdiction-aware
decision logic.

Renamed from: risk_brain
"""

from .turing_riskbrain import TuringRiskBrain, RiskAssessment, RiskLevel
from .fusion import fuse_scores, ScoreFusion
from .explainability import explain, RiskExplainer
from .decision import decide, DecisionEngine, Decision

__version__ = "2.0.0"
__all__ = [
    "TuringRiskBrain",
    "RiskAssessment",
    "RiskLevel",
    "fuse_scores",
    "ScoreFusion",
    "explain",
    "RiskExplainer",
    "decide",
    "DecisionEngine",
    "Decision"
]
