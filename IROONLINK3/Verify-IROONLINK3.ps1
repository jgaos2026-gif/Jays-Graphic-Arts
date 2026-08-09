<#
.SYNOPSIS
    Verifies the health of the IROONLINK3 Control Room and all registered nodes.

.DESCRIPTION
    Checks that the Control Room API is reachable, then tests each registered
    node's registration state and last-seen timestamp. Exits with code 0 if
    all checks pass, 1 if any fail.

.PARAMETER ControlRoomUrl
    Base URL of the IROONLINK3 Control Room. Defaults to http://localhost:3000.

.PARAMETER MaxStaleSecs
    Seconds after which a node's lastSeen is considered stale. Defaults to 120.

.EXAMPLE
    .\Verify-IROONLINK3.ps1
    .\Verify-IROONLINK3.ps1 -ControlRoomUrl http://192.168.1.5:3000 -MaxStaleSecs 60
#>
[CmdletBinding()]
param(
    [string]$ControlRoomUrl = 'http://localhost:3000',
    [int]   $MaxStaleSecs   = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

$pass = 0
$fail = 0

function Check([string]$Label, [bool]$Ok, [string]$Detail = '') {
    if ($Ok) {
        Write-Host "  [PASS] $Label" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  [FAIL] $Label$(if ($Detail) { ' — ' + $Detail })" -ForegroundColor Red
        $script:fail++
    }
}

Write-Host "`nIROONLINK3 Verification" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "Control Room: $ControlRoomUrl`n"

# ── Check 1: server reachable ─────────────────────────────────────────────────
Write-Host "[ Server ]"
try {
    $status = Invoke-RestMethod "$ControlRoomUrl/api/status"
    Check "Server online" ($status.status -eq 'online')
    Check "Version present" (-not [string]::IsNullOrWhiteSpace($status.version))
} catch {
    Check "Server reachable" $false "Could not connect: $_"
    Write-Host "`nVerification FAILED — Control Room is not running." -ForegroundColor Red
    exit 1
}

# ── Check 2: node registry readable ──────────────────────────────────────────
Write-Host "`n[ Node Registry ]"
try {
    $nodes = Invoke-RestMethod "$ControlRoomUrl/api/nodes"
    Check "Node registry readable" $true
    Check "At least one node registered" ($nodes.Count -gt 0) "No nodes found"
} catch {
    Check "Node registry readable" $false "$_"
    $nodes = @()
}

# ── Check 3: per-node health ──────────────────────────────────────────────────
if ($nodes.Count -gt 0) {
    Write-Host "`n[ Node Health ]"
    $now = Get-Date
    foreach ($node in $nodes) {
        $id = $node.id
        $stale = $false
        if ($node.lastSeen) {
            $age = ($now - [datetime]$node.lastSeen).TotalSeconds
            $stale = $age -gt $MaxStaleSecs
        }
        $label = "$id ($($node.name))"
        Check "$label — status" ($node.status -ne 'offline') "status=$($node.status)"
        if ($node.lastSeen) {
            Check "$label — heartbeat fresh" (-not $stale) "last seen $([int]$age)s ago (limit ${MaxStaleSecs}s)"
        }
    }
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host "`n──────────────────────────────" -ForegroundColor Gray
if ($fail -eq 0) {
    Write-Host "All $pass check(s) passed." -ForegroundColor Green
    exit 0
} else {
    Write-Host "$fail check(s) FAILED, $pass passed." -ForegroundColor Red
    exit 1
}
