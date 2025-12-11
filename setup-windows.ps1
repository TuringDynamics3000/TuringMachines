# TuringMachines™ Windows Setup Script
# Complete setup for Windows development environment
# Usage: .\setup-windows.ps1

param(
    [switch]$SkipGit = $false,
    [switch]$SkipDocker = $false,
    [switch]$SkipPython = $false,
    [switch]$SkipNode = $false
)

# Configuration
$MinPythonVersion = "3.11"
$MinNodeVersion = "20"
$MinGitVersion = "2.30"

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

# Check if command exists
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

# Get version from command
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
Write-Host "================================" -ForegroundColor Cyan
Write-Host "TuringMachines™ Windows Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Info "Checking prerequisites..."
Write-Host ""

$allGood = $true

# Check Git
if (-not $SkipGit) {
    Write-Info "Checking Git..."
    if (Test-Command "git") {
        $gitVersion = Get-CommandVersion "git"
        Write-Success "Git installed: $gitVersion"
    } else {
        Write-Error-Custom "Git not found"
        Write-Info "Install from: https://git-scm.com/download/win"
        $allGood = $false
    }
}

# Check Python
if (-not $SkipPython) {
    Write-Info "Checking Python..."
    if (Test-Command "python") {
        $pythonVersion = Get-CommandVersion "python"
        Write-Success "Python installed: $pythonVersion"
    } elseif (Test-Command "python3") {
        $pythonVersion = Get-CommandVersion "python3"
        Write-Success "Python3 installed: $pythonVersion"
    } else {
        Write-Error-Custom "Python not found"
        Write-Info "Install from: https://www.python.org/downloads/"
        $allGood = $false
    }
}

# Check Node.js
if (-not $SkipNode) {
    Write-Info "Checking Node.js..."
    if (Test-Command "node") {
        $nodeVersion = Get-CommandVersion "node"
        Write-Success "Node.js installed: $nodeVersion"
    } else {
        Write-Error-Custom "Node.js not found"
        Write-Info "Install from: https://nodejs.org/"
        $allGood = $false
    }
}

# Check Docker
if (-not $SkipDocker) {
    Write-Info "Checking Docker..."
    if (Test-Command "docker") {
        $dockerVersion = Get-CommandVersion "docker"
        Write-Success "Docker installed: $dockerVersion"
    } else {
        Write-Warning-Custom "Docker not found (optional)"
        Write-Info "Install from: https://www.docker.com/products/docker-desktop"
    }
}

Write-Host ""

if (-not $allGood) {
    Write-Error-Custom "Please install missing prerequisites and try again"
    exit 1
}

# Create virtual environments for each service
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
        }
        
        # Activate virtual environment
        & ".\.venv\Scripts\Activate.ps1"
        
        # Install dependencies
        if (Test-Path "requirements.txt") {
            Write-Host "  Installing dependencies..."
            pip install -q -r requirements.txt
            Write-Success "  Dependencies installed"
        }
        
        # Deactivate virtual environment
        deactivate
        
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
            npm install --silent
            Write-Success "  Dependencies installed"
        }
        
        Pop-Location
        Write-Host ""
    }
}

# Display summary
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Success "All prerequisites installed and configured"
Write-Host ""

Write-Info "Next steps:"
Write-Host "  1. Review DEVELOPER_RUNBOOK.md for development guide"
Write-Host "  2. Read SERVICE_SETUP_GUIDE.md for service-specific setup"
Write-Host "  3. Check INTEGRATION_GUIDE.md for integration patterns"
Write-Host ""

Write-Info "To start development:"
Write-Host "  cd turing-capture"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn app.main:app --reload --port 8101"
Write-Host ""

Write-Info "To run entire platform with Docker:"
Write-Host "  cd deploy\compose"
Write-Host "  docker compose up --build"
Write-Host ""

Write-Info "For more information:"
Write-Host "  - README.md - Platform overview"
Write-Host "  - ARCHITECTURE.md - System architecture"
Write-Host "  - MIGRATION.md - Migration guide"
Write-Host ""
