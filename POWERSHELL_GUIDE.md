# TuringMachines™ PowerShell Quick Start Guide

This guide provides PowerShell scripts and commands for Windows users to set up and run TuringMachines locally.

---

## Prerequisites

You have:
- ✅ Docker Desktop installed
- ✅ PostgreSQL running locally
- ✅ Windows PowerShell or PowerShell Core

You need to install:
- Python 3.11+ - https://www.python.org/downloads/
- Node.js 20+ - https://nodejs.org/
- Git - https://git-scm.com/download/win

---

## Quick Start (3 Steps)

### Step 1: Clone the Repository

```powershell
git clone https://github.com/TuringDynamics3000/TuringMachines.git
cd TuringMachines
```

### Step 2: Run Setup Script

```powershell
# Set execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup script (creates virtual environments and installs dependencies)
.\setup-local.ps1
```

### Step 3: Start Services

**Option A: Run individual service**
```powershell
.\run-services.ps1 -Service turing-riskbrain
```

**Option B: Run all services with Docker**
```powershell
cd deploy\compose
docker compose up --build
```

---

## Available PowerShell Scripts

### 1. setup-local.ps1
**Purpose**: Initial setup with Docker and PostgreSQL pre-installed

```powershell
# Basic setup (uses default PostgreSQL settings)
.\setup-local.ps1

# Custom PostgreSQL settings
.\setup-local.ps1 `
  -PostgresHost "localhost" `
  -PostgresPort "5432" `
  -PostgresUser "postgres" `
  -PostgresPassword "your_password" `
  -PostgresDatabase "turingmachines"

# Skip Python setup (if already configured)
.\setup-local.ps1 -SkipPython
```

**What it does:**
- ✅ Verifies Python, Node.js, Docker, Git
- ✅ Creates .env files for each service
- ✅ Creates Python virtual environments
- ✅ Installs Python dependencies
- ✅ Installs Node.js dependencies

### 2. run-services.ps1
**Purpose**: Start individual services or all services

```powershell
# Interactive menu (choose service to run)
.\run-services.ps1

# Run specific service
.\run-services.ps1 -Service turing-riskbrain
.\run-services.ps1 -Service turing-capture
.\run-services.ps1 -Service turing-orchestrate

# Run frontend for a service
.\run-services.ps1 -Service turing-capture -Frontend

# Run all services with Docker
.\run-services.ps1 -Service all
```

**Available services:**
- turing-capture (port 8101)
- turing-orchestrate (port 8102)
- turing-riskbrain (port 8103)
- turing-policy (port 8104)
- turing-settleguard (port 8105)
- turing-ml (port 8108)
- turing-investigator (port 8107)

### 3. push-to-github.ps1
**Purpose**: Push repository to GitHub

```powershell
# Interactive push to GitHub
.\push-to-github.ps1

# Custom GitHub username and repository
.\push-to-github.ps1 `
  -GitHubUsername "YourUsername" `
  -RepositoryName "TuringMachines" `
  -BranchName "main"
```

**What it does:**
- ✅ Verifies Git is installed
- ✅ Checks for uncommitted changes
- ✅ Adds GitHub remote
- ✅ Renames branch to main
- ✅ Pushes to GitHub

---

## Manual Service Setup

If you prefer not to use scripts, follow these steps:

### Setup Python Virtual Environment

```powershell
# Navigate to service directory
cd turing-riskbrain

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
@"
PORT=8103
LOG_LEVEL=INFO
DB_HOST=localhost
DB_PORT=5432
DB_NAME=turingmachines
DB_USER=postgres
DB_PASSWORD=postgres
TURING_ML_URL=http://localhost:8108
TURING_POLICY_URL=http://localhost:8104
"@ | Out-File -FilePath .env -Encoding UTF8

# Run service
uvicorn app.main:app --reload --port 8103
```

### Setup Node.js Project

```powershell
# Navigate to UI directory
cd turing-capture\ui

# Install dependencies
npm install

# Start development server
npm start
```

---

## Service Endpoints

Once services are running, access them at:

| Service | URL | Purpose |
|---------|-----|---------|
| TuringCapture | http://localhost:8101/docs | Identity capture |
| TuringOrchestrate | http://localhost:8102/docs | Flow orchestration |
| TuringRiskBrain | http://localhost:8103/docs | Risk assessment |
| TuringPolicy | http://localhost:8104/docs | Policy management |
| TuringSettleGuard | http://localhost:8105/docs | Settlement authority |
| TuringInvestigator | http://localhost:8107/docs | Case management |
| TuringML | http://localhost:8108/docs | Model registry |

---

## Docker Compose Commands

