# Communication Braid

> **Status:** See [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Carry messages between computational contexts with delivery proof, acknowledgment, retry history, and bidirectional confirmation.

## Intended Computational Role
The Communication Braid handles message passing with reliability guarantees. Every message carries a delivery record; every acknowledgment is evidence; every retry is logged.

## Strand Types
- **Message strand**: carries the message content
- **Delivery strand**: carries delivery confirmation
- **Acknowledgment strand**: carries recipient acknowledgment
- **Retry strand**: handles retransmission with history

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `COMM.SEND` | Send message with delivery tracking |
| `COMM.RECEIVE` | Record message receipt |
| `COMM.ACKNOWLEDGE` | Send acknowledgment with evidence |
| `COMM.RETRY` | Retransmit with prior attempt record |

## Direction of Information Flow
Bidirectional by design: message flows sender → receiver; acknowledgment flows receiver → sender.

## Invariants
1. Every sent message has a delivery record
2. Every retry is distinguishable from original send
3. Acknowledgments are evidence-backed

## Failure Modes and Recovery
**Delivery failure**: retry with evidence; archive if max retries exceeded.
**Acknowledgment timeout**: re-send with prior attempt reference.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
🔬 **DEFINED** — Formal definition complete; implementation planned Phase 3

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: TCP with application-level ACK. BCT adds structural delivery evidence beyond transport acknowledgment.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
