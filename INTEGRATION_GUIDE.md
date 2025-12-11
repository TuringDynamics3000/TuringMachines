# TuringMachines™ Integration Guide

**Purpose**: Detailed integration patterns and service-to-service communication specifications.

---

## Table of Contents

1. [Integration Architecture](#integration-architecture)
2. [Service Communication Patterns](#service-communication-patterns)
3. [Data Flow Examples](#data-flow-examples)
4. [Error Handling](#error-handling)
5. [Event Schema](#event-schema)
6. [Monitoring Integration](#monitoring-integration)

---

## Integration Architecture

### Service Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                    External Channels                         │
│              (Web, Mobile, Branch, Partner)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Orchestr │
                    │  (8102)  │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼───┐      ┌────▼────┐      ┌───▼────┐
    │Capture│      │RiskBrain│      │ Policy │
    │(8101) │      │ (8103)  │      │ (8104) │
    └───┬───┘      └────┬────┘      └───┬────┘
        │               │                │
        └───────────────┼────────────────┘
                        │
                   ┌────▼──────┐
                   │SettleGuard│
                   │  (8105)   │
                   └────┬──────┘
                        │
                   ┌────▼──────┐
                   │TuringCore  │
                   │(External)  │
                   └────────────┘
```

### Integration Layers

| Layer | Components | Purpose |
|-------|-----------|---------|
| **Presentation** | Web, Mobile, Branch | User-facing interfaces |
| **Orchestration** | TuringOrchestrate | Flow coordination |
| **Intelligence** | TuringCapture, RiskBrain, Policy | Decision making |
| **Enforcement** | TuringSettleGuard | Settlement authority |
| **Persistence** | TuringCore | Ledger & events |

---

## Service Communication Patterns

### 1. Synchronous HTTP/REST

Used for immediate responses and real-time decisions.

#### TuringOrchestrate → TuringRiskBrain

```python
# Request
POST http://turing-riskbrain:8103/v1/turing-riskbrain/evaluate
Content-Type: application/json
X-Correlation-ID: corr_abc123
X-Tenant-ID: tenant_001
X-Jurisdiction: AU

{
  "event_id": "evt_123",
  "user_id": "usr_456",
  "transaction_id": "txn_789",
  "amount": 5000,
  "currency": "AUD"
}

# Response
HTTP/1.1 200 OK
Content-Type: application/json

{
  "event_id": "evt_123",
  "fraud_score": 0.3,
  "aml_score": 0.2,
  "credit_score": 0.25,
  "liquidity_score": 0.15,
  "overall_risk": "low",
  "explanation": "Low risk profile",
  "factors": ["new_user"],
  "confidence": 0.85,
  "correlation_id": "corr_abc123"
}
```

#### TuringRiskBrain → TuringPolicy

```python
# Request
GET http://turing-policy:8104/v1/policy/AU/aml
X-Correlation-ID: corr_abc123

# Response
HTTP/1.1 200 OK

{
  "jurisdiction": "AU",
  "policy_type": "aml",
  "version": "1.0",
  "rules": [
    {
      "id": "kyc_required",
      "value": true
    },
    {
      "id": "aml_threshold",
      "value": 0.6
    }
  ]
}
```

#### TuringRiskBrain → TuringML

```python
# Request
POST http://turing-ml:8108/v1/score
Content-Type: application/json
X-Correlation-ID: corr_abc123

{
  "model_id": "fraud_detector_v2",
  "features": {
    "amount": 5000,
    "user_age": 35,
    "account_age_days": 180,
    "transaction_count_24h": 3
  }
}

# Response
HTTP/1.1 200 OK

{
  "model_id": "fraud_detector_v2",
  "score": 0.3,
  "confidence": 0.95,
  "model_version": "2.1.0",
  "inference_time_ms": 45
}
```

### 2. Asynchronous Event Streaming

Used for audit trails, analytics, and non-blocking operations.

#### Event Publishing

```python
# TuringRiskBrain publishes risk assessment event
import json
import redis

redis_client = redis.Redis(host='localhost', port=6379)

event = {
    "event_type": "risk.assessed",
    "event_id": "evt_123",
    "timestamp": "2024-01-15T10:30:00Z",
    "service": "turing_riskbrain",
    "data": {
        "user_id": "usr_456",
        "transaction_id": "txn_789",
        "risk_level": "low",
        "fraud_score": 0.3
    },
    "correlation_id": "corr_abc123",
    "tenant_id": "tenant_001"
}

redis_client.publish('events', json.dumps(event))
```

#### Event Subscription

```python
# TuringInvestigator subscribes to events
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)
pubsub = redis_client.pubsub()
pubsub.subscribe('events')

for message in pubsub.listen():
    if message['type'] == 'message':
        event = json.loads(message['data'])
        if event['event_type'] == 'risk.assessed':
            # Process risk assessment event
            handle_risk_event(event)
```

### 3. Callback/Webhook Pattern

Used for long-running operations with result notification.

#### TuringCapture → TuringOrchestrate (Callback)

```python
# TuringCapture initiates async operation
POST http://turing-capture:8101/v1/capture/document/async
Content-Type: application/json

{
  "user_id": "usr_123",
  "document_type": "passport",
  "image_data": "base64_encoded",
  "callback_url": "http://turing-orchestrate:8102/v1/callbacks/capture/document",
  "correlation_id": "corr_abc123"
}

# Response
HTTP/1.1 202 Accepted

{
  "operation_id": "op_123",
  "status": "processing"
}

# TuringCapture calls callback when done
POST http://turing-orchestrate:8102/v1/callbacks/capture/document
Content-Type: application/json

{
  "operation_id": "op_123",
  "user_id": "usr_123",
  "status": "completed",
  "result": {
    "document_verified": true,
    "confidence_score": 0.95
  },
  "correlation_id": "corr_abc123"
}
```

---

## Data Flow Examples

### Example 1: Complete KYC Onboarding Flow

#### Step 1: Flow Initiation

```
User → TuringOrchestrate
POST /v1/flows/onboarding_kyc/execute
{
  "user_id": "usr_123",
  "jurisdiction": "AU"
}
```

#### Step 2: Identity Capture

```
TuringOrchestrate → TuringCapture
POST /v1/capture/identity
{
  "user_id": "usr_123",
  "name": "John Doe",
  "dob": "1990-01-15"
}

← TuringCapture Response
{
  "capture_id": "cap_123",
  "status": "verified",
  "confidence_score": 0.95
}
```

#### Step 3: Risk Assessment

```
TuringOrchestrate → TuringRiskBrain
POST /v1/turing-riskbrain/evaluate
{
  "event_id": "evt_123",
  "user_id": "usr_123",
  "amount": 0,
  "jurisdiction": "AU"
}

← TuringRiskBrain Response
{
  "fraud_score": 0.2,
  "aml_score": 0.15,
  "overall_risk": "low"
}
```

#### Step 4: Policy Validation

```
TuringRiskBrain → TuringPolicy
GET /v1/policy/AU/kyc

← TuringPolicy Response
{
  "rules": [
    {"id": "kyc_required", "value": true},
    {"id": "document_required", "value": true}
  ]
}
```

#### Step 5: Settlement Decision

```
TuringOrchestrate → TuringSettleGuard
POST /v1/settle/authorise
{
  "transaction_id": "txn_123",
  "user_id": "usr_123",
  "amount": 0,
  "jurisdiction": "AU"
}

← TuringSettleGuard Response
{
  "decision": "approve",
  "reason": "KYC approved",
  "audit_id": "audit_456"
}
```

#### Step 6: Event Publishing

```
TuringSettleGuard → Event Stream
{
  "event_type": "settlement.authorized",
  "user_id": "usr_123",
  "decision": "approve"
}
```

### Example 2: Risk-Based Step-Up Authentication

#### Scenario: High-Risk Transaction

```
User → TuringOrchestrate
POST /v1/flows/payment/execute
{
  "user_id": "usr_456",
  "amount": 50000,
  "jurisdiction": "AU"
}

TuringOrchestrate → TuringRiskBrain
POST /v1/turing-riskbrain/evaluate
{
  "user_id": "usr_456",
  "amount": 50000,
  "jurisdiction": "AU"
}

← TuringRiskBrain Response
{
  "overall_risk": "high",
  "fraud_score": 0.7,
  "aml_score": 0.65
}

TuringOrchestrate → TuringOrchestrate (Internal)
Determine step-up requirement: "biometric_required"

TuringOrchestrate → User
{
  "status": "step_up_required",
  "method": "biometric",
  "message": "Please complete biometric verification"
}

User → TuringCapture
POST /v1/capture/biometric
{
  "user_id": "usr_456",
  "image_data": "base64_encoded"
}

TuringOrchestrate → TuringSettleGuard
POST /v1/settle/authorise
{
  "transaction_id": "txn_789",
  "amount": 50000,
  "step_up_completed": true
}

← TuringSettleGuard Response
{
  "decision": "approve",
  "reason": "Step-up completed, risk mitigated"
}
```

---

## Error Handling

### Standard Error Response Format

All services should return errors in this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: user_id",
    "details": {
      "field": "user_id",
      "reason": "required"
    },
    "correlation_id": "corr_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Meaning | Retry |
|------|-------------|---------|-------|
| INVALID_REQUEST | 400 | Bad request | No |
| UNAUTHORIZED | 401 | Authentication failed | No |
| FORBIDDEN | 403 | Authorization failed | No |
| NOT_FOUND | 404 | Resource not found | No |
| CONFLICT | 409 | Resource conflict | No |
| RATE_LIMITED | 429 | Too many requests | Yes |
| SERVICE_ERROR | 500 | Internal server error | Yes |
| SERVICE_UNAVAILABLE | 503 | Service unavailable | Yes |
| TIMEOUT | 504 | Request timeout | Yes |

### Retry Strategy

```python
import time
import requests

def call_with_retry(url, data, max_retries=3, backoff_factor=2):
    """Call service with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code < 500:
                return response
            
            # Retry on 5xx errors
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)
        
        except requests.Timeout:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)
            else:
                raise
    
    return response
```

---

## Event Schema

### Base Event Structure

```json
{
  "event_id": "evt_123",
  "event_type": "risk.assessed",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "turing_riskbrain",
  "correlation_id": "corr_abc123",
  "tenant_id": "tenant_001",
  "jurisdiction": "AU",
  "data": {}
}
```

### Risk Assessment Event

```json
{
  "event_type": "risk.assessed",
  "data": {
    "event_id": "evt_123",
    "user_id": "usr_456",
    "transaction_id": "txn_789",
    "fraud_score": 0.3,
    "aml_score": 0.2,
    "credit_score": 0.25,
    "liquidity_score": 0.15,
    "overall_risk": "low"
  }
}
```

### Settlement Event

```json
{
  "event_type": "settlement.authorized",
  "data": {
    "transaction_id": "txn_123",
    "user_id": "usr_456",
    "amount": 5000,
    "currency": "AUD",
    "decision": "approve",
    "audit_id": "audit_789"
  }
}
```

### Override Event

```json
{
  "event_type": "override.applied",
  "data": {
    "case_id": "case_123",
    "transaction_id": "txn_456",
    "original_decision": "decline",
    "new_decision": "approve",
    "reason": "Manual review approved",
    "authorized_by": "investigator_001"
  }
}
```

---

## Monitoring Integration

### Metrics Collection

Each service should expose Prometheus metrics:

```
# HELP turing_riskbrain_evaluations_total Total risk evaluations
# TYPE turing_riskbrain_evaluations_total counter
turing_riskbrain_evaluations_total{jurisdiction="AU"} 1234

# HELP turing_riskbrain_latency_seconds Risk evaluation latency
# TYPE turing_riskbrain_latency_seconds histogram
turing_riskbrain_latency_seconds_bucket{le="0.1"} 1000
turing_riskbrain_latency_seconds_bucket{le="0.5"} 1200
turing_riskbrain_latency_seconds_bucket{le="1.0"} 1234

# HELP turing_settleguard_authorizations_total Total settlement authorizations
# TYPE turing_settleguard_authorizations_total counter
turing_settleguard_authorizations_total{decision="approve"} 5000
turing_settleguard_authorizations_total{decision="decline"} 150
```

### Logging Integration

All services should log in structured JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "turing_riskbrain",
  "level": "INFO",
  "event": "risk_assessment_completed",
  "user_id": "usr_456",
  "transaction_id": "txn_789",
  "risk_level": "low",
  "duration_ms": 45,
  "correlation_id": "corr_abc123"
}
```

### Distributed Tracing

All services should include trace headers:

```
X-Trace-ID: trace_abc123
X-Span-ID: span_def456
X-Parent-Span-ID: span_xyz789
```

---

## Integration Checklist

- [ ] All services implement standard error response format
- [ ] All services include correlation_id in requests/responses
- [ ] All services log in structured JSON format
- [ ] All services expose Prometheus metrics
- [ ] All services implement health check endpoint
- [ ] All services support distributed tracing
- [ ] All services implement retry logic for external calls
- [ ] All services validate input data
- [ ] All services implement request timeouts
- [ ] All services publish relevant events

---

## Troubleshooting Integration Issues

### Service Not Responding

```bash
# Check service health
curl http://service-name:port/health

# Check logs
docker logs service-name

# Check network connectivity
docker exec service-name ping other-service
```

### Slow Response Times

```bash
# Check service metrics
curl http://service-name:port/metrics | grep latency

# Check database performance
docker exec postgres psql -U postgres -c "EXPLAIN ANALYZE SELECT ..."

# Check network latency
docker exec service-name ping -c 5 other-service
```

### Data Inconsistency

```bash
# Check correlation IDs in logs
docker logs service-name | grep "correlation_id"

# Verify event ordering
redis-cli LRANGE events 0 -1

# Check database transactions
docker exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity"
```

---

## Conclusion

This integration guide provides comprehensive patterns and specifications for service-to-service communication in TuringMachines. For additional information, refer to:

- **DEVELOPER_RUNBOOK.md** – Development guide
- **SERVICE_SETUP_GUIDE.md** – Service setup
- **ARCHITECTURE.md** – System architecture

---

**TuringMachines™ Integration Guide v1.0**  
*Enterprise Risk Intelligence for Financial Services*
