# TuringMachines™ GitHub Push Script
# This script pushes the TuringMachines repository to GitHub
# Usage: .\push-to-github.ps1

param(
    [string]$GitHubUsername = "TuringDynamics3000",
    [string]$RepositoryName = "TuringMachines",
    [string]$BranchName = "main",
    [switch]$CreateRepository = $false
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

# Main script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "TuringMachines™ GitHub Push" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Info "Checking for Git installation..."
try {
    $gitVersion = git --version
    Write-Success "Git found: $gitVersion"
} catch {
    Write-Error-Custom "Git is not installed or not in PATH"
    Write-Info "Please install Git from https://git-scm.com/download/win"
    exit 1
}

# Check if we're in a Git repository
Write-Info "Checking if we're in a Git repository..."
if (-not (Test-Path ".git")) {
    Write-Error-Custom "Not in a Git repository. Please run this script from the TuringMachines directory."
    exit 1
}
Write-Success "Git repository found"

# Check Git status
Write-Info "Checking Git status..."
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Warning-Custom "You have uncommitted changes:"
    Write-Host $gitStatus
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y") {
        Write-Info "Cancelled by user"
        exit 0
    }
}
Write-Success "Git status is clean"

# Display repository information
Write-Host ""
Write-Info "Repository Configuration:"
Write-Host "  GitHub Username: $GitHubUsername"
Write-Host "  Repository Name: $RepositoryName"
Write-Host "  Branch Name: $BranchName"
Write-Host ""

# Confirm before proceeding
$confirm = Read-Host "Push to https://github.com/$GitHubUsername/$RepositoryName.git? (y/n)"
if ($confirm -ne "y") {
    Write-Info "Cancelled by user"
    exit 0
}

# Add remote origin if it doesn't exist
Write-Info "Checking for remote origin..."
$remoteUrl = "https://github.com/$GitHubUsername/$RepositoryName.git"
$existingRemote = git remote get-url origin 2>$null

if ($existingRemote -and $existingRemote -ne $remoteUrl) {
    Write-Warning-Custom "Remote 'origin' already exists with different URL: $existingRemote"
    $response = Read-Host "Remove and recreate remote? (y/n)"
    if ($response -eq "y") {
        Write-Info "Removing existing remote..."
        git remote remove origin
        Write-Success "Remote removed"
    } else {
        Write-Info "Cancelled by user"
        exit 0
    }
}

if (-not $existingRemote -or $existingRemote -ne $remoteUrl) {
    Write-Info "Adding remote origin..."
    git remote add origin $remoteUrl
    Write-Success "Remote added: $remoteUrl"
} else {
    Write-Success "Remote already configured: $remoteUrl"
}

# Rename branch to main if needed
Write-Info "Checking current branch..."
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "  Current branch: $currentBranch"

if ($currentBranch -ne $BranchName) {
    Write-Info "Renaming branch to $BranchName..."
    git branch -M $BranchName
    Write-Success "Branch renamed to $BranchName"
} else {
    Write-Success "Already on branch $BranchName"
}

# Push to GitHub
Write-Host ""
Write-Info "Pushing to GitHub..."
Write-Host "  Repository: $remoteUrl"
Write-Host "  Branch: $BranchName"
Write-Host ""

try {
    git push -u origin $BranchName
    Write-Success "Successfully pushed to GitHub!"
} catch {
    Write-Error-Custom "Failed to push to GitHub"
    Write-Host "Error: $_"
    Write-Info "Possible solutions:"
    Write-Host "  1. Check your GitHub credentials"
    Write-Host "  2. Ensure the repository exists on GitHub"
    Write-Host "  3. Check your internet connection"
    Write-Host "  4. Try: git push -u origin $BranchName"
    exit 1
}

# Display summary
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Push Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Success "Repository pushed successfully"
Write-Host ""
Write-Info "Next steps:"
Write-Host "  1. Visit: https://github.com/$GitHubUsername/$RepositoryName"
Write-Host "  2. Configure repository settings on GitHub"
Write-Host "  3. Add team members as collaborators"
Write-Host "  4. Set up branch protection rules"
Write-Host ""
Write-Info "For more information, see:"
Write-Host "  - README.md - Platform overview"
Write-Host "  - DEVELOPER_RUNBOOK.md - Development guide"
Write-Host "  - ARCHITECTURE.md - System architecture"
Write-Host ""
