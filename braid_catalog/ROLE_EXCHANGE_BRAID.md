# Role Exchange Braid

> **Status:** See [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Transfer authority tokens between strands atomically, with full verification and evidence, so that capability moves cleanly without duplication or silent loss.

## Intended Computational Role
The Role Exchange Braid implements capability transfer. When a role (authority) must move from one computational agent to another, the Role Exchange Braid atomically removes it from the source and delivers it to the target with full evidence.

## Strand Types
- **Source strand**: carries authority token to be transferred
- **Target strand**: receives transferred token
- **Verification strand**: confirms transfer validity
- **Evidence strand**: permanent transfer record

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `ROLE.TRANSFER` | Move authority token from source to target strand |
| `ROLE.DELEGATE` | Create scoped sub-authority from parent token |
| `ROLE.REVOKE` | Remove authority token from strand |
| `ROLE.VERIFY_ROLE` | Confirm token ownership |

## Direction of Information Flow
Unidirectional at transfer time (token moves from source to target). Evidence flows to both strands.

## Invariants
1. Token count is conserved: source loses token when target gains it
2. Transfer is atomic: no state where token exists on neither or both strands
3. Every transfer is recorded with full evidence

## Failure Modes and Recovery
**Source lacks token**: deny transfer; record attempt as authority violation.
**Target strand invalid**: deny transfer; quarantine.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
✅ **IMPLEMENTED** — `braid_simulator/authority.py`

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: sudo/setuid for role elevation; session tokens for capability delegation. BCT makes the transfer atomic and evidence-bound.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
