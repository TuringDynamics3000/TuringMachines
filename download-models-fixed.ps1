# TuringMachines ONNX Model Download Script (Fixed)
# ===================================================
# Downloads pre-trained face recognition models from InsightFace

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TuringMachines Model Download Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$MODELS_DIR = "turing-capture\models"
$TEMP_DIR = "$env:TEMP\turingmachines_models"
$BUFFALO_L_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
$BUFFALO_S_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip"

# Step 1: Create directories
Write-Host "[1/4] Creating directories..." -ForegroundColor Yellow

if (-not (Test-Path $MODELS_DIR)) {
    New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null
}

if (Test-Path $TEMP_DIR) {
    Remove-Item -Recurse -Force $TEMP_DIR
}
New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null

Write-Host "  ✓ Directories ready" -ForegroundColor Green
Write-Host ""

# Step 2: Download and extract buffalo_l (ArcFace model)
Write-Host "[2/4] Downloading buffalo_l (ArcFace - 275 MB)..." -ForegroundColor Yellow

$buffaloLZip = "$TEMP_DIR\buffalo_l.zip"

try {
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($BUFFALO_L_URL, $buffaloLZip)
    
    Write-Host "  ✓ Download complete" -ForegroundColor Green
    Write-Host "  → Extracting..." -ForegroundColor Gray
    
    Expand-Archive -Path $buffaloLZip -DestinationPath "$TEMP_DIR\buffalo_l" -Force
    
    # Copy ArcFace model (w600k_r50.onnx)
    if (Test-Path "$TEMP_DIR\buffalo_l\w600k_r50.onnx") {
        Copy-Item "$TEMP_DIR\buffalo_l\w600k_r50.onnx" "$MODELS_DIR\arcface.onnx" -Force
        Write-Host "  ✓ ArcFace model installed (167 MB)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ ArcFace model not found" -ForegroundColor Red
    }
    
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Step 3: Download and extract buffalo_s (MobileFaceNet model)
Write-Host "[3/4] Downloading buffalo_s (MobileFaceNet - 122 MB)..." -ForegroundColor Yellow

$buffaloSZip = "$TEMP_DIR\buffalo_s.zip"

try {
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($BUFFALO_S_URL, $buffaloSZip)
    
    Write-Host "  ✓ Download complete" -ForegroundColor Green
    Write-Host "  → Extracting..." -ForegroundColor Gray
    
    Expand-Archive -Path $buffaloSZip -DestinationPath "$TEMP_DIR\buffalo_s" -Force
    
    # Copy MobileFaceNet model (w600k_mbf.onnx)
    if (Test-Path "$TEMP_DIR\buffalo_s\w600k_mbf.onnx") {
        Copy-Item "$TEMP_DIR\buffalo_s\w600k_mbf.onnx" "$MODELS_DIR\mobilefacenet.onnx" -Force
        Write-Host "  ✓ MobileFaceNet model installed (13 MB)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MobileFaceNet model not found" -ForegroundColor Red
    }
    
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Step 4: Verify installation
Write-Host "[4/4] Verifying models..." -ForegroundColor Yellow

$arcfaceExists = Test-Path "$MODELS_DIR\arcface.onnx"
$mobilefacenetExists = Test-Path "$MODELS_DIR\mobilefacenet.onnx"

if ($arcfaceExists) {
    $arcfaceSize = (Get-Item "$MODELS_DIR\arcface.onnx").Length / 1MB
    Write-Host "  ✓ arcface.onnx: $([math]::Round($arcfaceSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  ✗ arcface.onnx: NOT FOUND" -ForegroundColor Red
}

if ($mobilefacenetExists) {
    $mobileSize = (Get-Item "$MODELS_DIR\mobilefacenet.onnx").Length / 1MB
    Write-Host "  ✓ mobilefacenet.onnx: $([math]::Round($mobileSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  ✗ mobilefacenet.onnx: NOT FOUND" -ForegroundColor Red
}

Write-Host ""

# Cleanup
Write-Host "Cleaning up temporary files..." -ForegroundColor Gray
Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Model Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($arcfaceExists -or $mobilefacenetExists) {
    Write-Host "Models installed at: $MODELS_DIR" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart TuringCapture service" -ForegroundColor White
    Write-Host "  2. Check logs - you should see:" -ForegroundColor White
    Write-Host "     '✅ ONNX models loaded successfully'" -ForegroundColor Gray
    Write-Host "  3. Test face matching with real embeddings" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠ No models were successfully installed" -ForegroundColor Red
}
