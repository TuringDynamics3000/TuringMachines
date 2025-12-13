# TuringMachines™ Developer Runbook

**Version**: 1.0  
**Audience**: Backend engineers, ML engineers, frontend engineers, DevOps  
**Purpose**: Step-by-step instructions to build, run, extend, and integrate the TuringMachines™ platform.

---

## 1. Overview

TuringMachines™ is the multi-service financial decision OS powering:

- **TuringCapture™** – Identity & device capture
- **TuringOrchestrate™** – Flow engine with YAML-based step execution
- **TuringRiskBrain™** – Fused ML/AML/Fraud/Credit intelligence
- **TuringPolicy™** – Multi-jurisdiction rule packs (AU, EU, GCC)
- **TuringSettleGuard™** – Real-time settlement enforcement
- **TuringML™** – Model registry, GPU execution, feature store
- **TuringResolve™** – Case management & graph explorer
- **TuringCore™** – Ledger integration (external system)

All services run locally via Docker Compose. This runbook covers setup, execution, service structure, integration points, and dev workflows.

---

## 2. Prerequisites

### Required

- **Python 3.11+** – For backend services
- **Node.js 20+** – For frontend services (TuringCapture UI, TuringInvestigator UI)
- **Docker Desktop** – With Compose v2
- **Git** – For version control
- **Make** (optional but recommended) – For build automation

### Optional (for GPU development)

- **NVIDIA drivers** – Latest stable version
- **CUDA toolkit** – 12.0+
- **nvidia-smi** – Available in PATH for GPU detection

### Verification

```bash
# Check Python
python --version  # Should be 3.11+

# Check Node.js
node --version    # Should be 20+

# Check Docker
docker --version
docker compose version

# Check GPU (optional)
nvidia-smi
```

---

## 3. Monorepo Structure

```
turingmachines/
│
├── turing-capture/              # Capture surface (ID/doc/device biometrics)
│   ├── app/                     # FastAPI backend
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── providers/
│   │   └── models/
│   ├── ui/                      # React frontend
│   │   ├── src/
│   │   └── package.json
│   └── requirements.txt
│
├── turing-orchestrate/          # Flow engine (YAML → step executor)
│   ├── app/
│   │   ├── main.py
│   │   ├── engine/
│   │   └── flows/
│   ├── flows/                   # YAML flow definitions
│   └── requirements.txt
│
├── turing-policy/               # AU/EU/GCC jurisdictional policy packs
│   ├── app/
│   │   └── main.py
│   ├── packs/
│   │   ├── au/
│   │   ├── eu/
│   │   └── gcc/
│   └── requirements.txt
│
├── turing-riskbrain/            # Intelligence fusion engine
│   ├── app/
│   │   └── main.py
│   ├── turing_riskbrain.py      # Core engine (renamed from RiskBrain)
│   ├── fusion.py
│   ├── explainability.py
│   ├── decision.py
│   └── requirements.txt
│
├── turing-ml/                   # Model registry + feature store + GNN inference
│   ├── models/
│   ├── registry/
│   ├── scoring/
│   └── requirements.txt
│
├── turing-settleguard/          # Real-time settlement authority
│   ├── app/
│   │   └── main.py
│   ├── rules/
│   └── requirements.txt
│
├── turing-investigator/         # Case UI + graph explorer
│   ├── api/
│   │   └── main.py
│   ├── ui/
│   │   └── package.json
│   └── requirements.txt
│
├── shared-libs/                 # Identity graph, utilities, schema definitions
│   ├── identity_graph/
│   ├── event_schemas/
│   └── utils/
│
├── deploy/
│   ├── compose/
│   │   ├── docker-compose.yml
│   │   └── docker-compose.prod.yml
│   └── helm/                    # OEM partner deployment templates
│
├── assets/branding/             # TuringMachines logos + fonts
│
├── DEVELOPER_RUNBOOK.md         # This file
├── ARCHITECTURE.md
├── MIGRATION.md
├── README.md
└── requirements.txt
```

