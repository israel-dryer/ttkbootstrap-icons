# Builds one package and uploads it to TestPyPI.
#
# This used to publish to PyPI as well. It no longer does: releases go through
# `.github/workflows/release.yml`, triggered by a tag, authenticated by PyPI
# Trusted Publishing rather than by a token sitting in an environment variable.
# That workflow also runs a preflight this script never did. See RELEASE.md.
#
# What is left is the genuinely useful part - trying a package out on TestPyPI
# before its version is real and permanent.

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

    # packages/tkinter-icons-<key>
    $p2 = Join-Path 'packages' ("tkinter-icons-" + $Key)
    if (Test-Path (Join-Path $p2 'pyproject.toml')) { return (Resolve-Path $p2).Path }

    throw "Could not resolve package directory for '$Key'. Try: tkinter-icons-fa | fa | packages\tkinter-icons-fa"
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
        $baseNames = @('tkinter-icons', 'packages/tkinter-icons')
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

    # TestPyPI only. `-Dev` used to select it and is now the sole behaviour; it
    # is still accepted so existing muscle memory keeps working.
    $distGlob = Join-Path $pkgDir 'dist\*'
    Write-Host "> Uploading $distGlob to testpypi ..." -ForegroundColor Cyan
    twine upload -r testpypi $distGlob --non-interactive

    Write-Host "Done. To publish for real, push a tag - see RELEASE.md." -ForegroundColor Green
} catch {
    Write-Error $_
    exit 1
}



