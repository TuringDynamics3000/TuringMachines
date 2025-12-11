# TuringMachines™ Platform

**Enterprise-Grade Identity Verification, Risk Intelligence, and Settlement Authority**

TuringMachines is a comprehensive, production-ready platform for financial services providing identity verification, multi-dimensional risk assessment, jurisdiction-aware policy management, and real-time settlement authority.

## Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Kubernetes (optional, for production deployments)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourorgs/turingmachines.git
cd turingmachines

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start services locally
docker-compose up
```

## Platform Components

### Core Services

| Service | Purpose | Status |
|---------|---------|--------|
| **TuringCapture™** | Identity & document capture with biometrics | ✅ Production |
| **TuringOrchestrate™** | Risk-aware flow orchestration | ✅ Production |
| **TuringRiskBrain™** | Fused fraud/AML/credit/liquidity intelligence | ✅ Production |
| **TuringPolicy™** | Jurisdiction-specific regulatory policies | ✅ Production |
| **TuringSettleGuard™** | Real-time settlement authority | ✅ Production |
| **TuringML™** | ML model lifecycle & feature store | 🚀 Beta |
| **TuringInvestigator™** | Human-in-the-loop case management | 🚀 Beta |
| **TuringCore™** | Multi-tenant ledger & events | 🚀 Beta |

### Shared Libraries

- **identity_graph**: Graph-based identity resolution
- **event_schemas**: Standardized event definitions
- **utils**: Common utilities and helpers

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system architecture, data flows, and deployment models.

### High-Level Flow

```
Channels → Capture → Orchestrate → RiskBrain → Policy → SettleGuard → Core
```

## Code Rename: risk_brain → turing_riskbrain

This release includes a major platform transformation renaming all `risk_brain` references to `turing_riskbrain`.

### Breaking Changes

**Python Imports**:
```python
# Old (deprecated)
from risk_brain.fusion import fuse_scores
from risk_brain.risk_brain import RiskBrain

# New (required)
from turing_riskbrain.fusion import fuse_scores
from turing_riskbrain.turing_riskbrain import TuringRiskBrain
```

**API Endpoints**:
```
# New canonical endpoint
POST /v1/turing-riskbrain/evaluate

# Old endpoint (deprecated, with compatibility alias)
POST /v1/risk/evaluate → logs deprecation warning
```

**Class Names**:
```python
# Old
RiskBrain

# New
TuringRiskBrain
```

### Migration Guide

1. **Update imports** in all service code
2. **Update API calls** to use new endpoints
3. **Update telemetry** metric names
4. **Update logs** and span names
5. **Test thoroughly** before deploying

See [MIGRATION.md](./MIGRATION.md) for detailed migration instructions.

## API Documentation

### TuringRiskBrain™ API

```bash
# Evaluate risk
curl -X POST http://localhost:8000/v1/turing-riskbrain/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "user_id": "usr_456",
    "transaction_id": "txn_789",
    "amount": 5000,
    "jurisdiction": "AU"
  }'

# Get explanation
curl -X POST http://localhost:8000/v1/turing-riskbrain/explain \
  -H "Content-Type: application/json" \
  -d '{"assessment": {...}}'

# Get decision
curl -X POST http://localhost:8000/v1/turing-riskbrain/decide \
  -H "Content-Type: application/json" \
  -d '{"assessment": {...}}'
```

### TuringCapture™ API

```bash
# Capture identity
curl -X POST http://localhost:8001/v1/capture/identity \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_123",
    "name": "John Doe",
    "dob": "1990-01-15"
  }'

# Capture document
curl -X POST http://localhost:8001/v1/capture/document \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_123",
    "document_type": "passport",
    "image_data": "base64_encoded_image"
  }'
```

### TuringSettleGuard™ API

```bash
# Authorize settlement
curl -X POST http://localhost:8003/v1/turing-settleguard/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_123",
    "amount": 5000,
    "currency": "AUD",
    "risk_level": "medium"
  }'

# Override decision
curl -X POST http://localhost:8003/v1/turing-settleguard/override \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_123",
    "override_reason": "Verified customer",
    "authorized_by": "admin_001"
  }'
```

## Configuration

### Environment Variables

```bash
# Service Configuration
TURING_CAPTURE_PORT=8001
TURING_ORCHESTRATE_PORT=8002
TURING_RISKBRAIN_PORT=8000
TURING_SETTLEGUARD_PORT=8003

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=secret

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_GRAPH_INTELLIGENCE=true
ENABLE_EXPLAINABILITY=true
ENABLE_AUDIT_LOGGING=true
```

### Policy Configuration

```python
from turing_policy.loader import get_policy_pack