---

## 4. First-Time Setup

### 4.1 Clone the Repository

```bash
git clone https://github.com/TuringDynamics3000/TuringMachines.git
cd TuringMachines
```

### 4.2 Install Python Dependencies (Per-Service)

Each service has its own `requirements.txt`. Install them in order:

#### TuringCapture
```bash
cd turing-capture
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

#### TuringOrchestrate
```bash
cd ../turing-orchestrate
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### TuringPolicy
```bash
cd ../turing-policy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### TuringRiskBrain
```bash
cd ../turing-riskbrain
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### TuringML
```bash
cd ../turing-ml
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### TuringSettleGuard
```bash
cd ../turing-settleguard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### TuringInvestigator
```bash
cd ../turing-investigator/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4.3 Install Node.js Dependencies (Frontend Services)

#### TuringCapture UI
```bash
cd turing-capture/ui
npm install
```

#### TuringInvestigator UI
```bash
cd turing-investigator/ui
npm install
```

---

## 5. Running the Entire Platform Locally

### 5.1 Using Docker Compose (Recommended)

From the repo root:

```bash
cd deploy/compose
docker compose up --build
```

This starts all services:

| Service | URL | Purpose |
|---------|-----|---------|
| TuringCapture | http://localhost:8101/docs | Identity capture |
| TuringOrchestrate | http://localhost:8102/docs | Flow orchestration |
| TuringRiskBrain | http://localhost:8103/docs | Risk assessment |
| TuringPolicy | http://localhost:8104/docs | Policy management |
| TuringSettleGuard | http://localhost:8105/docs | Settlement authority |
| TuringInvestigator UI | http://localhost:8106 | Case management |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | Dashboards |
| Jaeger | http://localhost:16686 | Tracing |

### 5.2 Stop the Stack

```bash
docker compose down
```

### 5.3 View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f turing-riskbrain
```

---

## 6. Service-by-Service Development Guide

### 6.1 TuringCapture™

**Purpose**: ID capture → Doc ingestion → Face match → Device fingerprint.

#### Run Backend

```bash
cd turing-capture
uvicorn app.main:app --reload --port 8101
```

#### Run Frontend

```bash
cd turing-capture/ui
npm start
```

#### Key Files

- `turing-capture/app/routers/capture.py` – API routes
- `turing-capture/app/providers/` – IDV provider integrations
- `turing-capture/ui/src/screens/*` – React components

#### API Endpoints

```bash
# Capture identity
POST /v1/capture/identity
{
  "user_id": "usr_123",
  "name": "John Doe",
  "dob": "1990-01-15"
}

# Capture document
POST /v1/capture/document
{
  "user_id": "usr_123",
  "document_type": "passport",
  "image_data": "base64_encoded"
}

# Capture biometric
POST /v1/capture/biometric
{
  "user_id": "usr_123",
  "image_data": "base64_encoded"
}
```

---

### 6.2 TuringOrchestrate™

**Purpose**: Execute YAML-defined flows with step-by-step orchestration.

#### Run

```bash
cd turing-orchestrate
uvicorn app.main:app --reload --port 8102
```

#### Test a Flow

```bash
curl -X POST http://localhost:8102/v1/flows/onboarding_kyc/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123",
    "jurisdiction": "AU"
  }'
```

#### Flow Definitions

Flow definitions live in: `turing-orchestrate/flows/*.yaml`

**Example Flow** (`onboarding_kyc.yaml`):

```yaml
flow_id: onboarding_kyc
name: "KYC Onboarding Flow"
steps:
  - id: capture_identity
    type: http_call
    service: turing-capture
    endpoint: /v1/capture/identity
    timeout: 30s

  - id: risk_assessment
    type: http_call
    service: turing-riskbrain
    endpoint: /v1/turing-riskbrain/evaluate
    timeout: 10s

  - id: policy_check
    type: http_call
    service: turing-policy
    endpoint: /v1/policy/check
    timeout: 5s

  - id: settlement_decision
    type: http_call
    service: turing-settleguard
    endpoint: /v1/settle/authorise
    timeout: 5s
```

