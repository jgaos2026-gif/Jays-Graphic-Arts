# IROONLINK3 — System Documentation

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois
**Version:** 1.0.0

---

## Overview

IROONLINK3 is the operational control layer for the Braided Computational Topology (BCT) research kernel.
It provides a web-based Control Room dashboard and a set of PowerShell management scripts for
registering, monitoring, and verifying Protection Nodes across the network.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Control Room (Node.js)                │
│  ┌────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │  index.html│  │   server.js API │  │ data/nodes   │  │
│  │ (dashboard)│◄─┤  /api/nodes     │◄─┤  .json       │  │
│  └────────────┘  │  /api/status    │  └──────────────┘  │
│                  └────────┬────────┘                     │
└───────────────────────────│──────────────────────────────┘
                            │ heartbeat PATCH
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
   Protection Node 1  Protection Node 2  Protection Node N
```

---

## Quick Start

### Windows (PowerShell)

```powershell
# 1. Install Node.js dependencies (first time only)
cd IROONLINK3
npm install

# 2. Start the Control Room
.\Start-ControlRoom.ps1

# 3. Open http://localhost:3000 in a browser

# 4. Start a Protection Node (in a separate terminal)
.\Start-ProtectionNode.ps1 -NodeId node-003 -NodeName "Tertiary Guardian" -Host 192.168.1.20 -Port 4003

# 5. Verify everything is healthy
.\Verify-IROONLINK3.ps1

# 6. Start the Watchdog (optional, monitors node heartbeats)
.\WATCHDOG.ps1
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/status` | Server heartbeat / version info |
| GET | `/api/nodes` | List all registered protection nodes |
| GET | `/api/nodes/:id` | Get a single node by ID |
| POST | `/api/nodes` | Register a new node |
| PATCH | `/api/nodes/:id/heartbeat` | Node check-in (updates `lastSeen`) |
| DELETE | `/api/nodes/:id` | Deregister a node |

### POST /api/nodes — request body

```json
{
  "id":   "node-003",
  "name": "Tertiary Guardian",
  "host": "192.168.1.20",
  "port": 4003
}
```

---

## Node States

| State | Meaning |
|-------|---------|
| `registered` | Node record created; not yet checked in |
| `online` | Node sent a heartbeat within the expected interval |
| `offline` | Node missed its heartbeat window (set by WATCHDOG) |

---

## Files

```
IROONLINK3/
├── server.js                  Express web server + REST API
├── package.json               Node.js project manifest
├── index.html                 Control Room dashboard (served as static file)
├── styles/
│   └── main.css               Dashboard stylesheet
├── data/
│   └── nodes.json             Persistent node registry (JSON flat-file)
├── scripts/
│   └── register-node.js       CLI helper to register a node
├── tests/
│   └── server.test.js         Built-in Node.js test runner tests
├── docs/
│   └── IROONLINK3.md          This file
├── Start-ControlRoom.ps1      Start the web server
├── Start-ProtectionNode.ps1   Register + heartbeat a protection node
├── Verify-IROONLINK3.ps1      Health-check all components
└── WATCHDOG.ps1               Periodic heartbeat monitor
```

---

## Running Tests

```powershell
# Install deps first
npm install

# Run tests
npm test
```

---

## Configuration

| Environment variable | Default | Description |
|----------------------|---------|-------------|
| `PORT` | `3000` | HTTP port for the Control Room server |
| `WATCHDOG_INTERVAL` | `30` | Seconds between WATCHDOG heartbeat checks |
| `WATCHDOG_TIMEOUT` | `90` | Seconds before a node is marked offline |
