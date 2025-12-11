"""
TuringRiskBrain™ - FastAPI Application
Multi-dimensional risk assessment with liveness detection integration
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from turing_riskbrain import TuringRiskBrain, RiskLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TuringRiskBrain™",
    description="Multi-Dimensional Risk Assessment with Liveness Detection",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize risk brain
risk_brain = TuringRiskBrain()


# ============================================================================
# Models
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


class LivenessData(BaseModel):
    """Liveness detection data from identity verification"""
    liveness_score: float = Field(..., ge=0, le=1)
    blink_score: float = Field(..., ge=0, le=1)
    motion_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    face_centered: bool
    face_size: float = Field(..., ge=0, le=1)
    passed: bool


class IdentityData(BaseModel):
    """Identity verification data"""
    id_quality: Optional[float] = Field(None, ge=0, le=1)
    face_match_score: Optional[float] = Field(None, ge=0, le=1)
    liveness: Optional[LivenessData] = None
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = None


class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    tenant_id: Optional[str] = Field(None, description="Tenant identifier")
    identity: Optional[IdentityData] = Field(None, description="Identity verification data")
    transaction: Optional[Dict[str, Any]] = Field(None, description="Transaction data")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class RiskFactors(BaseModel):
    """Risk factors breakdown"""
    fraud: float = Field(..., ge=0, le=100)
    aml: float = Field(..., ge=0, le=100)
    credit: float = Field(..., ge=0, le=100)
    identity: float = Field(..., ge=0, le=100)
    liveness: float = Field(..., ge=0, le=100)


class RiskAssessmentResponse(BaseModel):
    """Response from risk assessment"""
    session_id: str
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_band: str = Field(..., description="Risk band: low, medium, high, critical")
    risk_factors: RiskFactors
    decision_recommendation: str = Field(..., description="Recommended decision")
    confidence: float = Field(..., ge=0, le=1, description="Assessment confidence")
    flags: List[str] = Field(..., description="Risk flags")
    explanation: str = Field(..., description="Human-readable explanation")
    timestamp: str


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "TuringRiskBrain™",
        "description": "Multi-Dimensional Risk Assessment Engine",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        service="turing-riskbrain",
        version="2.0.0",
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/v1/risk/assess", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Assess risk across multiple dimensions
    
    This endpoint analyzes:
    - Identity verification quality
    - Liveness detection scores
    - Biometric match quality
    - Transaction patterns
    - User behavior
    - AML/fraud indicators
    
    Returns comprehensive risk assessment with decision recommendation.
    """
    logger.info(f"Assessing risk for session: {request.session_id}")
    
    # Calculate risk factors
    risk_factors = calculate_risk_factors(request)
    
    # Calculate overall risk score (weighted average)
    overall_risk_score = calculate_overall_risk(risk_factors)
    
    # Determine risk band
    risk_band = determine_risk_band(overall_risk_score)
    
    # Generate flags
    flags = generate_risk_flags(request, risk_factors)
    
    # Determine decision recommendation
    decision = recommend_decision(risk_band, flags, request.identity)
    
    # Calculate confidence
    confidence = calculate_confidence(request)
    
    # Generate explanation
    explanation = generate_explanation(risk_band, risk_factors, flags)
    
    logger.info(
        f"Risk assessment complete for session {request.session_id}: "
        f"score={overall_risk_score:.2f}, band={risk_band}, decision={decision}"
    )
    
    return RiskAssessmentResponse(
        session_id=request.session_id,
        risk_score=overall_risk_score,
        risk_band=risk_band,
        risk_factors=risk_factors,
        decision_recommendation=decision,
        confidence=confidence,
        flags=flags,
        explanation=explanation,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/v1/risk/liveness-score")
async def calculate_liveness_risk(liveness: LivenessData):
    """
    Calculate risk score from liveness data alone
    
    This endpoint is useful for real-time liveness assessment during capture.
    """
    logger.info("Calculating liveness risk score")
    
    # Calculate liveness risk (inverse of liveness score)
    liveness_risk = (1 - liveness.liveness_score) * 100
    
    # Adjust based on confidence
    if liveness.confidence < 0.8:
        liveness_risk += 15
    
    # Adjust based on blink/motion
    if liveness.blink_score < 0.3:
        liveness_risk += 10
    if liveness.motion_score < 0.2:
        liveness_risk += 10
    
    # Adjust based on face positioning
    if not liveness.face_centered:
        liveness_risk += 5
    if liveness.face_size < 0.15 or liveness.face_size > 0.85:
        liveness_risk += 5
    
    # Clamp to 0-100
    liveness_risk = max(0, min(100, liveness_risk))
    
    risk_band = determine_risk_band(liveness_risk)
    
    return {
        "liveness_risk_score": liveness_risk,
        "risk_band": risk_band,
        "passed": liveness.passed,
        "liveness_score": liveness.liveness_score,
        "confidence": liveness.confidence,
    }


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_risk_factors(request: RiskAssessmentRequest) -> RiskFactors:
    """Calculate individual risk factor scores"""
    
    # Fraud risk (placeholder - would use ML models)
    fraud_risk = 20.0
    
    # AML risk (placeholder - would check sanctions lists)
    aml_risk = 15.0
    
    # Credit risk (placeholder - would use credit scoring)
    credit_risk = 25.0
    
    # Identity risk (based on verification quality)
    identity_risk = 30.0
    if request.identity:
        if request.identity.id_quality:
            identity_risk -= request.identity.id_quality * 20
        if request.identity.face_match_score:
            identity_risk -= request.identity.face_match_score * 10
    
    # Liveness risk (based on liveness detection)
    liveness_risk = 50.0
    if request.identity and request.identity.liveness:
        liveness_data = request.identity.liveness
        
        # Base liveness risk (inverse of score)
        liveness_risk = (1 - liveness_data.liveness_score) * 100
        
        # Adjust based on confidence
        if liveness_data.confidence < 0.8:
            liveness_risk += 15
        
        # Adjust based on blink/motion
        if liveness_data.blink_score < 0.3:
            liveness_risk += 10
        if liveness_data.motion_score < 0.2:
            liveness_risk += 10
        
        # Adjust based on face positioning
        if not liveness_data.face_centered:
            liveness_risk += 5
        if liveness_data.face_size < 0.15 or liveness_data.face_size > 0.85:
            liveness_risk += 5
        
        # Clamp to 0-100
        liveness_risk = max(0, min(100, liveness_risk))
    
    return RiskFactors(
        fraud=fraud_risk,
        aml=aml_risk,
        credit=credit_risk,
        identity=identity_risk,
        liveness=liveness_risk,
    )


def calculate_overall_risk(factors: RiskFactors) -> float:
    """Calculate weighted overall risk score"""
    
    # Weights for each factor
    weights = {
        "fraud": 0.25,
        "aml": 0.20,
        "credit": 0.15,
        "identity": 0.20,
        "liveness": 0.20,  # Liveness is critical for identity verification
    }
    
    overall = (
        factors.fraud * weights["fraud"]
        + factors.aml * weights["aml"]
        + factors.credit * weights["credit"]
        + factors.identity * weights["identity"]
        + factors.liveness * weights["liveness"]
    )
    
    return round(overall, 2)


def determine_risk_band(risk_score: float) -> str:
    """Determine risk band from risk score"""
    if risk_score < 30:
        return "low"
    elif risk_score < 60:
        return "medium"
    elif risk_score < 85:
        return "high"
    else:
        return "critical"


def generate_risk_flags(request: RiskAssessmentRequest, factors: RiskFactors) -> List[str]:
    """Generate risk flags based on assessment"""
    flags = []
    
    # Liveness flags
    if request.identity and request.identity.liveness:
        liveness = request.identity.liveness
        
        if not liveness.passed:
            flags.append("liveness_check_failed")
        
        if liveness.liveness_score < 0.75:
            flags.append("low_liveness_score")
        
        if liveness.confidence < 0.8:
            flags.append("low_liveness_confidence")
        
        if liveness.blink_score < 0.3:
            flags.append("insufficient_blink_activity")
        
        if liveness.motion_score < 0.2:
            flags.append("insufficient_motion")
    
    # Identity flags
    if request.identity:
        if request.identity.face_match_score and request.identity.face_match_score < 0.8:
            flags.append("low_face_match_score")
        
        if request.identity.id_quality and request.identity.id_quality < 0.7:
            flags.append("low_id_quality")
    
    # Factor-based flags
    if factors.fraud > 50:
        flags.append("elevated_fraud_risk")
    
    if factors.aml > 50:
        flags.append("elevated_aml_risk")
    
    if factors.liveness > 50:
        flags.append("elevated_liveness_risk")
    
    return flags


def recommend_decision(risk_band: str, flags: List[str], identity: Optional[IdentityData]) -> str:
    """Recommend decision based on risk assessment"""
    
    # Check for critical flags
    critical_flags = ["liveness_check_failed", "elevated_fraud_risk"]
    has_critical_flag = any(flag in flags for flag in critical_flags)
    
    if risk_band == "low" and not has_critical_flag:
        return "approved"
    elif risk_band == "medium":
        return "step_up"
    elif risk_band == "high":
        return "manual_review"
    else:
        return "rejected"


def calculate_confidence(request: RiskAssessmentRequest) -> float:
    """Calculate confidence in risk assessment"""
    
    confidence = 0.7  # Base confidence
    
    # Increase confidence if we have liveness data
    if request.identity and request.identity.liveness:
        confidence += 0.15
        
        # Further increase if liveness confidence is high
        if request.identity.liveness.confidence > 0.8:
            confidence += 0.1
    
    # Increase confidence if we have identity data
    if request.identity:
        if request.identity.id_quality:
            confidence += 0.05
    
    return min(1.0, confidence)


def generate_explanation(risk_band: str, factors: RiskFactors, flags: List[str]) -> str:
    """Generate human-readable explanation"""
    
    explanations = []
    
    # Risk band explanation
    if risk_band == "low":
        explanations.append("Low risk profile detected.")
    elif risk_band == "medium":
        explanations.append("Medium risk profile requires additional verification.")
    elif risk_band == "high":
        explanations.append("High risk profile requires manual review.")
    else:
        explanations.append("Critical risk profile detected.")
    
    # Factor explanations
    if factors.liveness > 50:
        explanations.append(f"Liveness risk is elevated ({factors.liveness:.0f}/100).")
    
    if factors.fraud > 50:
        explanations.append(f"Fraud risk indicators present ({factors.fraud:.0f}/100).")
    
    if factors.identity > 50:
        explanations.append(f"Identity verification concerns ({factors.identity:.0f}/100).")
    
    # Flag explanations
    if "liveness_check_failed" in flags:
        explanations.append("Liveness detection check failed.")
    
    if "low_face_match_score" in flags:
        explanations.append("Face match score below threshold.")
    
    return " ".join(explanations)


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 TuringRiskBrain™ service starting...")
    logger.info("✅ Service initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 TuringRiskBrain™ service shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8103)