---

### 6.3 TuringPolicy™

**Purpose**: Store & load jurisdictional rules.

#### Run

```bash
cd turing-policy
uvicorn app.main:app --reload --port 8104
```

#### Example Policies

- `turing-policy/packs/au/aml.yaml` – Australian AML rules
- `turing-policy/packs/eu/kyc.yaml` – European KYC rules
- `turing-policy/packs/gcc/sanctions.yaml` – GCC sanctions rules

#### API Endpoints

```bash
# Get AU AML policy
GET /v1/policy/AU/aml

# Get EU KYC policy
GET /v1/policy/EU/kyc

# Get GCC sanctions policy
GET /v1/policy/GCC/sanctions

# Validate transaction against policy
POST /v1/policy/validate
{
  "jurisdiction": "AU",
  "amount": 50000,
  "transaction_type": "transfer"
}
```

---

### 6.4 TuringRiskBrain™ (formerly RiskBrain)

**Purpose**: Combines ML, AML typologies, sanctions, credit, liquidity into a single decision.

#### Run

```bash
cd turing-riskbrain
uvicorn app.main:app --reload --port 8103
```

#### Evaluate Risk

```bash
curl -X POST http://localhost:8103/v1/turing-riskbrain/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "user_id": "usr_456",
    "transaction_id": "txn_789",
    "amount": 5000,
    "jurisdiction": "AU"
  }'
```

#### Responsibilities

1. **Calls TuringML** for model inference
2. **Calls TuringPolicy** for thresholds
3. **Fuses all signals** (fraud, AML, credit, liquidity)
4. **Produces canonical risk output**
5. **Feeds into TuringSettleGuard**

#### Key Files

- `turing-riskbrain/turing_riskbrain.py` – Core engine
- `turing-riskbrain/fusion.py` – Score fusion
- `turing-riskbrain/explainability.py` – Decision transparency
- `turing-riskbrain/decision.py` – Risk-based decisions

#### API Endpoints

```bash
# Evaluate risk
POST /v1/turing-riskbrain/evaluate

# Get explanation
POST /v1/turing-riskbrain/explain

# Get decision
POST /v1/turing-riskbrain/decide

# Deprecated (backward compatible)
POST /v1/risk/evaluate  # Logs deprecation warning
```

---

### 6.5 TuringML™

**Purpose**: Model training, scoring, registry, embeddings, GPU compute.

#### Run Scoring Server

```bash
cd turing-ml
python -m turing_ml.api.main
```

#### Model Organization

- `turing-ml/models/` – Model definitions
- `turing-ml/registry/` – Model versioning and metadata
- `turing-ml/scoring/` – Inference pipelines

#### API Endpoints

```bash
# Score with model
POST /v1/score
{
  "model_id": "fraud_detector_v2",
  "features": {...}
}

# Get model info
GET /v1/models/{model_id}

# List models
GET /v1/models
```

---

### 6.6 TuringSettleGuard™

**Purpose**: Final authority for settlement approval, step-up, hold, or freeze.

#### Run

```bash
cd turing-settleguard
uvicorn app.main:app --reload --port 8105
```

#### Example Call

```bash
curl -X POST http://localhost:8105/v1/settle/authorise \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_123",
    "amount": 5000,
    "currency": "AUD",
    "risk_level": "medium"
  }'
```

#### Responsibilities

1. **Calls TuringRiskBrain** for risk assessment
2. **Applies policy packs** from TuringPolicy
3. **Produces final settlement action** (approve/review/decline)
4. **Writes audit records** for compliance

#### API Endpoints

```bash
# Authorize settlement
POST /v1/settle/authorise

# Override decision
POST /v1/settle/override
{
  "transaction_id": "txn_123",
  "override_reason": "Verified customer",
  "authorized_by": "admin_001"
}

# Get settlement status
GET /v1/settle/{transaction_id}
```

---

