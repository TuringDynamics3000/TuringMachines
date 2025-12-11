# TuringMachines Complete Setup and Test Script
# =============================================
# This script sets up PostgreSQL databases, installs dependencies,
# starts services, and runs end-to-end integration tests.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TuringMachines Setup & Test Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$POSTGRES_USER = "postgres"
$POSTGRES_PASSWORD = "postgres"
$POSTGRES_HOST = "localhost"
$POSTGRES_PORT = "5432"

$CAPTURE_DB = "turingcapture"
$ORCHESTRATE_DB = "turing_orchestrate"

$CAPTURE_PORT = 8101
$ORCHESTRATE_PORT = 8102

# Step 1: Create PostgreSQL Databases
Write-Host "[1/6] Creating PostgreSQL databases..." -ForegroundColor Yellow

$env:PGPASSWORD = $POSTGRES_PASSWORD

# Create databases
Write-Host "  → Creating database: $CAPTURE_DB"
psql -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT -c "DROP DATABASE IF EXISTS $CAPTURE_DB;" 2>$null
psql -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT -c "CREATE DATABASE $CAPTURE_DB;"

Write-Host "  → Creating database: $ORCHESTRATE_DB"
psql -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT -c "DROP DATABASE IF EXISTS $ORCHESTRATE_DB;" 2>$null
psql -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT -c "CREATE DATABASE $ORCHESTRATE_DB;"

# Install pgvector extension
Write-Host "  → Installing pgvector extension"
psql -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT -d $CAPTURE_DB -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null
psql -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT -d $ORCHESTRATE_DB -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null

Write-Host "  ✓ Databases created successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Install TuringCapture Dependencies
Write-Host "[2/6] Installing TuringCapture dependencies..." -ForegroundColor Yellow
Push-Location turing-capture

if (Test-Path "venv") {
    Write-Host "  → Removing old virtual environment"
    Remove-Item -Recurse -Force venv
}

Write-Host "  → Creating virtual environment"
python -m venv venv

Write-Host "  → Installing dependencies"
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt

Write-Host "  ✓ TuringCapture dependencies installed" -ForegroundColor Green
deactivate
Pop-Location
Write-Host ""

# Step 3: Install TuringOrchestrate Dependencies
Write-Host "[3/6] Installing TuringOrchestrate dependencies..." -ForegroundColor Yellow
Push-Location turing-orchestrate

if (Test-Path "venv") {
    Write-Host "  → Removing old virtual environment"
    Remove-Item -Recurse -Force venv
}

Write-Host "  → Creating virtual environment"
python -m venv venv

Write-Host "  → Installing dependencies"
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt aiosqlite greenlet

Write-Host "  ✓ TuringOrchestrate dependencies installed" -ForegroundColor Green
deactivate
Pop-Location
Write-Host ""

# Step 4: Start Services
Write-Host "[4/6] Starting services..." -ForegroundColor Yellow

# Set environment variables
$env:DATABASE_URL = "postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${CAPTURE_DB}"
$env:ORCHESTRATE_DATABASE_URL = "postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${ORCHESTRATE_DB}"
$env:ORCHESTRATE_URL = "http://localhost:${ORCHESTRATE_PORT}"
$env:RISK_BRAIN_URL = "http://localhost:8103"

# Start TuringCapture
Write-Host "  → Starting TuringCapture on port $CAPTURE_PORT"
Push-Location turing-capture
.\venv\Scripts\Activate.ps1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='$env:DATABASE_URL'; `$env:ORCHESTRATE_URL='$env:ORCHESTRATE_URL'; uvicorn main:app --host 0.0.0.0 --port $CAPTURE_PORT" -WindowStyle Minimized
deactivate
Pop-Location

Start-Sleep -Seconds 3

# Start TuringOrchestrate
Write-Host "  → Starting TuringOrchestrate on port $ORCHESTRATE_PORT"
Push-Location turing-orchestrate
.\venv\Scripts\Activate.ps1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:ORCHESTRATE_DATABASE_URL='$env:ORCHESTRATE_DATABASE_URL'; `$env:RISK_BRAIN_URL='$env:RISK_BRAIN_URL'; uvicorn main:app --host 0.0.0.0 --port $ORCHESTRATE_PORT" -WindowStyle Minimized
deactivate
Pop-Location

Write-Host "  → Waiting for services to start..."
Start-Sleep -Seconds 5

Write-Host "  ✓ Services started" -ForegroundColor Green
Write-Host ""

