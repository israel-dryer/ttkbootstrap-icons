Param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Package,

    [Parameter(Mandatory = $false)]
    [switch]$Dev
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-PackageDir {
    Param([string]$Key)

    # Direct path
    if (Test-Path (Join-Path $Key 'pyproject.toml')) { return (Resolve-Path $Key).Path }

    # packages/<key>
    $p1 = Join-Path 'packages' $Key
    if (Test-Path (Join-Path $p1 'pyproject.toml')) { return (Resolve-Path $p1).Path }

    # packages/ttkbootstrap-icons-<key>
    $p2 = Join-Path 'packages' ("ttkbootstrap-icons-" + $Key)
    if (Test-Path (Join-Path $p2 'pyproject.toml')) { return (Resolve-Path $p2).Path }

    throw "Could not resolve package directory for '$Key'. Try: ttkbootstrap-icons-fa | fa | packages\ttkbootstrap-icons-fa"
}

function Ensure-Tool {
    Param([string]$Tool)
    try { & $Tool --version *> $null } catch { throw "Required tool '$Tool' not found in PATH." }
}

try {
    $pkgDir = Resolve-PackageDir -Key $Package

    Ensure-Tool python
    Ensure-Tool twine

    if (-not $env:TWINE_USERNAME) { $env:TWINE_USERNAME = '__token__' }
    if (-not $env:TWINE_PASSWORD) {
        throw "TWINE_PASSWORD not set. Set your PyPI/TestPyPI token (e.g., `$env:TWINE_PASSWORD='pypi-xxxxxxxx'`)."
    }

    Write-Host "> Building $pkgDir ..." -ForegroundColor Cyan
    Push-Location $pkgDir
    if (Test-Path dist) { Remove-Item -Recurse -Force dist }
    python -m build
    Pop-Location

    $repo = if ($Dev) { 'testpypi' } else { 'pypi' }
    $distGlob = Join-Path $pkgDir 'dist\*'
    Write-Host "> Uploading $distGlob to $repo ..." -ForegroundColor Cyan
    if ($repo -eq 'pypi') {
        twine upload $distGlob --non-interactive
    } else {
        twine upload -r $repo $distGlob --non-interactive
    }

    Write-Host "Done." -ForegroundColor Green
} catch {
    Write-Error $_
    exit 1
}

