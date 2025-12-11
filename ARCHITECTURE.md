# TuringMachines™ Platform Architecture

## Overview

TuringMachines is an enterprise-grade, scalable platform for identity verification, risk assessment, and settlement authority. The platform is built as a modular monorepo with clear separation of concerns and jurisdiction-aware policy management.

## System Architecture

### High-Level Data Flow

```
┌────────────────────────────────────────┐
│         CHANNELS                       │
│  Web · Mobile · Branch                 │
└──────────────────┬─────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│      TuringCapture™                     │
│  IDV · Document · Face · Device FP      │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│      TuringOrchestrate™                 │
│  Flow Engine · Step-Up Auth             │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│      TuringRiskBrain™                   │
│  Fraud GNN · AML · Credit · Liquidity   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│      Policy Service                     │
│  AU · EU · GCC Packs                    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│      TuringSettleGuard™                 │
│  Enforcement · Authority                │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│         TuringCore™                     │
│  Ledger · Postings · Events             │
└─────────────────────────────────────────┘
```

## Core Services

### 1. TuringCapture™
**Purpose**: Identity and document capture with biometric verification

**Components**:
- `app.py` - Main application entry point
- `routers/` - API route handlers
- `providers/` - Integration with IDV providers
- `ui/` - Frontend components for capture flows

**Key Features**:
- Identity verification (IDV)
- Document capture and OCR
- Biometric face verification
- Device fingerprinting
- Liveness detection

**API Endpoints**:
- `POST /v1/capture/identity` - Capture identity information
- `POST /v1/capture/document` - Capture identity document
- `POST /v1/capture/biometric` - Capture biometric data

### 2. TuringOrchestrate™
**Purpose**: Risk-aware flow orchestration and step-up authentication

**Components**:
- `app.py` - Flow execution engine
- `engine/` - Flow execution logic
- `flows/` - Flow definitions

**Key Features**:
- Dynamic flow routing based on risk
- Step-up authentication logic
- Context-aware decision making
- Flow state management
- Journey control

**API Endpoints**:
- `POST /v1/orchestrate/flow/{flow_id}` - Execute flow
- `POST /v1/orchestrate/step-up` - Evaluate step-up requirements

### 3. TuringRiskBrain™
**Purpose**: Fused risk assessment across fraud, AML, credit, and liquidity

**Components**:
- `turing_riskbrain.py` - Core risk assessment engine
- `fusion.py` - Multi-dimensional score fusion
- `explainability.py` - Decision transparency
- `decision.py` - Risk-based decision logic

**Key Features**:
- Fraud risk scoring
- AML/sanctions screening
- Credit risk assessment
- Liquidity risk evaluation
- GNN-powered graph intelligence
- Jurisdiction-aware decisions
- Explainable AI

**API Endpoints**:
- `POST /v1/turing-riskbrain/evaluate` - Evaluate risk
- `POST /v1/turing-riskbrain/explain` - Get risk explanation
- `POST /v1/turing-riskbrain/decide` - Get risk-based decision

**Backward Compatibility**:
- `POST /v1/risk/evaluate` - Deprecated, calls new handler with warning

### 4. TuringPolicy™
**Purpose**: Jurisdiction-specific regulatory policy management

**Components**:
- `loader.py` - Policy pack loader
- `packs/au/` - Australian regulations
- `packs/eu/` - European regulations
- `packs/gcc/` - GCC region regulations

**Key Features**:
- Policy pack management
- Jurisdiction-aware rule application
- Compliance validation
- Policy versioning

**Supported Jurisdictions**:
- **AU**: AUSTRAC, credit checks, beneficial owner disclosure
- **EU**: GDPR, PSD2, enhanced due diligence
- **GCC**: Sharia compliance, enhanced AML, sanctions screening

### 5. TuringSettleGuard™
**Purpose**: Real-time settlement authority and enforcement

**Components**:
- `app.py` - Settlement authorization engine
- `rules/` - Enforcement rules
- `adapters/` - Banking system adapters

**Key Features**:
- Real-time settlement authorization
- Regulator-grade enforcement
- Audit trails
- Override capabilities
- Risk-based gating

**API Endpoints**:
- `POST /v1/turing-settleguard/authorize` - Authorize settlement
- `POST /v1/turing-settleguard/override` - Override decision

### 6. TuringML™
**Purpose**: Machine learning model lifecycle and feature store

**Components**:
- `models/` - ML model definitions
- `registry/` - Model registry and versioning
- `scoring/` - Model scoring pipelines

**Key Features**:
- Model training and evaluation
- Model registry
- Feature store
- GPU support
- A/B testing

### 7. TuringInvestigator™
**Purpose**: Human-in-the-loop risk review and case management

**Components**:
- `ui/` - Investigation dashboard
- `api/` - Investigation API
- `graph/` - Graph explorer for entity relationships

**Key Features**:
- Case management
- Graph exploration
- Risk labeling
- Override management
- Audit trails

### 8. TuringCore™
**Purpose**: Multi-tenant ledger and event streaming

**Components**:
- `ledger/` - Ledger engine
- `postings/` - Double-entry postings
- `events/` - Event streaming

