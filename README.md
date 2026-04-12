# Jays-Graphic-Arts

> **The world's first fully Autonomous AI-run graphic arts company — complete business cycles, zero compromise on compliance.**

Jays-Graphic-Arts operates every function of a professional graphic design studio through a custom Autonomous AI platform: from lead capture and client communication, through creative production and quality assurance, all the way to invoicing, payment reconciliation, and regulatory reporting — without human bottlenecks.

---

## Documentation

| Document | Description |
|---|---|
| [AI Reliability](docs/AI_RELIABILITY.md) | How we engineered the AI to be trustworthy, resilient, and auditable |
| [AI Capabilities](docs/AI_CAPABILITIES.md) | Everything the AI can do across the full business |
| [Compliance Framework](docs/COMPLIANCE.md) | Legal, data-privacy, copyright, and financial compliance |
| [Business Cycles](docs/BUSINESS_CYCLES.md) | End-to-end automated business workflow overview |

---

## Quick Start

1. Read [AI Capabilities](docs/AI_CAPABILITIES.md) to see what the system can do.
2. Read [AI Reliability](docs/AI_RELIABILITY.md) to understand how we ensure accuracy and safety.
3. Read [Compliance Framework](docs/COMPLIANCE.md) to understand legal boundaries.
4. Read [Business Cycles](docs/BUSINESS_CYCLES.md) for the full operational picture.

---

## About

Jays-Graphic-Arts was founded on the principle that a small studio can deliver enterprise-grade design services at scale by pairing human creative direction with autonomous AI execution. Every policy, safeguard, and capability listed in this documentation reflects the real system in production.

---

## Core Backend (Now Implemented)

The repository now includes a runnable HTTP backend:

- `GET /` service info
- `GET /health` health check
- `GET /api` API index
- `GET/POST /api/leads`
- `GET/POST /api/projects`
- `GET/POST /api/invoices`

### Run

1. `npm install` (no external dependencies currently)
2. `npm start`
3. Open `http://localhost:3000/health`

### Test

1. `npm test`

### Numbered Completion Checklist

1. [x] Scaffold backend project (`package.json`)
2. [x] Create core HTTP server
3. [x] Implement lead/project/invoice API routes
4. [x] Add payload validation and error handling
5. [x] Add automated backend tests
6. [x] Document run and test workflow
7. [ ] Provision and attach a free public domain (requires external registrar/DNS account and deployment target)
