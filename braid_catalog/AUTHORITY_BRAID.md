# AUTHORITY BRAID (AUTHORITY BRAID)

> **Status:** See  for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Enforce structural permission requirements so that no execution can proceed without the required authority token — not by policy, but by architectural construction.

## Intended Computational Role
The Authority Braid is the gatekeeper. Every state promotion passes through an authority crossing. The crossing either permits or denies based on the strand's authority token, and records the decision regardless of outcome.

## Strand Types
- **Token strand**: carries authority token\n- **State strand**: carries state awaiting authorization\n- **Verdict strand**: carries permit/deny result\n- **Evidence strand**: records all authority checks

## Crossing Semantics
| AUTH.CHECK | Verify strand has required authority |\n| AUTH.GATE | Block promotion without authority |\n| AUTH.INHERIT | Child strand inherits scoped authority from parent |\n| AUTH.SCOPE | Restrict authority to defined scope |

## Direction of Information Flow
Forward: authority check results flow toward the state promotion crossing. Bidirectional: denial evidence flows back to the requesting strand.

## Invariants
1. Every state promotion is preceded by AUTH.CHECK\n2. Authority tokens are not duplicated\n3. Every denial is recorded in evidence

## Failure Modes and Recovery
**Token absent**: deny and record; route to recovery.\n**Token revoked**: deny and record; quarantine strand.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
✅ **IMPLEMENTED** — `braid_simulator/authority.py`, `braid_simulator/execution.py`

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: RBAC/ABAC policy enforcement in software layer. BCT makes authority a structural crossing requirement, not a policy check.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
