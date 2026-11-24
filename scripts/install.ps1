# Install math-modeling-championship as a user-level skill.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\install.ps1
$ErrorActionPreference = "Stop"

$src = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$dst = Join-Path $env:USERPROFILE ".agents\skills\math-modeling-championship"

Write-Host "Source: $src"
Write-Host "Target: $dst"

if (Test-Path $dst) {
    Write-Host "Target exists. Backing up to $dst.bak ..."
    if (Test-Path "$dst.bak") { Remove-Item "$dst.bak" -Recurse -Force }
    Copy-Item $dst "$dst.bak" -Recurse
    Remove-Item $dst -Recurse -Force
}

New-Item -ItemType Directory -Path (Split-Path -Parent $dst) -Force | Out-Null
# Copy content, excluding dev artifacts.
$exclude = @("__pycache__", ".git", ".pytest_cache")
Get-ChildItem $src | Where-Object { $exclude -notcontains $_.Name } | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $dst $_.Name) -Recurse -Force
}

Write-Host "Installed. Restart your Agent session so the skill is rediscovered."
Write-Host "Verify with: python `"$dst\scripts\doctor.py`" --project ."
