<#
.SYNOPSIS
    Starts a Protection Node and registers it with the IROONLINK3 Control Room.

.DESCRIPTION
    Registers the node via the REST API, then begins sending periodic heartbeats
    to the Control Room. Run this on each machine that should act as a protection node.

.PARAMETER NodeId
    Unique identifier for this node (e.g. "node-003").

.PARAMETER NodeName
    Human-readable name (e.g. "Tertiary Guardian").

.PARAMETER Host
    IP address or hostname of this machine as seen by the Control Room.

.PARAMETER Port
    Port this node will advertise. Defaults to 4000.

.PARAMETER ControlRoomUrl
    Base URL of the IROONLINK3 Control Room. Defaults to http://localhost:3000.

.PARAMETER HeartbeatInterval
    Seconds between heartbeat check-ins. Defaults to 30.

.EXAMPLE
    .\Start-ProtectionNode.ps1 -NodeId node-003 -NodeName "Tertiary Guardian" -Host 192.168.1.20
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$NodeId,
    [Parameter(Mandatory)][string]$NodeName,
    [Parameter(Mandatory)][string]$Host,
    [int]   $Port               = 4000,
    [string]$ControlRoomUrl     = 'http://localhost:3000',
    [int]   $HeartbeatInterval  = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Api([string]$Method, [string]$Path, $Body = $null) {
    $uri = "$ControlRoomUrl$Path"
    $params = @{ Uri = $uri; Method = $Method; ContentType = 'application/json' }
    if ($Body) { $params['Body'] = ($Body | ConvertTo-Json -Compress) }
    try {
        Invoke-RestMethod @params
    } catch {
        $_.Exception.Message
    }
}

Write-Host "IROONLINK3 Protection Node — $NodeId" -ForegroundColor Cyan
Write-Host "Control Room: $ControlRoomUrl" -ForegroundColor Gray

# Register (ignore 409 = already registered)
Write-Host "Registering node..." -ForegroundColor Yellow
try {
    $reg = Invoke-Api -Method POST -Path '/api/nodes' -Body @{
        id   = $NodeId
        name = $NodeName
        host = $Host
        port = $Port
    }
    Write-Host "Registered: $($reg.id) ($($reg.name))" -ForegroundColor Green
} catch {
    Write-Host "Note: node may already be registered. Continuing..." -ForegroundColor Yellow
}

# Heartbeat loop
Write-Host "Sending heartbeats every ${HeartbeatInterval}s. Press Ctrl+C to stop.`n" -ForegroundColor Cyan

while ($true) {
    try {
        $hb = Invoke-Api -Method PATCH -Path "/api/nodes/$NodeId/heartbeat"
        $ts = Get-Date -Format 'HH:mm:ss'
        Write-Host "[$ts] Heartbeat OK — status: $($hb.status)" -ForegroundColor Green
    } catch {
        $ts = Get-Date -Format 'HH:mm:ss'
        Write-Warning "[$ts] Heartbeat failed: $_"
    }
    Start-Sleep -Seconds $HeartbeatInterval
}
