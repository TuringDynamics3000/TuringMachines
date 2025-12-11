# TuringCapture Local Docker Deployment Script
# =============================================
# Runs TuringCapture locally with Docker, ONNX models, and Aurora database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TuringCapture Local Docker Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$AWSRegion = "ap-southeast-2"
$DBHost    = "turingcapture-aurora.cluster-cvyyew6ce7us.ap-southeast-2.rds.amazonaws.com"
$DBUser    = "postgres"
$DBPass    = "TuringCapture123!"
$DBName    = "postgres"

$DATABASE_URL = "postgresql+asyncpg://${DBUser}:${DBPass}@${DBHost}:5432/${DBName}"
$DockerImage  = "turing-capture:latest"
$ContainerName = "turing-capture-local"
$Port = 8101

# Step 1: Verify prerequisites
Write-Host "[1/7] Verifying prerequisites..." -ForegroundColor Yellow

# Check Docker
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "  ✗ Docker is not running" -ForegroundColor Red
    Write-Host "  → Please start Docker Desktop and try again" -ForegroundColor Gray
    exit 1
}
Write-Host "  ✓ Docker is running" -ForegroundColor Green

# Check if in correct directory
if (-not (Test-Path "turing-capture")) {
    Write-Host "  ✗ Not in TuringMachines root directory" -ForegroundColor Red
    Write-Host "  → Please run this script from the TuringMachines root directory" -ForegroundColor Gray
    exit 1
}
Write-Host "  ✓ In correct directory" -ForegroundColor Green

Write-Host ""

# Step 2: Verify ONNX models
Write-Host "[2/7] Checking ONNX models..." -ForegroundColor Yellow

$modelsDir = "turing-capture\models"
$arcfaceExists = Test-Path "$modelsDir\arcface.onnx"
$mobilefacenetExists = Test-Path "$modelsDir\mobilefacenet.onnx"

if ($arcfaceExists -and $mobilefacenetExists) {
    $arcfaceSize = (Get-Item "$modelsDir\arcface.onnx").Length / 1MB
    $mobileSize = (Get-Item "$modelsDir\mobilefacenet.onnx").Length / 1MB
    
    Write-Host "  ✓ arcface.onnx: $([math]::Round($arcfaceSize, 2)) MB" -ForegroundColor Green
    Write-Host "  ✓ mobilefacenet.onnx: $([math]::Round($mobileSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  ✗ ONNX models missing in $modelsDir" -ForegroundColor Red
    Write-Host "  → Run .\download-models-fixed.ps1 first" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Step 3: Stop existing container
Write-Host "[3/7] Stopping existing container..." -ForegroundColor Yellow

$existingContainer = docker ps -a -q -f name=$ContainerName
if ($existingContainer) {
    docker stop $ContainerName 2>$null | Out-Null
    docker rm $ContainerName 2>$null | Out-Null
    Write-Host "  ✓ Stopped and removed existing container" -ForegroundColor Green
} else {
    Write-Host "  → No existing container found" -ForegroundColor Gray
}

Write-Host ""

# Step 4: Build Docker image
Write-Host "[4/7] Building Docker image..." -ForegroundColor Yellow
Write-Host "  → This may take a few minutes..." -ForegroundColor Gray

Push-Location turing-capture

$buildOutput = docker build -t $DockerImage . 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Docker build failed" -ForegroundColor Red
    Write-Host $buildOutput
    Pop-Location
    exit 1
}

Pop-Location
Write-Host ""

# Step 5: Run container
Write-Host "[5/7] Starting TuringCapture container..." -ForegroundColor Yellow
Write-Host "  → Container: $ContainerName" -ForegroundColor Gray
Write-Host "  → Port: $Port" -ForegroundColor Gray
Write-Host "  → Database: $DBHost" -ForegroundColor Gray

docker run -d `
    --name $ContainerName `
    -e DATABASE_URL=$DATABASE_URL `
    -e ORCHESTRATE_URL="http://host.docker.internal:8102" `
    -p ${Port}:8101 `
    -v "${PWD}\turing-capture\models:/app/models" `
    $DockerImage

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Container started successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to start container" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 6: Wait for service to be ready
Write-Host "[6/7] Waiting for service to be ready..." -ForegroundColor Yellow

$maxRetries = 30
$retryCount = 0
$serviceReady = $false

while ($retryCount -lt $maxRetries -and -not $serviceReady) {
    Start-Sleep -Seconds 2
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:${Port}/health" -Method GET -ErrorAction SilentlyContinue
        if ($response.status -eq "ok") {
            $serviceReady = $true
        }
    } catch {
        $retryCount++
        Write-Host "  → Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    }
}

if ($serviceReady) {
    Write-Host "  ✓ Service is ready!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Service failed to start" -ForegroundColor Red
    Write-Host "  → Checking logs..." -ForegroundColor Gray
    docker logs $ContainerName
    exit 1
}

Write-Host ""

# Step 7: Run health check
Write-Host "[7/7] Running health check..." -ForegroundColor Yellow

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:${Port}/health" -Method GET
    Write-Host "  ✓ Health check passed" -ForegroundColor Green
    Write-Host "    Status: $($healthResponse.status)" -ForegroundColor Gray
    Write-Host "    Service: $($healthResponse.service)" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ TuringCapture is Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service Details:" -ForegroundColor Cyan
Write-Host "  • API:          http://localhost:${Port}" -ForegroundColor White
Write-Host "  • Docs:         http://localhost:${Port}/docs" -ForegroundColor White
Write-Host "  • Container:    $ContainerName" -ForegroundColor White
Write-Host "  • Database:     $DBHost" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  • View logs:    docker logs -f $ContainerName" -ForegroundColor Gray
Write-Host "  • Stop:         docker stop $ContainerName" -ForegroundColor Gray
Write-Host "  • Restart:      docker restart $ContainerName" -ForegroundColor Gray
Write-Host "  • Shell:        docker exec -it $ContainerName sh" -ForegroundColor Gray
Write-Host ""
Write-Host "To verify ONNX models in container:" -ForegroundColor Yellow
Write-Host "  docker exec -it $ContainerName ls -lh /app/models" -ForegroundColor Gray
Write-Host ""
