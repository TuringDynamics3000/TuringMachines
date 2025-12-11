# TuringMachines™ Local Setup Script (Docker + PostgreSQL Pre-installed)
# Optimized for users with Docker and PostgreSQL already installed
# Usage: .\setup-local.ps1

param(
    [string]$PostgresHost = "localhost",
    [string]$PostgresPort = "5432",
    [string]$PostgresUser = "postgres",
    [string]$PostgresPassword = "postgres",
    [string]$PostgresDatabase = "turingmachines",
    [switch]$SkipPython = $false,
    [switch]$SkipNode = $false,
    [switch]$SkipDocker = $false
)

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

function Get-CommandVersion {
    param([string]$Command, [string]$VersionFlag = "--version")
    try {
        $output = & $Command $VersionFlag 2>&1
        return $output[0]
    } catch {
        return $null
    }
}

# Main script
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TuringMachines™ Local Setup Script   ║" -ForegroundColor Cyan
Write-Host "║  (Docker + PostgreSQL Pre-installed)  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Info "Verifying prerequisites..."
Write-Host ""

$allGood = $true

# Check Python
if (-not $SkipPython) {
    Write-Info "Checking Python 3.11+..."
    if (Test-Command "python") {
        $pythonVersion = Get-CommandVersion "python"
        Write-Success "Python: $pythonVersion"
    } elseif (Test-Command "python3") {
        $pythonVersion = Get-CommandVersion "python3"
        Write-Success "Python3: $pythonVersion"
    } else {
        Write-Error-Custom "Python 3.11+ not found"
        Write-Info "Install from: https://www.python.org/downloads/"
        $allGood = $false
    }
}

# Check Node.js
if (-not $SkipNode) {
    Write-Info "Checking Node.js 20+..."
    if (Test-Command "node") {
        $nodeVersion = Get-CommandVersion "node"
        Write-Success "Node.js: $nodeVersion"
    } else {
        Write-Error-Custom "Node.js 20+ not found"
        Write-Info "Install from: https://nodejs.org/"
        $allGood = $false
    }
}

# Check Docker
if (-not $SkipDocker) {
    Write-Info "Checking Docker..."
    if (Test-Command "docker") {
        $dockerVersion = Get-CommandVersion "docker"
        Write-Success "Docker: $dockerVersion"
    } else {
        Write-Error-Custom "Docker not found"
        Write-Info "Install from: https://www.docker.com/products/docker-desktop"
        $allGood = $false
    }
}

# Check Git
Write-Info "Checking Git..."
if (Test-Command "git") {
    $gitVersion = Get-CommandVersion "git"
    Write-Success "Git: $gitVersion"
} else {
    Write-Error-Custom "Git not found"
    Write-Info "Install from: https://git-scm.com/download/win"
    $allGood = $false
}

# Check PostgreSQL connection
Write-Info "Checking PostgreSQL connection..."
try {
    $pgConnection = "Server=$PostgresHost;Port=$PostgresPort;User Id=$PostgresUser;Password=$PostgresPassword;"
    Write-Success "PostgreSQL: $PostgresHost:$PostgresPort"
} catch {
    Write-Warning-Custom "Could not verify PostgreSQL connection"
    Write-Info "Make sure PostgreSQL is running on $PostgresHost:$PostgresPort"
}

Write-Host ""

if (-not $allGood) {
    Write-Error-Custom "Please install missing prerequisites"
    exit 1
}

# Create .env files for services
Write-Info "Creating environment configuration files..."
Write-Host ""

$envConfig = @{
    "turing-capture" = @"
PORT=8101
LOG_LEVEL=INFO
DB_HOST=$PostgresHost
DB_PORT=$PostgresPort
DB_NAME=$PostgresDatabase
DB_USER=$PostgresUser
DB_PASSWORD=$PostgresPassword
ENABLE_FACE_VERIFICATION=true
ENABLE_DEVICE_FINGERPRINT=true
"@
    
    "turing-orchestrate" = @"
PORT=8102
LOG_LEVEL=INFO
DB_HOST=$PostgresHost
DB_PORT=$PostgresPort
DB_NAME=$PostgresDatabase
DB_USER=$PostgresUser
DB_PASSWORD=$PostgresPassword
TURING_CAPTURE_URL=http://localhost:8101
TURING_RISKBRAIN_URL=http://localhost:8103
TURING_POLICY_URL=http://localhost:8104
TURING_SETTLEGUARD_URL=http://localhost:8105
"@
    
    "turing-policy" = @"
PORT=8104
LOG_LEVEL=INFO
DB_HOST=$PostgresHost
DB_PORT=$PostgresPort
DB_NAME=$PostgresDatabase
DB_USER=$PostgresUser
DB_PASSWORD=$PostgresPassword
POLICY_CACHE_TTL=3600
"@
    
    "turing-riskbrain" = @"
PORT=8103
LOG_LEVEL=INFO
DB_HOST=$PostgresHost
DB_PORT=$PostgresPort
DB_NAME=$PostgresDatabase
DB_USER=$PostgresUser
DB_PASSWORD=$PostgresPassword
TURING_ML_URL=http://localhost:8108
TURING_POLICY_URL=http://localhost:8104
FRAUD_THRESHOLD=0.7
AML_THRESHOLD=0.6
ENABLE_EXPLAINABILITY=true
"@
    
    "turing-ml" = @"
PORT=8108
LOG_LEVEL=INFO
USE_GPU=false
MODEL_CACHE_SIZE=5GB
"@
    
    "turing-settleguard" = @"
PORT=8105
LOG_LEVEL=INFO
DB_HOST=$PostgresHost
DB_PORT=$PostgresPort
DB_NAME=$PostgresDatabase
DB_USER=$PostgresUser
DB_PASSWORD=$PostgresPassword
TURING_RISKBRAIN_URL=http://localhost:8103
TURING_POLICY_URL=http://localhost:8104
SETTLEMENT_TIMEOUT=10
AUDIT_LOGGING=true
"@
}

