# TuringMachines™ Service Runner Script
# Easily start and manage individual services
# Usage: .\run-services.ps1 -Service turing-riskbrain

param(
    [ValidateSet("turing-capture", "turing-orchestrate", "turing-policy", "turing-riskbrain", "turing-ml", "turing-settleguard", "turing-investigator", "all")]
    [string]$Service = "all",
    [int]$Port = 0,
    [switch]$Frontend = $false
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

# Service configuration
$services = @{
    "turing-capture" = @{
        port = 8101
        description = "Identity & document capture"
        entry = "app.main:app"
    }
    "turing-orchestrate" = @{
        port = 8102
        description = "Flow orchestration engine"
        entry = "app.main:app"
    }
    "turing-policy" = @{
        port = 8104
        description = "Jurisdiction policy management"
        entry = "app.main:app"
    }
    "turing-riskbrain" = @{
        port = 8103
        description = "Fused risk intelligence"
        entry = "app.main:app"
    }
    "turing-ml" = @{
        port = 8108
        description = "Model registry & inference"
        entry = "turing_ml.api.main"
    }
    "turing-settleguard" = @{
        port = 8105
        description = "Settlement authority"
        entry = "app.main:app"
    }
    "turing-investigator" = @{
        port = 8107
        description = "Case management & graph explorer"
        entry = "api.main:app"
    }
}

# Display menu
function Show-Menu {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  TuringMachines™ Service Runner       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available Services:" -ForegroundColor Yellow
    Write-Host ""
    
    $i = 1
    foreach ($svc in $services.Keys) {
        $desc = $services[$svc].description
        $port = $services[$svc].port
        Write-Host "  $i. $svc (port $port)"
        Write-Host "     $desc"
        Write-Host ""
        $i++
    }
    
    Write-Host "  8. All Services (Docker Compose)"
    Write-Host ""
}

# Run single service
function Start-Service {
    param(
        [string]$ServiceName,
        [int]$ServicePort
    )
    
    if (-not (Test-Path $ServiceName)) {
        Write-Error-Custom "Service directory not found: $ServiceName"
        return
    }
    
    Push-Location $ServiceName
    
    Write-Info "Starting $ServiceName..."
    Write-Host "  Port: http://localhost:$ServicePort/docs"
    Write-Host ""
    
    # Activate virtual environment
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        & ".\.venv\Scripts\Activate.ps1"
    } else {
        Write-Warning-Custom "Virtual environment not found. Run setup-local.ps1 first"
        Pop-Location
        return
    }
    
    # Get entry point
    $entry = $services[$ServiceName].entry
    
    # Run service
    Write-Success "Service running at http://localhost:$ServicePort/docs"
    Write-Info "Press Ctrl+C to stop"
    Write-Host ""
    
    uvicorn $entry --reload --port $ServicePort --host 0.0.0.0
    
    Pop-Location
}

# Run frontend
function Start-Frontend {
    param([string]$ServiceName)
    
    $uiPath = "$ServiceName\ui"
    
    if (-not (Test-Path $uiPath)) {
        Write-Error-Custom "Frontend directory not found: $uiPath"
        return
    }
    
    Push-Location $uiPath
    
    Write-Info "Starting $ServiceName frontend..."
    Write-Host "  URL: http://localhost:3000"
    Write-Host ""
    
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installing dependencies..."
        npm install
    }
    
    Write-Success "Frontend running at http://localhost:3000"
    Write-Info "Press Ctrl+C to stop"
    Write-Host ""
    
    npm start
    
    Pop-Location
}

# Run all services with Docker
function Start-AllServices {
    Write-Info "Starting all services with Docker Compose..."
    Write-Host ""
    
    if (-not (Test-Path "deploy\compose")) {
        Write-Error-Custom "Docker Compose directory not found"
        return
    }
    
    Push-Location "deploy\compose"
    
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  docker compose up --build      - Start all services"
    Write-Host "  docker compose down            - Stop all services"
    Write-Host "  docker compose logs -f         - View logs"
    Write-Host "  docker compose ps              - Show status"
    Write-Host ""
    
    Write-Info "Starting services..."
    Write-Host ""
    
    docker compose up --build
    
    Pop-Location
}

# Main logic
if ($Service -eq "all") {
    Show-Menu
    $choice = Read-Host "Select service to run (1-8)"
    
    switch ($choice) {
        "1" { Start-Service "turing-capture" 8101 }
        "2" { Start-Service "turing-orchestrate" 8102 }
        "3" { Start-Service "turing-policy" 8104 }
        "4" { Start-Service "turing-riskbrain" 8103 }
        "5" { Start-Service "turing-ml" 8108 }
        "6" { Start-Service "turing-settleguard" 8105 }
        "7" { Start-Service "turing-investigator" 8107 }
        "8" { Start-AllServices }
        default { Write-Error-Custom "Invalid selection" }
    }
} else {
    $servicePort = if ($Port -gt 0) { $Port } else { $services[$Service].port }
    
    if ($Frontend) {
        Start-Frontend $Service
    } else {
        Start-Service $Service $servicePort
    }
}
