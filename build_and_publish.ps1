# Build and Publish Script for ttkbootstrap-icons (PowerShell)
# Usage: .\build_and_publish.ps1 [-Mode test|prod]

param(
    [string]$Mode = "test"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Building ttkbootstrap-icons" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, src\*.egg-info

# Build the package
Write-Host "Building package..." -ForegroundColor Yellow
python -m build

# List the built files
Write-Host ""
Write-Host "Built files:" -ForegroundColor Green
Get-ChildItem dist\ | Format-Table Name, Length, LastWriteTime

# Upload based on mode
if ($Mode -eq "prod") {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Uploading to PyPI (PRODUCTION)" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Cyan
    $confirm = Read-Host "Are you sure you want to upload to PyPI? (yes/no)"
    if ($confirm -eq "yes") {
        python -m twine upload dist\*
        Write-Host ""
        Write-Host "✅ Successfully published to PyPI!" -ForegroundColor Green
        Write-Host "Visit: https://pypi.org/project/ttkbootstrap-icons/" -ForegroundColor Cyan
    } else {
        Write-Host "Upload cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Uploading to TestPyPI" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    python -m twine upload --repository testpypi dist\*
    Write-Host ""
    Write-Host "✅ Successfully published to TestPyPI!" -ForegroundColor Green
    Write-Host "Test installation:" -ForegroundColor Cyan
    Write-Host "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ttkbootstrap-icons" -ForegroundColor White
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green