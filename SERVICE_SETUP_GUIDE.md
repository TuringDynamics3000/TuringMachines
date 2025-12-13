# TuringMachines™ Service Setup & Testing Guide

**Purpose**: Detailed setup, configuration, and testing instructions for each service.

---

## Table of Contents

1. [TuringCapture™](#turingcapture)
2. [TuringOrchestrate™](#turingorchestrate)
3. [TuringPolicy™](#turingpolicy)
4. [TuringRiskBrain™](#turingriskbrain)
5. [TuringML™](#turingml)
6. [TuringSettleGuard™](#turingsettle guard)
7. [TuringResolve™](#turinginvestigator)

---

## TuringCapture™

### Overview

TuringCapture provides identity verification, document capture, biometric analysis, and device fingerprinting.

### Setup

#### Backend Setup

```bash
cd turing-capture
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Configuration

Create `.env` file:

```env
# Service
PORT=8101
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres

# IDV Providers
IDV_PROVIDER=mock  # or: jumio, onfido, trulioo
IDV_API_KEY=your_api_key
IDV_API_SECRET=your_api_secret

# Feature Flags
ENABLE_FACE_VERIFICATION=true
ENABLE_DEVICE_FINGERPRINT=true
ENABLE_LIVENESS_DETECTION=true
```

#### Frontend Setup

```bash
cd turing-capture/ui
npm install
npm start
```

### Running

#### Backend

```bash
uvicorn app.main:app --reload --port 8101
```

#### Frontend

```bash
npm start  # Runs on http://localhost:3000
```

### API Endpoints

#### Capture Identity

```bash
POST /v1/capture/identity
Content-Type: application/json

{
  "user_id": "usr_123",
  "name": "John Doe",
  "dob": "1990-01-15",
  "address": "123 Main St, Sydney, NSW 2000",
  "jurisdiction": "AU"
}
```

**Response**:
```json
{
  "capture_id": "cap_abc123",
  "status": "verified",
  "confidence_score": 0.95,
  "message": "Identity verified successfully"
}
```

#### Capture Document

```bash
POST /v1/capture/document
Content-Type: application/json

{
  "user_id": "usr_123",
  "document_type": "passport",
  "image_data": "base64_encoded_image",
  "side": "front"
}
```

#### Capture Biometric

```bash
POST /v1/capture/biometric
Content-Type: application/json

{
  "user_id": "usr_123",
  "biometric_type": "face",
  "image_data": "base64_encoded_image",
  "liveness_check": true
}
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/
```

#### Integration Tests

```bash
pytest tests/integration/
```

#### API Tests

```bash
# Test identity capture
curl -X POST http://localhost:8101/v1/capture/identity \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_123",
    "name": "Test User",
    "dob": "1990-01-15"
  }'

# Test document capture
curl -X POST http://localhost:8101/v1/capture/document \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_123",
    "document_type": "passport",
    "image_data": "fake_base64_data"
  }'
```

---

## TuringOrchestrate™

### Overview

TuringOrchestrate manages customer journeys with risk-aware flow execution and step-up authentication.

### Setup

```bash
cd turing-orchestrate
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

Create `.env` file:

```env
PORT=8102
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres

# Service URLs
TURING_CAPTURE_URL=http://localhost:8101
TURING_RISKBRAIN_URL=http://localhost:8103
TURING_POLICY_URL=http://localhost:8104
TURING_SETTLEGUARD_URL=http://localhost:8105

# Flow Configuration
FLOW_TIMEOUT=60
STEP_TIMEOUT=30
RETRY_ATTEMPTS=3
```

### Running

```bash
uvicorn app.main:app --reload --port 8102
```

### Flow Definition Format

Create flows in `turing-orchestrate/flows/`:

```yaml
flow_id: onboarding_kyc
name: "KYC Onboarding"
version: "1.0"
description: "Complete KYC onboarding flow"

steps:
  - id: identity_capture
    name: "Capture Identity"
    type: http_call
    service: turing-capture
    endpoint: /v1/capture/identity
    timeout: 30s
    retry:
      attempts: 2
      backoff: exponential

  - id: risk_assessment
    name: "Assess Risk"
    type: http_call
    service: turing-riskbrain
    endpoint: /v1/turing-riskbrain/evaluate
    timeout: 10s
    depends_on:
      - identity_capture

  - id: policy_check
    name: "Check Policies"
    type: http_call
    service: turing-policy
    endpoint: /v1/policy/validate
    timeout: 5s
    depends_on:
      - risk_assessment

  - id: settlement
    name: "Authorize Settlement"
    type: http_call
    service: turing-settleguard
    endpoint: /v1/settle/authorise
    timeout: 5s
    depends_on:
      - policy_check
```

### API Endpoints

#### Execute Flow

```bash
POST /v1/flows/{flow_id}/execute
Content-Type: application/json

{
  "user_id": "usr_123",
  "jurisdiction": "AU",
  "amount": 5000
}
```

#### Get Flow Status

```bash
GET /v1/flows/{execution_id}/status
```

#### List Available Flows

```bash
GET /v1/flows
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/test_flow_engine.py
```

#### Integration Tests

```bash
pytest tests/integration/test_flow_execution.py
```

#### API Tests

```bash
# Execute a flow
curl -X POST http://localhost:8102/v1/flows/onboarding_kyc/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_123",
    "jurisdiction": "AU"
  }'

# Check flow status
curl http://localhost:8102/v1/flows/{execution_id}/status
```

---

## TuringPolicy™

### Overview

TuringPolicy manages jurisdiction-specific regulatory rules and compliance requirements.

### Setup

```bash
cd turing-policy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

Create `.env` file:

```env
PORT=8104
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres

# Policy Configuration
POLICY_CACHE_TTL=3600
POLICY_RELOAD_INTERVAL=300
```

### Policy Pack Structure

```
turing-policy/packs/
├── au/
│   ├── aml.yaml
│   ├── kyc.yaml
│   └── sanctions.yaml
├── eu/
│   ├── gdpr.yaml
│   ├── kyc.yaml
│   └── psd2.yaml
└── gcc/
    ├── aml.yaml
    ├── sanctions.yaml
    └── sharia.yaml
```

### Policy File Format

Example: `turing-policy/packs/au/aml.yaml`

```yaml
jurisdiction: AU
policy_type: aml
version: "1.0"
regulator: AUSTRAC

rules:
  - id: kyc_required
    name: "KYC Required"
    type: boolean
    value: true
    description: "Know Your Customer verification is mandatory"

  - id: beneficial_owner_threshold
    name: "Beneficial Owner Disclosure Threshold"
    type: percentage
    value: 25
    description: "Disclose beneficial owners with 25%+ ownership"

  - id: transaction_reporting_threshold
    name: "Transaction Reporting Threshold"
    type: amount
    value: 10000
    currency: AUD
    description: "Report transactions over AUD 10,000"

  - id: sanctions_screening
    name: "Sanctions Screening Required"
    type: boolean
    value: true
    description: "Screen against OFAC and other sanctions lists"

  - id: pep_screening
    name: "PEP Screening Required"
    type: boolean
    value: true
    description: "Screen against Politically Exposed Persons lists"
```

### Running

```bash
uvicorn app.main:app --reload --port 8104
```

### API Endpoints

#### Get Policy Pack

```bash
GET /v1/policy/{jurisdiction}/{policy_type}

# Example
GET /v1/policy/AU/aml
```

**Response**:
```json
{
  "jurisdiction": "AU",
  "policy_type": "aml",
  "version": "1.0",
  "rules": [
    {
      "id": "kyc_required",
      "name": "KYC Required",
      "value": true
    }
  ]
}
```

#### Validate Transaction

```bash
POST /v1/policy/validate
Content-Type: application/json

{
  "jurisdiction": "AU",
  "amount": 50000,
  "transaction_type": "transfer",
  "user_type": "individual"
}
```

#### List Jurisdictions

```bash
GET /v1/policy/jurisdictions
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/test_policy_loader.py
```

#### Integration Tests

```bash
pytest tests/integration/test_policy_validation.py
```

#### API Tests

```bash
# Get AU AML policy
curl http://localhost:8104/v1/policy/AU/aml

# Validate transaction
curl -X POST http://localhost:8104/v1/policy/validate \
  -H "Content-Type: application/json" \
  -d '{
    "jurisdiction": "AU",
    "amount": 50000,
    "transaction_type": "transfer"
  }'
```

---

## TuringRiskBrain™

### Overview

TuringRiskBrain provides fused risk assessment across fraud, AML, credit, and liquidity dimensions.

### Setup

```bash
cd turing-riskbrain
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

Create `.env` file:

```env
PORT=8103
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres

# Service URLs
TURING_ML_URL=http://localhost:8108
TURING_POLICY_URL=http://localhost:8104

# Risk Thresholds
FRAUD_THRESHOLD=0.7
AML_THRESHOLD=0.6
CREDIT_THRESHOLD=0.65
LIQUIDITY_THRESHOLD=0.5

# Feature Flags
ENABLE_EXPLAINABILITY=true
ENABLE_GRAPH_INTELLIGENCE=true
```

### Running

```bash
uvicorn app.main:app --reload --port 8103
```

### API Endpoints

#### Evaluate Risk

```bash
POST /v1/turing-riskbrain/evaluate
Content-Type: application/json

{
  "event_id": "evt_123",
  "user_id": "usr_456",
  "transaction_id": "txn_789",
  "amount": 5000,
  "currency": "AUD",
  "jurisdiction": "AU",
  "transaction_type": "transfer",
  "user_type": "individual"
}
```

**Response**:
```json
{
  "event_id": "evt_123",
  "fraud_score": 0.3,
  "aml_score": 0.2,
  "credit_score": 0.25,
  "liquidity_score": 0.15,
  "overall_risk": "low",
  "explanation": "Low risk profile for AU jurisdiction",
  "factors": ["new_user"],
  "confidence": 0.85
}
```

#### Get Explanation

```bash
POST /v1/turing-riskbrain/explain
Content-Type: application/json

{
  "assessment": {...}
}
```

#### Get Decision

```bash
POST /v1/turing-riskbrain/decide
Content-Type: application/json

{
  "assessment": {...}
}
```

#### Backward Compatibility (Deprecated)

```bash
# Old endpoint (logs deprecation warning)
POST /v1/risk/evaluate
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/test_turing_riskbrain.py
pytest tests/unit/test_fusion.py
pytest tests/unit/test_explainability.py
```

#### Integration Tests

```bash
pytest tests/integration/test_riskbrain_ml.py
pytest tests/integration/test_riskbrain_policy.py
```

#### API Tests

```bash
# Evaluate risk
curl -X POST http://localhost:8103/v1/turing-riskbrain/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test_123",
    "user_id": "usr_456",
    "amount": 5000,
    "jurisdiction": "AU"
  }'

# Get explanation
curl -X POST http://localhost:8103/v1/turing-riskbrain/explain \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## TuringML™

### Overview

TuringML provides model registry, feature store, and GPU-accelerated inference.

### Setup

```bash
cd turing-ml
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

Create `.env` file:

```env
PORT=8108
LOG_LEVEL=INFO

# GPU Configuration
USE_GPU=true
GPU_DEVICE=0
CUDA_VISIBLE_DEVICES=0

# Model Registry
MODEL_REGISTRY_PATH=/models
MODEL_CACHE_SIZE=5GB

# Feature Store
FEATURE_STORE_URL=http://localhost:9000
FEATURE_STORE_API_KEY=your_api_key
```

### Model Organization

```
turing-ml/
├── models/
│   ├── fraud_detector_v2/
│   │   ├── model.pkl
│   │   ├── config.yaml
│   │   └── requirements.txt
│   └── credit_scorer_v1/
│       ├── model.pkl
│       ├── config.yaml
│       └── requirements.txt
├── registry/
│   └── model_registry.json
└── scoring/
    ├── inference.py
    └── feature_engineering.py
```

### Running

```bash
python -m turing_ml.api.main
```

### API Endpoints

#### Score with Model

```bash
POST /v1/score
Content-Type: application/json

{
  "model_id": "fraud_detector_v2",
  "features": {
    "amount": 5000,
    "user_age": 35,
    "account_age_days": 180,
    "transaction_count_24h": 3
  }
}
```

#### Get Model Info

```bash
GET /v1/models/{model_id}
```

#### List Models

```bash
GET /v1/models
```

#### Register Model

```bash
POST /v1/models
Content-Type: application/json

{
  "model_id": "new_model_v1",
  "version": "1.0",
  "model_type": "fraud",
  "framework": "sklearn",
  "accuracy": 0.95
}
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/test_inference.py
```

#### Integration Tests

```bash
pytest tests/integration/test_model_registry.py
```

#### API Tests

```bash
# Score with model
curl -X POST http://localhost:8108/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fraud_detector_v2",
    "features": {
      "amount": 5000,
      "user_age": 35
    }
  }'

# List models
curl http://localhost:8108/v1/models
```

---

## TuringSettleGuard™

### Overview

TuringSettleGuard provides real-time settlement authorization with enforcement rules and audit trails.

### Setup

```bash
cd turing-settleguard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

Create `.env` file:

```env
PORT=8105
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres

# Service URLs
TURING_RISKBRAIN_URL=http://localhost:8103
TURING_POLICY_URL=http://localhost:8104

# Settlement Configuration
SETTLEMENT_TIMEOUT=10
AUDIT_LOGGING=true
ENABLE_OVERRIDES=true
```

### Running

```bash
uvicorn app.main:app --reload --port 8105
```

### API Endpoints

#### Authorize Settlement

```bash
POST /v1/settle/authorise
Content-Type: application/json

{
  "transaction_id": "txn_123",
  "amount": 5000,
  "currency": "AUD",
  "user_id": "usr_456",
  "jurisdiction": "AU"
}
```

**Response**:
```json
{
  "transaction_id": "txn_123",
  "decision": "approve",
  "reason": "Transaction approved for settlement",
  "risk_level": "low",
  "authority": "turing_settleguard",
  "audit_id": "audit_789"
}
```

#### Override Decision

```bash
POST /v1/settle/override
Content-Type: application/json

{
  "transaction_id": "txn_123",
  "override_reason": "Verified customer",
  "authorized_by": "admin_001"
}
```

#### Get Settlement Status

```bash
GET /v1/settle/{transaction_id}
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/test_settlement_engine.py
```

#### Integration Tests

```bash
pytest tests/integration/test_settlement_riskbrain.py
```

#### API Tests

```bash
# Authorize settlement
curl -X POST http://localhost:8105/v1/settle/authorise \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_123",
    "amount": 5000,
    "currency": "AUD",
    "jurisdiction": "AU"
  }'

# Override decision
curl -X POST http://localhost:8105/v1/settle/override \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_123",
    "override_reason": "Manual review approved",
    "authorized_by": "admin_001"
  }'
```

---

## TuringResolve™

### Overview

TuringInvestigator provides case management, graph exploration, and human-in-the-loop overrides.

### Setup

#### API Setup

```bash
cd turing-investigator/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### UI Setup

```bash
cd turing-investigator/ui
npm install
```

### Environment Configuration

Create `.env` file:

```env
PORT=8107
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres

# Service URLs
TURING_RISKBRAIN_URL=http://localhost:8103
TURING_SETTLEGUARD_URL=http://localhost:8105

# Graph Configuration
GRAPH_DB_URL=http://localhost:7687
GRAPH_DB_USER=neo4j
GRAPH_DB_PASSWORD=password
```

### Running

#### API

```bash
uvicorn api.main:app --reload --port 8107
```

#### UI

```bash
npm start  # Runs on http://localhost:3001
```

### API Endpoints

#### Get Case Details

```bash
GET /v1/cases/{case_id}
```

#### List Cases

```bash
GET /v1/cases?status=pending&jurisdiction=AU&limit=20
```

#### Create Override

```bash
POST /v1/overrides
Content-Type: application/json

{
  "case_id": "case_123",
  "transaction_id": "txn_456",
  "reason": "Manual review approved - verified customer",
  "authorized_by": "investigator_001",
  "new_decision": "approve"
}
```

#### Get Entity Graph

```bash
GET /v1/graph/{entity_id}?depth=2
```

### Testing

#### Unit Tests

```bash
pytest tests/unit/test_case_manager.py
```

#### Integration Tests

```bash
pytest tests/integration/test_graph_explorer.py
```

#### API Tests

```bash
# Get case details
curl http://localhost:8107/v1/cases/case_123

# List cases
curl "http://localhost:8107/v1/cases?status=pending"

# Create override
curl -X POST http://localhost:8107/v1/overrides \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "reason": "Manual review approved",
    "authorized_by": "investigator_001"
  }'
```

---

## Common Testing Patterns

### Mock External Services

```python
from unittest.mock import patch, MagicMock

@patch('turing_riskbrain.ml_client.score')
def test_risk_evaluation(mock_score):
    mock_score.return_value = 0.7
    
    result = evaluate_risk({...})
    assert result['fraud_score'] == 0.7
```

### Test Database Interactions

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    return Session()

def test_save_case(test_db):
    case = Case(case_id="test_123", status="pending")
    test_db.add(case)
    test_db.commit()
    
    assert test_db.query(Case).filter_by(case_id="test_123").first() is not None
```

### Test API Endpoints

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_evaluate_risk():
    response = client.post(
        "/v1/turing-riskbrain/evaluate",
        json={
            "event_id": "test_123",
            "user_id": "usr_456",
            "amount": 5000
        }
    )
    assert response.status_code == 200
    assert response.json()["overall_risk"] in ["low", "medium", "high", "critical"]
```

---

## Conclusion

This guide provides comprehensive setup and testing instructions for each TuringMachines service. For additional help, refer to the main documentation files:

- **DEVELOPER_RUNBOOK.md** – Complete development guide
- **ARCHITECTURE.md** – System architecture
- **MIGRATION.md** – Migration from risk_brain to turing_riskbrain
- **README.md** – Platform overview

---

**TuringMachines™ Service Setup & Testing Guide v1.0**  
*Enterprise Risk Intelligence for Financial Services*
