# TuringCapture UI - Local Development Script
# This script sets up and runs the TuringCapture UI locally

param(
    [switch]$Install,
    [switch]$Build,
    [switch]$Start
)

$ErrorActionPreference = "Stop"

# Navigate to UI directory
cd "$PSScriptRoot\turing-capture\ui"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " TuringCapture UI - Local Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[INFO] Checking Node.js..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Install dependencies if requested or package-lock.json doesn't exist
if ($Install -or -not (Test-Path "package-lock.json")) {
    Write-Host ""
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Cyan
    npm install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Build if requested
if ($Build) {
    Write-Host ""
    Write-Host "[INFO] Building for production..." -ForegroundColor Cyan
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Build complete" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Build failed" -ForegroundColor Red
        exit 1
    }
}

# Start production server if requested
if ($Start) {
    Write-Host ""
    Write-Host "[INFO] Starting production server..." -ForegroundColor Cyan
    npm start
    exit
}

# Default: Run development server
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host " Starting Development Server" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Server will start on: http://localhost:3001" -ForegroundColor Cyan
Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start dev server
npm run dev