```powershell
# Navigate to compose directory
cd deploy\compose

# Start all services
docker compose up --build

# Start in background
docker compose up -d --build

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f turing-riskbrain

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Show running services
docker compose ps

# Execute command in service
docker compose exec turing-riskbrain bash

# Rebuild specific service
docker compose build turing-riskbrain
```

---

## Testing Services

### Test with PowerShell

```powershell
# Test TuringRiskBrain endpoint
$response = Invoke-WebRequest -Uri "http://localhost:8103/v1/turing-riskbrain/evaluate" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"event_id":"test_123","user_id":"usr_456","amount":5000,"jurisdiction":"AU"}'

$response.Content | ConvertFrom-Json | Format-Table
```

### Test with curl

```powershell
# Test TuringRiskBrain
curl -X POST http://localhost:8103/v1/turing-riskbrain/evaluate `
  -H "Content-Type: application/json" `
  -d '{
    "event_id": "test_123",
    "user_id": "usr_456",
    "amount": 5000,
    "jurisdiction": "AU"
  }'
```

---

## Troubleshooting

### Virtual Environment Not Activating

```powershell
# Check if .venv exists
Test-Path .\.venv

# If not, create it
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

### Port Already in Use

```powershell
# Find process using port 8103
Get-NetTCPConnection -LocalPort 8103

# Kill process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force
```

### PostgreSQL Connection Error

```powershell
# Test PostgreSQL connection
psql -h localhost -U postgres -d turingmachines

# If not installed, install PostgreSQL tools or use Docker
docker run -it --rm postgres:15 psql -h host.docker.internal -U postgres
```

### Docker Compose Build Fails

```powershell
# Clean up Docker
docker system prune -a

# Rebuild
docker compose build --no-cache
```

### Module Not Found Error

```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or use --force-reinstall
pip install --force-reinstall -r requirements.txt
```

---

## Development Workflow

### 1. Start Service

```powershell
.\run-services.ps1 -Service turing-riskbrain
```

### 2. Make Changes

Edit files in the service directory. Changes are automatically reloaded due to `--reload` flag.

### 3. Test Changes

```powershell
# In another PowerShell window
curl -X POST http://localhost:8103/v1/turing-riskbrain/evaluate `
  -H "Content-Type: application/json" `
  -d '{"event_id":"test_123","user_id":"usr_456","amount":5000}'
```

### 4. Run Tests

```powershell
cd turing-riskbrain
.\.venv\Scripts\Activate.ps1
pytest tests/
```

### 5. Commit Changes

```powershell
git add .
git commit -m "Add feature: description"
git push origin main
```

---

## GitHub Integration

### Push to GitHub

```powershell
# Interactive push
.\push-to-github.ps1

# Or manual steps
git remote add origin https://github.com/YourUsername/TuringMachines.git
git branch -M main
git push -u origin main
```

### Clone from GitHub

```powershell
git clone https://github.com/TuringDynamics3000/TuringMachines.git
cd TuringMachines
.\setup-local.ps1
```

---

## Useful PowerShell Functions

Add these to your PowerShell profile for quick access:

```powershell
# $PROFILE location: C:\Users\YourUsername\Documents\PowerShell\profile.ps1

# Function to activate TuringMachines venv
function Activate-Turing {
    param([string]$Service = "turing-riskbrain")
    if (Test-Path "$Service\.venv\Scripts\Activate.ps1") {
        & "$Service\.venv\Scripts\Activate.ps1"
    } else {
        Write-Host "Service not found: $Service"
    }
}

# Function to start service
function Start-Turing {
    param([string]$Service = "turing-riskbrain")
    .\run-services.ps1 -Service $Service
}

# Function to run all services
function Start-TuringAll {
    cd deploy\compose
    docker compose up --build
}

# Usage:
# Activate-Turing turing-riskbrain
# Start-Turing turing-capture
# Start-TuringAll
```

---

## Next Steps

1. **Read Documentation**
   - README.md - Platform overview
   - DEVELOPER_RUNBOOK.md - Development guide
   - SERVICE_SETUP_GUIDE.md - Service setup
   - INTEGRATION_GUIDE.md - Integration patterns

2. **Explore Services**
   - Start individual services with `run-services.ps1`
   - Access Swagger UI at http://localhost:PORT/docs
   - Test endpoints with curl or Postman

3. **Contribute**
   - Read CONTRIBUTING.md
   - Create feature branch
   - Make changes
   - Push to GitHub

4. **Deploy**
   - Use Docker Compose for local development
   - Use Kubernetes for production (see deploy/helm/)

---

## Support

For issues or questions:
- Check DEVELOPER_RUNBOOK.md
- Review SERVICE_SETUP_GUIDE.md
- See INTEGRATION_GUIDE.md for integration patterns
- Contact: dev@turingmachines.io

---

**TuringMachines™ PowerShell Guide v1.0**  
*Enterprise Risk Intelligence for Financial Services*