# Step 5: Health Checks
Write-Host "[5/6] Running health checks..." -ForegroundColor Yellow

$captureHealth = Invoke-RestMethod -Uri "http://localhost:${CAPTURE_PORT}/health" -Method Get -ErrorAction SilentlyContinue
if ($captureHealth.status -eq "ok") {
    Write-Host "  ✓ TuringCapture: HEALTHY" -ForegroundColor Green
} else {
    Write-Host "  ✗ TuringCapture: UNHEALTHY" -ForegroundColor Red
}

$orchestrateHealth = Invoke-RestMethod -Uri "http://localhost:${ORCHESTRATE_PORT}/health" -Method Get -ErrorAction SilentlyContinue
if ($orchestrateHealth.status -eq "ok") {
    Write-Host "  ✓ TuringOrchestrate: HEALTHY" -ForegroundColor Green
} else {
    Write-Host "  ✗ TuringOrchestrate: UNHEALTHY" -ForegroundColor Red
}

Write-Host ""

# Step 6: End-to-End Integration Test
Write-Host "[6/6] Running end-to-end integration test..." -ForegroundColor Yellow
Write-Host ""

# Create a test image (base64 encoded 1x1 pixel PNG)
$testImageBase64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
$testImageBytes = [Convert]::FromBase64String($testImageBase64)
$testImagePath = "$env:TEMP\test_selfie.png"
[IO.File]::WriteAllBytes($testImagePath, $testImageBytes)

Write-Host "  → Test 1: Upload selfie to TuringCapture" -ForegroundColor Cyan

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"selfie`"; filename=`"test.png`"",
    "Content-Type: image/png$LF",
    [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($testImageBytes),
    "--$boundary",
    "Content-Disposition: form-data; name=`"tenant_id`"$LF",
    "test_tenant_001",
    "--$boundary--$LF"
) -join $LF

try {
    $uploadResponse = Invoke-RestMethod -Uri "http://localhost:${CAPTURE_PORT}/v1/biometrics/upload" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines `
        -ErrorAction Stop

    Write-Host "    ✓ Selfie uploaded successfully" -ForegroundColor Green
    Write-Host "      Session ID: $($uploadResponse.session_id)" -ForegroundColor Gray
    Write-Host "      Liveness Score: $($uploadResponse.liveness.score)" -ForegroundColor Gray
    Write-Host "      Is Live: $($uploadResponse.liveness.is_live)" -ForegroundColor Gray

    $sessionId = $uploadResponse.session_id

    # Wait for event propagation
    Start-Sleep -Seconds 2

    Write-Host ""
    Write-Host "  → Test 2: Check workflow in TuringOrchestrate" -ForegroundColor Cyan

    $workflowResponse = Invoke-RestMethod -Uri "http://localhost:${ORCHESTRATE_PORT}/v1/orchestrate/workflows/${sessionId}" `
        -Method Get `
        -ErrorAction Stop

    Write-Host "    ✓ Workflow found in Orchestrate" -ForegroundColor Green
    Write-Host "      Workflow ID: $($workflowResponse.id)" -ForegroundColor Gray
    Write-Host "      State: $($workflowResponse.state)" -ForegroundColor Gray
    Write-Host "      Tenant ID: $($workflowResponse.tenant_id)" -ForegroundColor Gray

    Write-Host ""
    Write-Host "  → Test 3: List workflows by tenant" -ForegroundColor Cyan

    $workflowsResponse = Invoke-RestMethod -Uri "http://localhost:${ORCHESTRATE_PORT}/v1/orchestrate/workflows?tenant_id=test_tenant_001&limit=10" `
        -Method Get `
        -ErrorAction Stop

    Write-Host "    ✓ Workflows retrieved" -ForegroundColor Green
    Write-Host "      Total workflows: $($workflowsResponse.Count)" -ForegroundColor Gray

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

} catch {
    Write-Host "    ✗ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ TESTS FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Services are running:" -ForegroundColor Cyan
Write-Host "  • TuringCapture:    http://localhost:${CAPTURE_PORT}/docs" -ForegroundColor White
Write-Host "  • TuringOrchestrate: http://localhost:${ORCHESTRATE_PORT}/docs" -ForegroundColor White
Write-Host ""
Write-Host "To stop services, close the PowerShell windows or run:" -ForegroundColor Yellow
Write-Host "  Get-Process | Where-Object {`$_.CommandLine -like '*uvicorn*'} | Stop-Process" -ForegroundColor Gray
Write-Host ""
