# Braided AI Architecture

> **[HYPOTHESIS]** throughout unless labeled **[CS-TRAJECTORY]**  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## The Problem

**[CS-TRAJECTORY]** AI systems face growing requirements for explainability, provenance, authority tracking, auditability, and recovery. These are currently addressed through separate overlays: RAG for provenance, RLHF for authority, chain-of-thought for reasoning transparency, separate logging for audit.

**[HYPOTHESIS]** A braided AI architecture carries these requirements natively through defined braid families cooperating as one runtime.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              BRAIDED AI RUNTIME                  │
│                                                  │
│  Evidence Braid ──────────────────────────────── │
│  Hypothesis Braid ──── Verification Braid ─────  │
│  Authority Braid ──────────────────────────────  │
│  Memory Braid ─────────────────────────────────  │
│  Recovery Braid ───────────────────────────────  │
│  Consensus Braid (multi-agent) ─────────────────  │
│  Output Braid ─────────────────────────────────  │
└─────────────────────────────────────────────────┘
           ↓ promotes only certified results
         OUTPUT (with provenance chain attached)
```

---

## Braid Families in the AI Context

| Family | AI Function |
|---|---|
| Evidence Braid | Carries sources, citations, and data provenance |
| Hypothesis Braid | Generates candidate conclusions (all ACTIVE until verified) |
| Verification Braid | Challenges candidates against independent evidence |
| Authority Braid | Enforces source credibility ordering and instruction priority |
| Memory Braid | Hot: current context; Warm: recent sessions; Cold: full history |
| Recovery Braid | Rewinds reasoning after contradiction; preserves contradiction record |
| Consensus Braid | Reconciles multiple specialized reasoning agents |
| Output Braid | Promotes only certified conclusions to external output |

---

## Bidirectional Reasoning

**[HYPOTHESIS]**

```
Forward:   evidence → interpretation → candidate → verify → output
Reverse:   output → contradiction check → source validation → correction
```

The reverse path does not regenerate a new answer. It inspects the specific path that produced the original answer, identifies the earliest point of failure, and corrects there.

---

## Current Status

**SPECULATIVE** — No implementation exists. This is a research direction, not a current result.  
See `CLAIMS_REGISTER.md` — BCT-020.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
