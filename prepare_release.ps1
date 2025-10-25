# Prepare Release Script (PowerShell)
# This script prepares your repository for a clean v1.0.0 release

param(
    [string]$Version = "v1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Preparing Release: $Version" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Clean build artifacts
Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, __pycache__
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter *.egg-info | Remove-Item -Recurse -Force

# Check git status
Write-Host ""
Write-Host "Current git status:" -ForegroundColor Yellow
git status --short

# Stage all changes
Write-Host ""
Write-Host "Staging all changes..." -ForegroundColor Yellow
git add .

# Show what will be committed
Write-Host ""
Write-Host "Changes to be committed:" -ForegroundColor Green
git status --short

# Prompt for commit message
Write-Host ""
$commit_msg = Read-Host "Enter commit message (press Enter for default: 'Prepare release $Version')"
if ([string]::IsNullOrWhiteSpace($commit_msg)) {
    $commit_msg = "Prepare release $Version"
}

# Commit
Write-Host ""
Write-Host "Committing changes..." -ForegroundColor Yellow
try {
    git commit -m $commit_msg
} catch {
    Write-Host "Nothing to commit or commit failed" -ForegroundColor Yellow
}

# Create tag
Write-Host ""
$confirm_tag = Read-Host "Create tag $Version? (yes/no)"
if ($confirm_tag -eq "yes") {
    git tag -a $Version -m "Release $Version"
    Write-Host "✅ Tag $Version created" -ForegroundColor Green

    # Show version that will be built
    Write-Host ""
    Write-Host "Version that will be built:" -ForegroundColor Cyan
    python -m setuptools_scm

    # Prompt to push
    Write-Host ""
    $confirm_push = Read-Host "Push to remote? (yes/no)"
    if ($confirm_push -eq "yes") {
        git push origin main
        git push origin $Version
        Write-Host "✅ Pushed to remote" -ForegroundColor Green
    }
} else {
    Write-Host "Tag creation skipped" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Release preparation complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\build_and_publish.ps1 -Mode test   # Test on TestPyPI" -ForegroundColor White
Write-Host "2. Run: .\build_and_publish.ps1 -Mode prod   # Publish to PyPI" -ForegroundColor White