**Key Features**:
- Multi-tenant ledger
- Double-entry accounting
- Event sourcing
- AML transaction sync
- Audit logging

## Shared Libraries

### identity_graph
Graph-based identity resolution and relationship mapping for fraud detection.

**Key Classes**:
- `IdentityGraph` - Graph management and entity linking

### event_schemas
Standardized event definitions and validation across all services.

**Key Classes**:
- `BaseEvent` - Base event structure
- `RiskAssessmentEvent` - Risk assessment events
- `SettlementEvent` - Settlement events
- `OverrideEvent` - Override events
- `EventValidator` - Event validation

### utils
Common utilities and helpers.

**Key Classes**:
- `Logger` - Centralized logging
- `Crypto` - Cryptographic utilities
- `Serialization` - JSON serialization
- `Validation` - Data validation
- `Config` - Configuration management

## Code Rename Patch

### From risk_brain to turing_riskbrain

**Directory**:
```
/risk-brain → /turing-riskbrain
```

**Python Package**:
```python
# Before
from risk_brain.fusion import fuse_scores
from risk_brain.explainability import explain
from risk_brain.risk_brain import RiskBrain

# After
from turing_riskbrain.fusion import fuse_scores
from turing_riskbrain.explainability import explain
from turing_riskbrain.turing_riskbrain import TuringRiskBrain
```

**API Endpoints**:
```
# Canonical
POST /v1/turing-riskbrain/evaluate

# Deprecated (with compatibility alias)
POST /v1/risk/evaluate → calls new handler, logs deprecation warning
```

**Class Names**:
```python
# Before
class RiskBrain

# After
class TuringRiskBrain
```

**Telemetry**:
```
# Before
metric_name="risk_brain_latency"

# After
metric_name="turing_riskbrain_latency"
```

## Deployment Architecture

### OEM Partner Deployment (Geniusto)

```
┌────────────────────────────────┐
│  Geniusto Channels / Mobile    │
└──────────────┬─────────────────┘
               │
┌──────────────┴────────────────┐
│  TuringMachines™ OEM          │
│  (Helm / Docker)              │
└──────────────┬────────────────┘
               │
┌──────────────┴────────────────┐
│  TuringCapture™               │
│  TuringOrchestrate™           │
│  TuringRiskBrain™             │
│  TuringSettleGuard™           │
│  Policy Packs                 │
└──────────────┬────────────────┘
               │
┌──────────────┴────────────────┐
│  Core Banking                 │
│  (Geniusto / Temenos etc.)    │
└────────────────────────────────┘
```

### Deployment Options

- **Docker**: Containerized deployment with Docker Compose
- **Kubernetes**: Helm charts for enterprise deployments
- **Cloud**: AWS, Azure, GCP compatible

## Data Flow Example: Transaction Processing

1. **Capture Phase**: User identity and document capture via TuringCapture
2. **Orchestration Phase**: Risk-aware flow routing via TuringOrchestrate
3. **Risk Assessment**: Multi-dimensional risk evaluation via TuringRiskBrain
4. **Policy Check**: Jurisdiction compliance via TuringPolicy
5. **Settlement**: Real-time authorization via TuringSettleGuard
6. **Ledger**: Transaction recording via TuringCore
7. **Investigation**: Case management via TuringInvestigator

## Security Considerations

- **Encryption**: All data encrypted in transit and at rest
- **Authentication**: OAuth 2.0 / OpenID Connect
- **Authorization**: Role-based access control (RBAC)
- **Audit**: Comprehensive audit trails for all operations
- **Compliance**: GDPR, PSD2, AML/KYC, AUSTRAC compliant

## Scalability

- **Horizontal Scaling**: Stateless service design
- **Load Balancing**: Multi-instance deployment
- **Database**: Sharded multi-tenant architecture
- **Caching**: Redis for performance optimization
- **Message Queue**: Async event processing

## Monitoring & Observability

- **Metrics**: Prometheus-compatible metrics
- **Logging**: Structured logging with correlation IDs
- **Tracing**: Distributed tracing support
- **Alerting**: Real-time alerting on anomalies
- **Dashboards**: Grafana dashboards for operations

## Development Guidelines

### Code Organization
- Each service is self-contained with clear boundaries
- Shared libraries in `shared-libs/` for cross-service code
- Deployment configurations in `deploy/`

### API Design
- RESTful APIs with consistent naming
- Versioned endpoints (`/v1/`, `/v2/`, etc.)
- Standardized error responses
- Request/response validation

### Testing
- Unit tests for business logic
- Integration tests for service interactions
- End-to-end tests for complete flows
- Performance tests for scalability

### Documentation
- API documentation with OpenAPI/Swagger
- Architecture Decision Records (ADRs)
- Service-specific README files
- Deployment guides

## Future Enhancements

- **GraphQL API**: Alternative to REST
- **Real-time Analytics**: Stream processing with Kafka
- **Advanced ML**: Deep learning models for fraud detection
- **Blockchain**: Immutable audit trails
- **Multi-language Support**: Polyglot service architecture
