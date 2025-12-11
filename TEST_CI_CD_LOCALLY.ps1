# TuringCapture CI/CD Local Testing Script
# Test the complete CI/CD pipeline locally before pushing to GitHub
# Run this from the TuringMachines root directory

param(
    [switch]$SkipTests = $false,
    [switch]$SkipLint = $false,
    [switch]$SkipDocker = $false,
    [switch]$Verbose = $false
)

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host " $Message" -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host ""
}

# Start
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " TuringCapture CI/CD Local Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Check prerequisites
Write-Step "Checking Prerequisites"

$allGood = $true

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Python not found"
    $allGood = $false
} else {
    $pythonVersion = python --version 2>&1
    Write-Success "Python: $pythonVersion"
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Docker not found"
    $allGood = $false
} else {
    $dockerVersion = docker --version
    Write-Success "Docker: $dockerVersion"
}

if (-not $allGood) {
    Write-Error-Custom "Missing prerequisites"
    exit 1
}

# Navigate to turing-capture
Write-Step "Navigating to turing-capture"

if (-not (Test-Path "turing-capture")) {
    Write-Error-Custom "turing-capture directory not found"
    Write-Info "Run this script from the TuringMachines root directory"
    exit 1
}

Push-Location turing-capture
Write-Success "In directory: $(Get-Location)"

# Setup virtual environment
Write-Step "Setting Up Virtual Environment"

if (-not (Test-Path ".venv")) {
    Write-Info "Creating virtual environment..."
    python -m venv .venv
    Write-Success "Virtual environment created"
} else {
    Write-Success "Virtual environment exists"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"
Write-Success "Virtual environment activated"

# Install dependencies
Write-Step "Installing Dependencies"

Write-Info "Installing production dependencies..."
pip install -q -r requirements.txt
Write-Success "Production dependencies installed"

Write-Info "Installing dev dependencies..."
pip install -q pytest pytest-cov black flake8 isort mypy
Write-Success "Dev dependencies installed"

# Run tests
if (-not $SkipTests) {
    Write-Step "Running Tests"
    
    Write-Info "Running pytest..."
    if ($Verbose) {
        pytest -v
    } else {
        pytest -q
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All tests passed"
    } else {
        Write-Error-Custom "Tests failed"
        Pop-Location
        exit 1
    }
} else {
    Write-Info "Skipping tests (--SkipTests)"
}

# Run linting
if (-not $SkipLint) {
    Write-Step "Running Code Quality Checks"
    
    Write-Info "Running flake8..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Flake8 critical checks passed"
    } else {
        Write-Error-Custom "Flake8 found critical issues"
    }
    
    Write-Info "Checking code formatting with black..."
    black --check .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Black formatting check passed"
    } else {
        Write-Info "Run 'black .' to format code"
    }
    
    Write-Info "Checking import sorting with isort..."
    isort --check-only .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Isort check passed"
    } else {
        Write-Info "Run 'isort .' to sort imports"
    }
    
    Write-Info "Running type checking with mypy..."
    mypy . --ignore-missing-imports
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Mypy type checking passed"
    } else {
        Write-Info "Type hints need attention"
    }
} else {
    Write-Info "Skipping linting (--SkipLint)"
}

# Build Docker image
if (-not $SkipDocker) {
    Write-Step "Building Docker Image"
    
    Write-Info "Building turing-capture:local..."
    docker build -t turing-capture:local .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    } else {
        Write-Error-Custom "Docker build failed"
        Pop-Location
        exit 1
    }
    
    # Test Docker container
    Write-Step "Testing Docker Container"
    
    Write-Info "Starting container..."
    docker run -d -p 8101:8101 --name turing-capture-test turing-capture:local
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container started"
        
        Write-Info "Waiting for service to be ready..."
        Start-Sleep -Seconds 5
        
        Write-Info "Testing health endpoint..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8101/health" -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "Health check passed"
                $health = $response.Content | ConvertFrom-Json
                Write-Host "  Service: $($health.service)"
                Write-Host "  Status: $($health.status)"
                Write-Host "  Version: $($health.version)"
            } else {
                Write-Error-Custom "Health check failed with status: $($response.StatusCode)"
            }
        } catch {
            Write-Error-Custom "Health check failed: $_"
        }
        
        Write-Info "Stopping container..."
        docker stop turing-capture-test | Out-Null
        docker rm turing-capture-test | Out-Null
        Write-Success "Container stopped and removed"
    } else {
        Write-Error-Custom "Failed to start container"
        Pop-Location
        exit 1
    }
} else {
    Write-Info "Skipping Docker build (--SkipDocker)"
}

# Summary
Pop-Location

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host " CI/CD Local Test Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

Write-Success "All checks passed"
Write-Info "Duration: $($duration.TotalSeconds) seconds"
Write-Host ""

Write-Info "Next steps:"
Write-Host "  1. Review any warnings above"
Write-Host "  2. Fix any issues"
Write-Host "  3. Commit and push to GitHub"
Write-Host "  4. Monitor GitHub Actions for CI/CD pipeline"
Write-Host ""

Write-Info "GitHub Actions will run:"
Write-Host "  - CI pipeline on every push/PR"
Write-Host "  - CD pipeline on push to main"
Write-Host "  - Security scan weekly"
Write-Host ""

Write-Info "View pipelines at:"
Write-Host "  https://github.com/TuringDynamics3000/TuringMachines/actions"
Write-Host ""
