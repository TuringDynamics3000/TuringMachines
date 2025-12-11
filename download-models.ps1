# TuringMachines ONNX Model Download Script
# ==========================================
# Downloads pre-trained face recognition models from InsightFace
# and sets them up for TuringCapture service

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TuringMachines Model Download Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$MODELS_DIR = "turing-capture/models"
$TEMP_DIR = "$env:TEMP\turingmachines_models"
$BUFFALO_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

# Step 1: Create directories
Write-Host "[1/5] Creating directories..." -ForegroundColor Yellow

if (-not (Test-Path $MODELS_DIR)) {
    New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null
    Write-Host "  → Created $MODELS_DIR" -ForegroundColor Gray
}

if (-not (Test-Path $TEMP_DIR)) {
    New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null
    Write-Host "  → Created temp directory" -ForegroundColor Gray
}

Write-Host "  ✓ Directories ready" -ForegroundColor Green
Write-Host ""

# Step 2: Download buffalo_l model pack
Write-Host "[2/5] Downloading buffalo_l model pack (275 MB)..." -ForegroundColor Yellow
Write-Host "  → This may take a few minutes..." -ForegroundColor Gray

$zipPath = "$TEMP_DIR\buffalo_l.zip"

try {
    # Use WebClient for progress
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($BUFFALO_URL, $zipPath)
    
    Write-Host "  ✓ Download complete" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Download failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Download manually from:" -ForegroundColor Yellow
    Write-Host "  $BUFFALO_URL" -ForegroundColor White
    exit 1
}

Write-Host ""

# Step 3: Extract models
Write-Host "[3/5] Extracting models..." -ForegroundColor Yellow

try {
    Expand-Archive -Path $zipPath -DestinationPath $TEMP_DIR -Force
    Write-Host "  ✓ Extraction complete" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Copy recognition models to TuringCapture
Write-Host "[4/5] Setting up models for TuringCapture..." -ForegroundColor Yellow

# Buffalo_l contains multiple models, we need the recognition model
$buffaloDir = "$TEMP_DIR\buffalo_l"

if (Test-Path "$buffaloDir\w600k_r50.onnx") {
    # Copy and rename w600k_r50.onnx to arcface.onnx
    Copy-Item "$buffaloDir\w600k_r50.onnx" "$MODELS_DIR\arcface.onnx" -Force
    Write-Host "  ✓ Copied ArcFace model (w600k_r50.onnx → arcface.onnx)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ ArcFace model not found in buffalo_l pack" -ForegroundColor Yellow
}

# Check for MobileFaceNet alternative
if (Test-Path "$buffaloDir\w600k_mbf.onnx") {
    Copy-Item "$buffaloDir\w600k_mbf.onnx" "$MODELS_DIR\mobilefacenet.onnx" -Force
    Write-Host "  ✓ Copied MobileFaceNet model (w600k_mbf.onnx → mobilefacenet.onnx)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ MobileFaceNet model not found, will download separately..." -ForegroundColor Yellow
    
    # Download MobileFaceNet from alternative source
    $mobileFaceNetUrl = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip"
    $mobileZipPath = "$TEMP_DIR\buffalo_s.zip"
    
    Write-Host "  → Downloading buffalo_s (contains MobileFaceNet)..." -ForegroundColor Gray
    
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($mobileFaceNetUrl, $mobileZipPath)
        
        Expand-Archive -Path $mobileZipPath -DestinationPath "$TEMP_DIR\buffalo_s" -Force
        
        if (Test-Path "$TEMP_DIR\buffalo_s\w600k_mbf.onnx") {
            Copy-Item "$TEMP_DIR\buffalo_s\w600k_mbf.onnx" "$MODELS_DIR\mobilefacenet.onnx" -Force
            Write-Host "  ✓ Copied MobileFaceNet model" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠ Could not download MobileFaceNet, will use ArcFace only" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 5: Verify models
Write-Host "[5/5] Verifying models..." -ForegroundColor Yellow

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
    Write-Host "  ⚠ mobilefacenet.onnx: NOT FOUND (will use arcface only)" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Cleanup
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
    Write-Host "  2. Check logs for 'ONNX models loaded successfully'" -ForegroundColor White
    Write-Host "  3. Test face matching with real embeddings" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠ No models were successfully installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual download required:" -ForegroundColor Yellow
    Write-Host "  1. Download buffalo_l.zip from:" -ForegroundColor White
    Write-Host "     https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip" -ForegroundColor Gray
    Write-Host "  2. Extract and copy w600k_r50.onnx to $MODELS_DIR\arcface.onnx" -ForegroundColor White
    Write-Host ""
}
