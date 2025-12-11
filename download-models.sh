#!/bin/bash
# TuringMachines ONNX Model Download Script
# ==========================================
# Downloads pre-trained face recognition models from InsightFace
# and sets them up for TuringCapture service

set -e

echo "========================================"
echo "TuringMachines Model Download Script"
echo "========================================"
echo ""

# Configuration
MODELS_DIR="turing-capture/models"
TEMP_DIR="/tmp/turingmachines_models"
BUFFALO_URL="https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

# Step 1: Create directories
echo "[1/5] Creating directories..."

mkdir -p "$MODELS_DIR"
mkdir -p "$TEMP_DIR"

echo "  ✓ Directories ready"
echo ""

# Step 2: Download buffalo_l model pack
echo "[2/5] Downloading buffalo_l model pack (275 MB)..."
echo "  → This may take a few minutes..."

cd "$TEMP_DIR"

if command -v wget &> /dev/null; then
    wget -q --show-progress "$BUFFALO_URL" -O buffalo_l.zip
elif command -v curl &> /dev/null; then
    curl -L --progress-bar "$BUFFALO_URL" -o buffalo_l.zip
else
    echo "  ✗ Error: Neither wget nor curl is available"
    echo "  Please install wget or curl and try again"
    exit 1
fi

echo "  ✓ Download complete"
echo ""

# Step 3: Extract models
echo "[3/5] Extracting models..."

unzip -q buffalo_l.zip

echo "  ✓ Extraction complete"
echo ""

# Step 4: Copy recognition models to TuringCapture
echo "[4/5] Setting up models for TuringCapture..."

cd - > /dev/null

# Buffalo_l contains multiple models, we need the recognition model
BUFFALO_DIR="$TEMP_DIR/buffalo_l"

if [ -f "$BUFFALO_DIR/w600k_r50.onnx" ]; then
    cp "$BUFFALO_DIR/w600k_r50.onnx" "$MODELS_DIR/arcface.onnx"
    echo "  ✓ Copied ArcFace model (w600k_r50.onnx → arcface.onnx)"
else
    echo "  ⚠ ArcFace model not found in buffalo_l pack"
fi

# Check for MobileFaceNet alternative
if [ -f "$BUFFALO_DIR/w600k_mbf.onnx" ]; then
    cp "$BUFFALO_DIR/w600k_mbf.onnx" "$MODELS_DIR/mobilefacenet.onnx"
    echo "  ✓ Copied MobileFaceNet model (w600k_mbf.onnx → mobilefacenet.onnx)"
else
    echo "  ⚠ MobileFaceNet model not found, will download separately..."
    
    # Download MobileFaceNet from alternative source
    cd "$TEMP_DIR"
    
    echo "  → Downloading buffalo_s (contains MobileFaceNet)..."
    
    if command -v wget &> /dev/null; then
        wget -q --show-progress "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip" -O buffalo_s.zip
    else
        curl -L --progress-bar "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip" -o buffalo_s.zip
    fi
    
    unzip -q buffalo_s.zip -d buffalo_s
    
    if [ -f "$TEMP_DIR/buffalo_s/w600k_mbf.onnx" ]; then
        cp "$TEMP_DIR/buffalo_s/w600k_mbf.onnx" "$MODELS_DIR/mobilefacenet.onnx"
        echo "  ✓ Copied MobileFaceNet model"
    fi
    
    cd - > /dev/null
fi

echo ""

# Step 5: Verify models
echo "[5/5] Verifying models..."

if [ -f "$MODELS_DIR/arcface.onnx" ]; then
    ARCFACE_SIZE=$(du -h "$MODELS_DIR/arcface.onnx" | cut -f1)
    echo "  ✓ arcface.onnx: $ARCFACE_SIZE"
else
    echo "  ✗ arcface.onnx: NOT FOUND"
fi

if [ -f "$MODELS_DIR/mobilefacenet.onnx" ]; then
    MOBILE_SIZE=$(du -h "$MODELS_DIR/mobilefacenet.onnx" | cut -f1)
    echo "  ✓ mobilefacenet.onnx: $MOBILE_SIZE"
else
    echo "  ⚠ mobilefacenet.onnx: NOT FOUND (will use arcface only)"
fi

echo ""

# Step 6: Cleanup
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "✓ Model Setup Complete!"
echo "========================================"
echo ""

if [ -f "$MODELS_DIR/arcface.onnx" ] || [ -f "$MODELS_DIR/mobilefacenet.onnx" ]; then
    echo "Models installed at: $MODELS_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Restart TuringCapture service"
    echo "  2. Check logs for 'ONNX models loaded successfully'"
    echo "  3. Test face matching with real embeddings"
    echo ""
else
    echo "⚠ No models were successfully installed"
    echo ""
    echo "Manual download required:"
    echo "  1. Download buffalo_l.zip from:"
    echo "     https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
    echo "  2. Extract and copy w600k_r50.onnx to $MODELS_DIR/arcface.onnx"
    echo ""
fi
