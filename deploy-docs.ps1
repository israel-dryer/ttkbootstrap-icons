# Deploy MkDocs documentation to GitHub Pages
# Usage: .\deploy-docs.ps1

Write-Host "Deploying MkDocs documentation to GitHub Pages..." -ForegroundColor Cyan

# Check if mkdocs is installed
try {
    $mkdocsVersion = mkdocs --version 2>&1
    Write-Host "Using $mkdocsVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: mkdocs is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Install with: pip install mkdocs mkdocs-material mkdocs-gen-files" -ForegroundColor Yellow
    exit 1
}

# Deploy documentation
Write-Host "`nDeploying documentation..." -ForegroundColor Yellow
mkdocs gh-deploy --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDocumentation deployed successfully!" -ForegroundColor Green
    Write-Host "View your documentation at the GitHub Pages URL for this repository." -ForegroundColor Cyan
} else {
    Write-Host "`nDeployment failed!" -ForegroundColor Red
    exit 1
}
