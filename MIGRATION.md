# Migration Guide: risk_brain → turing_riskbrain

This guide provides step-by-step instructions for migrating from the legacy `risk_brain` package to the new `turing_riskbrain` package.

## Overview

The TuringMachines platform v2.0 includes a major code rename transforming all `risk_brain` references to `turing_riskbrain`. This is a **breaking change** that requires updates to all dependent code.

## Timeline

- **v2.0.0**: New `turing_riskbrain` package released with backward compatibility layer
- **v2.1.0** (Q2 2024): Deprecation warnings enabled for old endpoints
- **v3.0.0** (Q4 2024): Old endpoints removed, `risk_brain` package deprecated

## Migration Steps

### Step 1: Update Python Imports

**Before**:
```python
from risk_brain.fusion import fuse_scores
from risk_brain.explainability import explain
from risk_brain.decision import decide
from risk_brain.risk_brain import RiskBrain
```

**After**:
```python
from turing_riskbrain.fusion import fuse_scores
from turing_riskbrain.explainability import explain
from turing_riskbrain.decision import decide
from turing_riskbrain.turing_riskbrain import TuringRiskBrain
```

### Step 2: Update Class Instantiation

**Before**:
```python
risk_engine = RiskBrain(config=config)
assessment = risk_engine.evaluate(event)
```

**After**:
```python
risk_engine = TuringRiskBrain(config=config)
assessment = risk_engine.evaluate(event)
```

### Step 3: Update API Endpoints

#### Risk Evaluation

**Before**:
```bash
POST /v1/risk/evaluate
```

**After** (Canonical):
```bash
POST /v1/turing-riskbrain/evaluate
```

**Note**: The old endpoint `/v1/risk/evaluate` still works but logs a deprecation warning.

#### Risk Explanation

**Before**:
```bash
POST /v1/risk/explain
```

**After**:
```bash
POST /v1/turing-riskbrain/explain
```

#### Risk Decision

**Before**:
```bash
POST /v1/risk/decide
```

**After**:
```bash
POST /v1/turing-riskbrain/decide
```

### Step 4: Update Telemetry

#### Metric Names

**Before**:
```python
metric_name="risk_brain_latency"
metric_name="risk_brain_evaluations_total"
metric_name="risk_brain_errors_total"
```

**After**:
```python
metric_name="turing_riskbrain_latency"
metric_name="turing_riskbrain_evaluations_total"
metric_name="turing_riskbrain_errors_total"
```

#### Span Names

**Before**:
```python
tracer.start_as_current_span("risk_brain.evaluate")
tracer.start_as_current_span("risk_brain.fuse_scores")
```

**After**:
```python
tracer.start_as_current_span("turing_riskbrain.evaluate")
tracer.start_as_current_span("turing_riskbrain.fuse_scores")
```

#### Log Names

**Before**:
```python
logger = logging.getLogger("risk_brain")
```

**After**:
```python
logger = logging.getLogger("turing_riskbrain")
```

### Step 5: Update Configuration

**Before**:
```yaml
services:
  risk_brain:
    image: risk-brain:1.0.0
    port: 8000
    environment:
      - RISK_BRAIN_LOG_LEVEL=INFO
```

**After**:
```yaml
services:
  turing_riskbrain:
    image: turingmachines/turing-riskbrain:2.0.0
    port: 8000
    environment:
      - TURING_RISKBRAIN_LOG_LEVEL=INFO
```

### Step 6: Update Documentation

- Update API documentation to reference new endpoints
- Update architecture diagrams
- Update runbooks and operational guides
- Update integration guides for partners

### Step 7: Update Tests

**Before**:
```python
from risk_brain import RiskBrain
from risk_brain.fusion import fuse_scores

def test_risk_assessment():
    engine = RiskBrain()
    result = engine.evaluate(test_event)
    assert result.fraud_score > 0
```

**After**:
```python
from turing_riskbrain import TuringRiskBrain
from turing_riskbrain.fusion import fuse_scores

def test_risk_assessment():
    engine = TuringRiskBrain()
    result = engine.evaluate(test_event)
    assert result.fraud_score > 0
```

### Step 8: Update Deployment

#### Docker

**Before**:
```dockerfile
FROM risk-brain:1.0.0
WORKDIR /app
COPY . .
```

**After**:
```dockerfile
FROM turingmachines/turing-riskbrain:2.0.0
WORKDIR /app
COPY . .
```

#### Kubernetes