# Load AU policy pack
au_pack = get_policy_pack("AU")

# Validate transaction
result = au_pack.validate_transaction({
    "amount": 10000,
    "currency": "AUD"
})
```

## Development

### Project Structure

```
turingmachines/
├── turing-capture/          # Identity capture service
├── turing-orchestrate/      # Flow orchestration service
├── turing-policy/           # Policy management
├── turing-riskbrain/        # Risk assessment engine
├── turing-ml/               # ML models & registry
├── turing-settleguard/      # Settlement authority
├── turing-investigator/     # Case management
├── turing-core/             # Ledger & events
├── shared-libs/             # Shared libraries
├── deploy/                  # Deployment configs
├── ARCHITECTURE.md          # System architecture
├── MIGRATION.md             # Migration guide
└── README.md                # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific service tests
pytest turing-riskbrain/tests/

# Run integration tests
pytest tests/integration/
```

### Building Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker build -t turingmachines/turing-riskbrain:latest turing-riskbrain/

# Push to registry
docker push turingmachines/turing-riskbrain:latest
```

### Deployment

#### Local Development
```bash
docker-compose up
```

#### Kubernetes
```bash
# Install Helm chart
helm install turingmachines ./deploy/helm/turingmachines

# Upgrade
helm upgrade turingmachines ./deploy/helm/turingmachines

# Check status
kubectl get pods -l app=turingmachines
```

#### AWS ECS
```bash
# Deploy using AWS CLI
aws ecs create-service \
  --cluster turingmachines \
  --service-name turing-riskbrain \
  --task-definition turing-riskbrain:1
```

## Supported Jurisdictions

### Australia (AU)
- AUSTRAC compliance
- Credit checks required
- Beneficial owner disclosure
- Transaction limits: AUD 100,000

### European Union (EU)
- GDPR compliant
- PSD2 compliant
- Enhanced due diligence
- Transaction limits: EUR 50,000

### GCC Region
- Sharia compliance
- Enhanced AML screening
- Sanctions screening
- Transaction limits: AED 75,000

## Monitoring & Observability

### Metrics

```bash
# Prometheus endpoint
http://localhost:9090/metrics

# Key metrics
- turing_riskbrain_latency
- turing_riskbrain_evaluations_total
- turing_settleguard_authorizations_total
- turing_capture_verifications_total
```

### Logging

```bash
# View logs
docker-compose logs -f turing-riskbrain

# Structured logging with correlation IDs
{
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "turing_riskbrain",
  "level": "INFO",
  "correlation_id": "corr_abc123",
  "message": "Risk assessment completed",
  "event_id": "evt_123",
  "risk_level": "medium"
}
```

### Distributed Tracing

```bash
# Jaeger UI
http://localhost:16686

# View traces for risk assessment
# Service: turing-riskbrain
# Operation: evaluate
```

## Security

- **Encryption**: TLS 1.3 for all communications
- **Authentication**: OAuth 2.0 / OpenID Connect
- **Authorization**: Role-based access control (RBAC)
- **Audit**: Comprehensive audit trails
- **Compliance**: GDPR, PSD2, AML/KYC, AUSTRAC

## Performance

- **Latency**: <100ms for risk assessment
- **Throughput**: 10,000+ transactions/second
- **Availability**: 99.99% SLA
- **Scalability**: Horizontal scaling with Kubernetes

## Support & Contribution

- **Issues**: [GitHub Issues](https://github.com/yourorgs/turingmachines/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorgs/turingmachines/discussions)
- **Contributing**: See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

Proprietary - All Rights Reserved

## Changelog

### v2.0.0 (Current)
- ✅ Complete code rename: risk_brain → turing_riskbrain
- ✅ Enterprise monorepo structure
- ✅ Jurisdiction-aware policy management
- ✅ Explainable AI for risk decisions
- ✅ OEM deployment support

### v1.0.0
- Initial release with core risk assessment

## Contact

- **Sales**: sales@turingmachines.io
- **Support**: support@turingmachines.io
- **Technical**: tech@turingmachines.io

---

**TuringMachines™** - Enterprise Risk Intelligence for Financial Services
#   T u r i n g M a c h i n e s   C I / C D   A c t i v e  
 
# CI/CD Pipeline Test - 2025-12-11 13:44:44