### 6.7 TuringResolve™

**Purpose**: Case explorer, graph viewer, human override system.

#### Run API

```bash
cd turing-investigator
uvicorn api.main:app --reload --port 8107
```

#### Run UI

```bash
cd turing-investigator/ui
npm start
```

#### API Endpoints

```bash
# Get case details
GET /v1/cases/{case_id}

# List cases
GET /v1/cases?status=pending

# Create override
POST /v1/overrides
{
  "case_id": "case_123",
  "reason": "Manual review approved",
  "authorized_by": "investigator_001"
}

# Get entity graph
GET /v1/graph/{entity_id}
```

---

## 7. Development Workflows

### 7.1 Adding a New Flow in TuringOrchestrate

#### Step 1: Create YAML Definition

Create `turing-orchestrate/flows/payment_flow.yaml`:

```yaml
flow_id: payment_flow
name: "Payment Processing Flow"
steps:
  - id: capture_data
    type: http_call
    service: turing-capture
    endpoint: /v1/capture/document
    timeout: 30s

  - id: risk_assessment
    type: http_call
    service: turing-riskbrain
    endpoint: /v1/turing-riskbrain/evaluate
    timeout: 10s

  - id: policy_validation
    type: http_call
    service: turing-policy
    endpoint: /v1/policy/validate
    timeout: 5s

  - id: settlement_decision
    type: http_call
    service: turing-settleguard
    endpoint: /v1/settle/authorise
    timeout: 5s
```

#### Step 2: Execute Flow

```bash
curl -X POST http://localhost:8102/v1/flows/payment_flow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_123",
    "amount": 5000,
    "jurisdiction": "AU"
  }'
```

#### Step 3: Test & Iterate

- Check logs: `docker compose logs -f turing-orchestrate`
- Verify each step executes correctly
- Add error handling and retries as needed

---

### 7.2 Adding a New Jurisdiction Policy

#### Step 1: Create Directory

```bash
mkdir -p turing-policy/packs/uk
```

#### Step 2: Add Policy Files

Create `turing-policy/packs/uk/kyc.yaml`:

```yaml
jurisdiction: UK
policy_type: kyc
version: "1.0"
rules:
  - id: identity_verification
    required: true
    timeout: 30s

  - id: address_verification
    required: true
    timeout: 20s

  - id: beneficial_owner_disclosure
    required: true
    threshold: 25%
```

#### Step 3: Restart Policy Service

```bash
docker compose restart turing-policy
```

#### Step 4: Use in Requests

TuringRiskBrain will automatically load UK policies when request includes:

```bash
curl -X POST http://localhost:8103/v1/turing-riskbrain/evaluate \
  -H "X-Jurisdiction: UK" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

### 7.3 Integration with TuringCore

TuringCore (external ledger system) must follow this flow:

#### Step 1: Call SettleGuard

```bash
POST http://turing-settleguard:8105/v1/settle/authorise
{
  "transaction_id": "txn_123",
  "amount": 5000,
  "currency": "AUD"
}
```

#### Step 2: Check Response

```json
{
  "transaction_id": "txn_123",
  "recommendation": "approve",
  "risk_level": "low",
  "audit_id": "audit_456"
}
```

#### Step 3: Conditional Processing

```python
if response["recommendation"] == "approve":
    # Safe to POST settlement
    core.post_settlement(transaction_id, amount)
else:
    # Hold or reject
    core.hold_settlement(transaction_id, reason="Risk assessment failed")
```

---

## 8. Testing

### 8.1 Unit Tests (Per Service)

```bash
cd turing-riskbrain
pytest tests/unit/

# With coverage
pytest tests/unit/ --cov=turing_riskbrain
```

### 8.2 Integration Tests

```bash
# Test service-to-service communication
pytest tests/integration/

# Example: Test RiskBrain → Policy integration
pytest tests/integration/test_riskbrain_policy.py
```

### 8.3 API Tests

Use `httpx` or `curl`:

```bash
# Test risk evaluation
curl -X POST http://localhost:8103/v1/turing-riskbrain/evaluate \
  -H "Content-Type: application/json" \
  -d '{"event_id": "test_123"}'