**Before**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: risk-brain
spec:
  containers:
  - name: risk-brain
    image: risk-brain:1.0.0
```

**After**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: turing-riskbrain
spec:
  containers:
  - name: turing-riskbrain
    image: turingmachines/turing-riskbrain:2.0.0
```

## Backward Compatibility

### Compatibility Layer (v2.0.0 - v2.x.x)

The old `risk_brain` package is still available with a compatibility layer that wraps the new `turing_riskbrain` implementation.

```python
# This still works in v2.x.x but logs a deprecation warning
from risk_brain.risk_brain import RiskBrain
engine = RiskBrain()  # Internally uses TuringRiskBrain
```

### Deprecation Warnings

When using old imports or endpoints, you'll see warnings like:

```
DeprecationWarning: risk_brain.RiskBrain is deprecated. 
Use turing_riskbrain.TuringRiskBrain instead.
```

### Removal Timeline

| Version | Status | Old Package | Old Endpoints |
|---------|--------|-------------|---------------|
| v2.0.0 | Current | ✅ Works | ✅ Works (warns) |
| v2.1.0 | Q2 2024 | ✅ Works | ✅ Works (warns) |
| v3.0.0 | Q4 2024 | ❌ Removed | ❌ Removed |

## Testing Migration

### Pre-Migration Checklist

- [ ] Identify all services using `risk_brain`
- [ ] Review API calls to risk assessment endpoints
- [ ] Check telemetry and monitoring configurations
- [ ] Review deployment configurations
- [ ] Prepare test environment

### Migration Testing

1. **Unit Tests**: Update and run unit tests with new imports
2. **Integration Tests**: Test service-to-service communication
3. **End-to-End Tests**: Test complete transaction flows
4. **Performance Tests**: Verify latency and throughput
5. **Monitoring Tests**: Verify metrics and logs are working

### Validation

```bash
# Test new imports
python -c "from turing_riskbrain import TuringRiskBrain; print('OK')"

# Test API endpoint
curl -X POST http://localhost:8000/v1/turing-riskbrain/evaluate \
  -H "Content-Type: application/json" \
  -d '{"event_id": "test"}'

# Check metrics
curl http://localhost:9090/metrics | grep turing_riskbrain

# Check logs
docker logs turing-riskbrain | grep "TuringRiskBrain"
```

## Rollback Plan

If issues occur during migration:

1. **Revert Code Changes**: Roll back to previous version
2. **Revert Deployments**: Use previous Docker images
3. **Check Logs**: Review error logs for root cause
4. **Contact Support**: Reach out to support team

```bash
# Rollback to v1.0.0
docker pull turingmachines/turing-riskbrain:1.0.0
docker-compose up -d

# Or with Kubernetes
kubectl set image deployment/turing-riskbrain \
  turing-riskbrain=turingmachines/turing-riskbrain:1.0.0
```

## Common Issues & Solutions

### Issue: ImportError for turing_riskbrain

**Solution**: Ensure the new package is installed
```bash
pip install turing-riskbrain>=2.0.0
```

### Issue: Old endpoints returning 404

**Solution**: Update API calls to use new endpoints
```bash
# Old
POST /v1/risk/evaluate

# New
POST /v1/turing-riskbrain/evaluate
```

### Issue: Metrics not showing up

**Solution**: Update metric names in monitoring configuration
```yaml
# Prometheus scrape config
- job_name: 'turing-riskbrain'
  metrics_path: '/metrics'
  static_configs:
  - targets: ['localhost:8000']
```

### Issue: Deprecation warnings in logs

**Solution**: Update imports to use new package
```python
# Old (causes warning)
from risk_brain.risk_brain import RiskBrain

# New (no warning)
from turing_riskbrain.turing_riskbrain import TuringRiskBrain
```

## Support

For migration assistance:

- **Documentation**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Examples**: Check `examples/` directory for updated code samples
- **Support Team**: Contact support@turingmachines.io
- **GitHub Issues**: Report issues on GitHub

## Checklist for Complete Migration

- [ ] Updated all Python imports
- [ ] Updated API endpoint calls
- [ ] Updated telemetry metric names
- [ ] Updated span and log names
- [ ] Updated configuration files
- [ ] Updated documentation
- [ ] Updated tests
- [ ] Updated deployment manifests
- [ ] Tested in staging environment
- [ ] Deployed to production
- [ ] Verified metrics and logs
- [ ] Removed deprecation warnings

---

**Migration Status**: Use this guide to track your migration progress and ensure all components are updated to the new `turing_riskbrain` package.