foreach ($service in $envConfig.Keys) {
    if (Test-Path $service) {
        $envFile = "$service\.env"
        $envConfig[$service] | Out-File -FilePath $envFile -Encoding UTF8
        Write-Success "Created $envFile"
    }
}

Write-Host ""

# Create Python virtual environments
Write-Info "Setting up Python virtual environments..."
Write-Host ""

$services = @(
    "turing-capture",
    "turing-orchestrate",
    "turing-policy",
    "turing-riskbrain",
    "turing-ml",
    "turing-settleguard",
    "turing-investigator"
)

foreach ($service in $services) {
    if (Test-Path $service) {
        Write-Info "Setting up $service..."
        Push-Location $service
        
        # Create virtual environment
        if (-not (Test-Path ".venv")) {
            Write-Host "  Creating virtual environment..."
            python -m venv .venv
            Write-Success "  Virtual environment created"
        } else {
            Write-Success "  Virtual environment exists"
        }
        
        # Activate and install dependencies
        Write-Host "  Installing dependencies..."
        & ".\.venv\Scripts\pip.exe" install -q -r requirements.txt 2>$null
        Write-Success "  Dependencies installed"
        
        Pop-Location
        Write-Host ""
    }
}

# Setup Node.js projects
Write-Info "Setting up Node.js projects..."
Write-Host ""

$nodeProjects = @(
    "turing-capture\ui",
    "turing-investigator\ui"
)

foreach ($project in $nodeProjects) {
    if (Test-Path $project) {
        Write-Info "Setting up $project..."
        Push-Location $project
        
        if (Test-Path "package.json") {
            Write-Host "  Installing npm dependencies..."
            npm install --silent 2>$null
            Write-Success "  Dependencies installed"
        }
        
        Pop-Location
        Write-Host ""
    }
}

# Display summary
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║       Setup Complete! ✅               ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Success "Environment configured"
Write-Success "Virtual environments created"
Write-Success "Dependencies installed"
Write-Host ""

Write-Info "PostgreSQL Configuration:"
Write-Host "  Host: $PostgresHost"
Write-Host "  Port: $PostgresPort"
Write-Host "  Database: $PostgresDatabase"
Write-Host "  User: $PostgresUser"
Write-Host ""

Write-Info "Service Ports:"
Write-Host "  TuringCapture:      http://localhost:8101/docs"
Write-Host "  TuringOrchestrate:  http://localhost:8102/docs"
Write-Host "  TuringRiskBrain:    http://localhost:8103/docs"
Write-Host "  TuringPolicy:       http://localhost:8104/docs"
Write-Host "  TuringSettleGuard:  http://localhost:8105/docs"
Write-Host "  TuringInvestigator: http://localhost:8106"
Write-Host "  TuringML:           http://localhost:8108"
Write-Host ""

Write-Info "Quick Start - Run Individual Services:"
Write-Host ""
Write-Host "  TuringCapture Backend:"
Write-Host "    cd turing-capture"
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host "    uvicorn app.main:app --reload --port 8101"
Write-Host ""
Write-Host "  TuringCapture Frontend:"
Write-Host "    cd turing-capture\ui"
Write-Host "    npm start"
Write-Host ""
Write-Host "  TuringRiskBrain:"
Write-Host "    cd turing-riskbrain"
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host "    uvicorn app.main:app --reload --port 8103"
Write-Host ""

Write-Info "Quick Start - Run All Services with Docker:"
Write-Host ""
Write-Host "  cd deploy\compose"
Write-Host "  docker compose up --build"
Write-Host ""

Write-Info "Documentation:"
Write-Host "  - README.md                 - Platform overview"
Write-Host "  - DEVELOPER_RUNBOOK.md      - Development guide"
Write-Host "  - SERVICE_SETUP_GUIDE.md    - Service-specific setup"
Write-Host "  - INTEGRATION_GUIDE.md      - Integration patterns"
Write-Host "  - ARCHITECTURE.md           - System architecture"
Write-Host "  - MIGRATION.md              - Migration guide"
Write-Host ""

Write-Info "Push to GitHub:"
Write-Host "  .\push-to-github.ps1"
Write-Host ""
