Param( [Parameter(Mandatory = $true, Position = 0)] [string]$Package, [Parameter(Mandatory = $false)] [switch]$Dev, [Parameter(Mandatory = $false)] [string]$Version )

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
        # If building base package and no explicit -Version, try to infer from latest git tag
    if (-not $Version) {
        $baseNames = @('ttkbootstrap-icons', 'packages/ttkbootstrap-icons')
        foreach ($bn in $baseNames) {
            if ($pkgDir -like "*\$bn") {
                try {
                    Ensure-Tool git
                    $tag = (git describe --tags --abbrev=0).Trim()
                    if ($tag) {
                        $tag = $tag -replace '^v',''
                        if ($tag -match '^[0-9]+\.[0-9]+\.[0-9]+') {
                            $Version = $tag
                            Write-Host "> Using version from git tag: $Version" -ForegroundColor Yellow
                        }
                    }
                } catch {}
                break
            }
        }
    }
Push-Location $pkgDir
    if (Test-Path dist) { Remove-Item -Recurse -Force dist }
    if ($Version) { $env:SETUPTOOLS_SCM_PRETEND_VERSION = $Version }; python -m build; if ($Version) { Remove-Item Env:SETUPTOOLS_SCM_PRETEND_VERSION -ErrorAction SilentlyContinue }
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