# Test with httpx
python -c "
import httpx
response = httpx.post(
    'http://localhost:8103/v1/turing-riskbrain/evaluate',
    json={'event_id': 'test_123'}
)
print(response.json())
"
```

### 8.4 End-to-End Tests

```bash
# Run complete flow
pytest tests/e2e/test_onboarding_flow.py
```

---

## 9. CI/CD

GitHub Actions workflow is defined under: `.github/workflows/ci.yml`

CI runs:

1. **Lint** – Code style checks
2. **Unit tests** – Per-service tests
3. **Build Docker images** – For each service
4. **Push to registry** – If tests pass

---

## 10. Running Everything in Production Mode (Local)

```bash
cd deploy/compose
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

This uses production settings:
- No hot-reload
- Optimized logging
- Resource limits
- Security headers enabled

---

## 11. Support Notes for Developers

### 11.1 Naming Conventions

- Services use prefix `turing-*`
- RiskBrain must always be named **TuringRiskBrain™**
- Every event must carry:
  - `tenant_id` – Multi-tenancy identifier
  - `jurisdiction` – Regulatory jurisdiction
  - `correlation_id` – Request tracing

### 11.2 Logging

Use structured JSON logs:

```python
import logging
import json

logger = logging.getLogger(__name__)

logger.info(json.dumps({
    "service": "turing-riskbrain",
    "event": "evaluation",
    "risk_score": 0.73,
    "correlation_id": "corr_abc123"
}))
```

### 11.3 Key Integration Points

| From | To | Purpose |
|------|-----|---------|
| TuringCapture | Identity Graph | Store entity relationships |
| TuringOrchestrate | All Services | Sequence steps |
| TuringRiskBrain | TuringML | Get model scores |
| TuringRiskBrain | TuringPolicy | Get thresholds |
| TuringSettleGuard | TuringRiskBrain | Get risk assessment |
| TuringInvestigator | All Services | Query & override |

### 11.4 Error Handling

All services should return standardized error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: user_id",
    "correlation_id": "corr_abc123"
  }
}
```

### 11.5 Monitoring & Observability

- **Metrics**: Prometheus endpoint at `/metrics`
- **Logs**: Structured JSON to stdout
- **Traces**: Jaeger at http://localhost:16686

---

## 12. Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port 8103
lsof -i :8103

# Kill process
kill -9 <PID>
```

### Issue: Docker Compose Build Fails

```bash
# Clean up
docker compose down -v
docker system prune -a

# Rebuild
docker compose up --build
```

### Issue: Database Connection Error

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres
```

### Issue: Service Not Responding

```bash
# Check service health
curl http://localhost:8103/health

# View logs
docker compose logs -f turing-riskbrain
```

---

## 13. Quick Reference

### Start Everything

```bash
cd deploy/compose
docker compose up --build
```

### Stop Everything

```bash
docker compose down
```

### View Logs

```bash
docker compose logs -f
docker compose logs -f turing-riskbrain
```

### Run Tests

```bash
pytest
pytest --cov
```

### Access Services

| Service | URL |
|---------|-----|
| TuringCapture API | http://localhost:8101/docs |
| TuringOrchestrate API | http://localhost:8102/docs |
| TuringRiskBrain API | http://localhost:8103/docs |
| TuringPolicy API | http://localhost:8104/docs |
| TuringSettleGuard API | http://localhost:8105/docs |
| TuringInvestigator UI | http://localhost:8106 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |

---

## ✅ Final Note

This runbook is the **single source of truth** for engineers building TuringMachines™.

For questions or updates, refer to:
- **Architecture**: `ARCHITECTURE.md`
- **Migration**: `MIGRATION.md`
- **Platform Overview**: `README.md`

---

**TuringMachines™ Developer Runbook v1.0**  
*Enterprise Risk Intelligence for Financial Services*
