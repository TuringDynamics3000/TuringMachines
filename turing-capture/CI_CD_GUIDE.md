# TuringCapture™ CI/CD Pipeline Guide

**Bank-Grade Continuous Integration & Deployment**

This document describes the enterprise-grade CI/CD pipeline for TuringCapture, designed to meet the quality standards expected from regulated financial services providers.

---

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [CI Pipeline (ci.yml)](#ci-pipeline)
4. [CD Pipeline (cd.yml)](#cd-pipeline)
5. [Security Pipeline (security.yml)](#security-pipeline)
6. [Local Testing](#local-testing)
7. [Deployment](#deployment)
8. [Monitoring & Observability](#monitoring--observability)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 **Overview**

The TuringCapture CI/CD pipeline provides:

✅ **Automated Testing** - Unit tests, integration tests, health checks  
✅ **Code Quality** - Linting (flake8), formatting (black), type checking (mypy)  
✅ **Security Scanning** - Python vulnerabilities, Docker vulnerabilities, secret detection  
✅ **Docker Image Build** - Multi-stage builds for optimal size and security  
✅ **Container Registry** - Automated push to GitHub Container Registry (GHCR)  
✅ **Versioning** - Semantic versioning with build numbers (v1.<build-number>)  
✅ **Deployment Artifacts** - JSON metadata for deployment automation  

This pipeline ensures that every commit is tested, scanned, and packaged to production standards.

---

## 🏗️ **Pipeline Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPER WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    GIT PUSH / PULL REQUEST                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    CI PIPELINE (ci.yml)                      │
│  ✓ Checkout code                                             │
│  ✓ Setup Python 3.11                                         │
│  ✓ Install dependencies                                      │
│  ✓ Run pytest tests                                          │
│  ✓ Lint with flake8                                          │
│  ✓ Check formatting (black)                                  │
│  ✓ Check imports (isort)                                     │
│  ✓ Type check (mypy)                                         │
│  ✓ Build Docker image                                        │
│  ✓ Test Docker container                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CD PIPELINE (cd.yml) - MAIN BRANCH ONLY         │
│  ✓ Login to GHCR                                             │
│  ✓ Extract version (v1.<build-number>)                       │
│  ✓ Build Docker image                                        │
│  ✓ Push to GHCR with multiple tags                           │
│  ✓ Create deployment artifact                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           SECURITY PIPELINE (security.yml) - WEEKLY          │
│  ✓ Python vulnerability scan (pip-audit)                     │
│  ✓ Container vulnerability scan (Trivy)                      │
│  ✓ Container security scan (Anchore)                         │
│  ✓ Secret detection (TruffleHog)                             │
│  ✓ Upload results to GitHub Security                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT READY                          │
│  Image: ghcr.io/turingdynamics3000/turingcapture:v1.X       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 **CI Pipeline (ci.yml)**

### **Trigger Events**
- Push to `main` or `dev` branches
- Pull requests to `main` or `dev` branches

### **Jobs**

#### **build-test**
Runs on: `ubuntu-latest`

**Steps:**
1. **Checkout code** - Clone repository
2. **Setup Python 3.11** - Install Python environment
3. **Install dependencies** - Install from requirements.txt + dev tools
4. **Run tests** - Execute pytest test suite
5. **Lint with flake8** - Check code quality
6. **Check formatting** - Verify black formatting
7. **Check imports** - Verify isort import ordering
8. **Type check** - Run mypy type checking
9. **Build Docker image** - Create container image
10. **Test Docker container** - Verify health endpoint
11. **Upload artifacts** - Save test results and coverage

### **Quality Gates**

| Check | Tool | Failure Action |
|-------|------|----------------|
| Tests | pytest | ❌ Block merge |
| Critical lint errors | flake8 | ⚠️ Warning only |
| Formatting | black | ⚠️ Warning only |
| Import order | isort | ⚠️ Warning only |
| Type hints | mypy | ⚠️ Warning only |
| Docker build | docker | ❌ Block merge |
| Health check | curl | ❌ Block merge |

### **Local Testing**

Run CI checks locally before pushing:

```powershell
# Navigate to turing-capture
cd turing-capture

# Run tests
pytest -v

# Check linting
flake8 .

# Check formatting
black --check .

# Check imports
isort --check-only .

# Type check
mypy . --ignore-missing-imports

# Build Docker image
docker build -t turing-capture:local .

# Test Docker container
docker run -d -p 8101:8101 --name test-capture turing-capture:local
curl http://localhost:8101/health
docker stop test-capture
docker rm test-capture
```

---

## 🚀 **CD Pipeline (cd.yml)**

### **Trigger Events**
- Push to `main` branch only

### **Jobs**

#### **deploy**
Runs on: `ubuntu-latest`

**Steps:**
1. **Checkout code** - Clone repository
2. **Login to GHCR** - Authenticate with GitHub Container Registry
3. **Extract version** - Generate version: `v1.<GITHUB_RUN_NUMBER>`
4. **Setup Docker Buildx** - Enable advanced Docker features
5. **Build and push** - Build image and push to GHCR with multiple tags
6. **Create deployment artifact** - Generate JSON metadata
7. **Upload artifact** - Save deployment info

### **Versioning Strategy**

**Format:** `v1.<build-number>`

**Examples:**
- `v1.1` - First build
- `v1.42` - 42nd build
- `v1.100` - 100th build

**Tags Created:**
- `ghcr.io/turingdynamics3000/turingcapture:v1.42` - Specific version
- `ghcr.io/turingdynamics3000/turingcapture:latest` - Latest build
- `ghcr.io/turingdynamics3000/turingcapture:abc123` - Git commit SHA

### **Deployment Artifact**

The CD pipeline creates a `deploy-info.json` file:

```json
{
  "service": "turing-capture",
  "version": "v1.42",
  "commit_sha": "abc123",
  "timestamp": "20231211-143022",
  "image": "ghcr.io/turingdynamics3000/turingcapture:v1.42",
  "registry": "ghcr.io",
  "repository": "TuringDynamics3000/TuringMachines",
  "branch": "main",
  "actor": "developer"
}
```

This metadata can be used for:
- Automated deployments
- Rollback procedures
- Audit trails
- Release notes

### **Pull and Run Image**

```powershell
# Pull specific version
docker pull ghcr.io/turingdynamics3000/turingcapture:v1.42

# Run container
docker run -d -p 8101:8101 `
  -e DB_HOST=postgres `
  -e DB_PORT=5432 `
  -e DB_NAME=turingmachines `
  -e DB_USER=postgres `
  -e DB_PASSWORD=postgres `
  --name turing-capture `
  ghcr.io/turingdynamics3000/turingcapture:v1.42

# Check health
curl http://localhost:8101/health

# View logs
docker logs -f turing-capture

# Stop container
docker stop turing-capture
docker rm turing-capture
```

---

## 🔐 **Security Pipeline (security.yml)**

### **Trigger Events**
- Weekly schedule (Monday 3am UTC)
- Manual trigger via workflow_dispatch
- Push to main when requirements.txt or Dockerfile changes

### **Jobs**

#### **security**
Runs on: `ubuntu-latest`

**Steps:**
1. **Python vulnerability scan** - pip-audit checks dependencies
2. **Container vulnerability scan** - Trivy scans Docker image
3. **Container security scan** - Anchore analyzes image security
4. **Secret detection** - TruffleHog finds exposed secrets
5. **Dependency review** - GitHub dependency review (PRs only)
6. **Upload results** - Send findings to GitHub Security tab

### **Security Tools**

| Tool | Purpose | Severity |
|------|---------|----------|
| pip-audit | Python package vulnerabilities | CRITICAL, HIGH |
| Trivy | Container CVE scanning | CRITICAL, HIGH |
| Anchore | Container security best practices | HIGH |
| TruffleHog | Secret detection | ALL |

### **Security Reports**

View security findings:
1. Go to repository **Security** tab
2. Click **Code scanning alerts**
3. Review vulnerabilities
4. Create issues for remediation

### **Manual Security Scan**

Run security scans locally:

```powershell
# Install tools
pip install pip-audit
docker pull aquasec/trivy

# Scan Python dependencies
cd turing-capture
pip-audit -r requirements.txt

# Build image
docker build -t turing-capture:security .

# Scan Docker image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock `
  aquasec/trivy image turing-capture:security
```

---

## 🧪 **Local Testing**

### **Prerequisites**
- Python 3.11+
- Docker Desktop
- Git

### **Setup Local Environment**

```powershell
# Clone repository
git clone https://github.com/TuringDynamics3000/TuringMachines.git
cd TuringMachines/turing-capture

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black flake8 isort mypy
```

### **Run Tests**

```powershell
# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_health.py -v

# Run with output
pytest -v -s
```

### **Code Quality Checks**

```powershell
# Lint
flake8 .

# Format code
black .

# Sort imports
isort .

# Type check
mypy . --ignore-missing-imports
```

### **Build and Test Docker Image**

```powershell
# Build image
docker build -t turing-capture:local .

# Run container
docker run -d -p 8101:8101 --name test-capture turing-capture:local

# Test health endpoint
curl http://localhost:8101/health

# Test API docs
Start-Process http://localhost:8101/docs

# View logs
docker logs -f test-capture

# Stop and remove
docker stop test-capture
docker rm test-capture
```

---

## 🌐 **Deployment**

### **Development Environment**

```powershell
# Pull latest image
docker pull ghcr.io/turingdynamics3000/turingcapture:latest

# Run with dev settings
docker run -d -p 8101:8101 `
  -e LOG_LEVEL=DEBUG `
  -e DB_HOST=localhost `
  --name turing-capture-dev `
  ghcr.io/turingdynamics3000/turingcapture:latest
```

### **Staging Environment**

```powershell
# Pull specific version
docker pull ghcr.io/turingdynamics3000/turingcapture:v1.42

# Run with staging settings
docker run -d -p 8101:8101 `
  -e LOG_LEVEL=INFO `
  -e DB_HOST=staging-db `
  -e DB_NAME=turingmachines_staging `
  --name turing-capture-staging `
  ghcr.io/turingdynamics3000/turingcapture:v1.42
```

### **Production Environment**

```powershell
# Pull verified version
docker pull ghcr.io/turingdynamics3000/turingcapture:v1.42

# Run with production settings
docker run -d -p 8101:8101 `
  -e LOG_LEVEL=WARNING `
  -e DB_HOST=prod-db `
  -e DB_NAME=turingmachines `
  -e DB_USER=turing_prod `
  -e DB_PASSWORD=$env:DB_PASSWORD `
  --restart unless-stopped `
  --name turing-capture-prod `
  ghcr.io/turingdynamics3000/turingcapture:v1.42
```

### **Kubernetes Deployment**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: turing-capture
spec:
  replicas: 3
  selector:
    matchLabels:
      app: turing-capture
  template:
    metadata:
      labels:
        app: turing-capture
    spec:
      containers:
      - name: turing-capture
        image: ghcr.io/turingdynamics3000/turingcapture:v1.42
        ports:
        - containerPort: 8101
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /health
            port: 8101
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8101
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## 📊 **Monitoring & Observability**

### **Health Endpoints**

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/health` | Service health | Load balancer health checks |
| `/ready` | Readiness check | Kubernetes readiness probe |
| `/live` | Liveness check | Kubernetes liveness probe |
| `/metrics` | Prometheus metrics | Monitoring & alerting |

### **Logging**

The service uses structured logging:

```json
{
  "timestamp": "2023-12-11T14:30:22Z",
  "level": "INFO",
  "service": "turing-capture",
  "message": "Creating capture session",
  "user_id": "usr_123",
  "capture_id": "cap_20231211143022_usr_123"
}
```

### **Metrics**

Prometheus metrics available at `/metrics`:
- `requests_total` - Total requests
- `requests_success` - Successful requests
- `requests_failed` - Failed requests
- `avg_response_time_ms` - Average response time

---

## 🔧 **Troubleshooting**

### **CI Pipeline Failures**

#### **Tests Failing**
```powershell
# Run tests locally
cd turing-capture
pytest -v

# Check specific test
pytest tests/test_health.py::test_health_endpoint_status_ok -v
```

#### **Docker Build Failing**
```powershell
# Build locally with verbose output
docker build -t turing-capture:debug . --progress=plain

# Check Dockerfile syntax
docker build -t turing-capture:debug . --no-cache
```

#### **Health Check Failing**
```powershell
# Run container and check logs
docker run -d -p 8101:8101 --name debug-capture turing-capture:local
docker logs debug-capture

# Test health endpoint
curl -v http://localhost:8101/health
```

### **CD Pipeline Failures**

#### **GHCR Push Failing**
- Check GitHub token permissions
- Verify repository settings allow GHCR
- Ensure workflow has `packages: write` permission

#### **Version Tagging Issues**
- Check `GITHUB_RUN_NUMBER` environment variable
- Verify git commit SHA is accessible

### **Security Pipeline Failures**

#### **Vulnerability Detected**
1. Review security alert in GitHub Security tab
2. Update affected package in requirements.txt
3. Test locally
4. Push fix
5. Verify security scan passes

#### **Secret Detected**
1. Review TruffleHog findings
2. Remove secret from code
3. Rotate compromised credentials
4. Add to .gitignore
5. Push fix

---

## 📚 **Additional Resources**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GHCR Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🎯 **Summary**

The TuringCapture CI/CD pipeline provides:

✅ **Automated quality gates** - Every commit is tested  
✅ **Security scanning** - Weekly vulnerability checks  
✅ **Container registry** - Versioned images in GHCR  
✅ **Deployment ready** - Production-grade artifacts  
✅ **Observability** - Health checks and metrics  
✅ **Documentation** - Comprehensive guides  

This establishes **bank-grade engineering discipline** before continuing with product development.

---

**TuringCapture™ CI/CD Pipeline v1.0**  
*Enterprise Risk Intelligence for Financial Services*
