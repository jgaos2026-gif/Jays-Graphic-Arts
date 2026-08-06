<#
.SYNOPSIS
    Starts the IROONLINK3 Control Room web server.

.DESCRIPTION
    Installs Node.js dependencies (if needed) then launches server.js.
    The Control Room dashboard will be available at http://localhost:PORT.

.PARAMETER Port
    HTTP port to listen on. Defaults to 3000.

.EXAMPLE
    .\Start-ControlRoom.ps1
    .\Start-ControlRoom.ps1 -Port 8080
#>
[CmdletBinding()]
param(
    [int]$Port = 3000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "IROONLINK3 Control Room" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Verify Node.js is available
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js is not installed or not on PATH. Install it from https://nodejs.org"
    exit 1
}
$nodeVersion = node --version
Write-Host "Node.js: $nodeVersion" -ForegroundColor Green

# Install dependencies if node_modules is missing
$modulesPath = Join-Path $ScriptDir "node_modules"
if (-not (Test-Path $modulesPath)) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    Push-Location $ScriptDir
    npm install --silent
    Pop-Location
    Write-Host "Dependencies installed." -ForegroundColor Green
}

# Set environment and start server
$env:PORT = $Port
Write-Host "Starting server on http://localhost:$Port" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Gray

Push-Location $ScriptDir
try {
    node server.js
} finally {
    Pop-Location
}
