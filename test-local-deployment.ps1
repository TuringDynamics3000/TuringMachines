# TuringCapture Local Deployment Test Script
# ===========================================
# Tests the locally running TuringCapture container

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TuringCapture Deployment Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "http://localhost:8101"
$ContainerName = "turing-capture-local"

# Test 1: Health Check
Write-Host "[Test 1/5] Health Check..." -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET
    Write-Host "  ✓ Health check passed" -ForegroundColor Green
    Write-Host "    Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Verify ONNX models in container
Write-Host "[Test 2/5] Verifying ONNX models in container..." -ForegroundColor Yellow

$modelsOutput = docker exec $ContainerName ls -lh /app/models 2>&1

if ($modelsOutput -match "arcface.onnx" -and $modelsOutput -match "mobilefacenet.onnx") {
    Write-Host "  ✓ ONNX models found in container" -ForegroundColor Green
    Write-Host $modelsOutput | Select-String "onnx"
} else {
    Write-Host "  ✗ ONNX models not found in container" -ForegroundColor Red
    Write-Host $modelsOutput
}

Write-Host ""

# Test 3: Check container logs for model loading
Write-Host "[Test 3/5] Checking logs for model initialization..." -ForegroundColor Yellow

$logs = docker logs $ContainerName 2>&1 | Select-String -Pattern "ONNX|model|embedding" -Context 0,2

if ($logs -match "ONNX models loaded successfully" -or $logs -match "models loaded") {
    Write-Host "  ✓ Models loaded successfully" -ForegroundColor Green
} elseif ($logs -match "mock embedding") {
    Write-Host "  ⚠ Using mock embeddings (models not loaded)" -ForegroundColor Yellow
} else {
    Write-Host "  → Model loading status unclear, check logs:" -ForegroundColor Gray
}

Write-Host $logs
Write-Host ""

# Test 4: Database connection
Write-Host "[Test 4/5] Checking database connection..." -ForegroundColor Yellow

$dbLogs = docker logs $ContainerName 2>&1 | Select-String -Pattern "database|pgvector|DB" -SimpleMatch

if ($dbLogs -match "Database initialized" -or $dbLogs -match "pgvector") {
    Write-Host "  ✓ Database connection successful" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database connection status unclear" -ForegroundColor Yellow
}

Write-Host ""

# Test 5: API Documentation
Write-Host "[Test 5/5] Checking API documentation..." -ForegroundColor Yellow

try {
    $docs = Invoke-WebRequest -Uri "$BaseUrl/docs" -Method GET -UseBasicParsing
    if ($docs.StatusCode -eq 200) {
        Write-Host "  ✓ API docs accessible at $BaseUrl/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ API docs not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Deployment Test Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8101/docs in your browser" -ForegroundColor White
Write-Host "  2. Test the /v1/biometrics/upload-selfie endpoint" -ForegroundColor White
Write-Host "  3. Check logs: docker logs -f $ContainerName" -ForegroundColor White
Write-Host ""
