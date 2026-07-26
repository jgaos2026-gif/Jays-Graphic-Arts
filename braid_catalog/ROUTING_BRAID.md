# ROUTING BRAID (ROUTING BRAID)

> **Status:** See  for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Move information through dynamically selected verified paths while preserving authority, verification, and evidence at every routing decision.

## Intended Computational Role
The Routing Braid selects among available execution paths based on defined predicates, load conditions, and authority state. All selected paths are verified. No path is selected that lacks authority or verification crossings.

## Strand Types
- **State strand**: carries execution state to be routed\n- **Path strands**: alternative execution routes\n- **Decision strand**: carries routing predicate result\n- **Evidence strand**: records routing decisions

## Crossing Semantics
| ROUTE.SELECT | Evaluate predicate; route to selected path |\n| ROUTE.FORK | Duplicate state to multiple parallel paths |\n| ROUTE.JOIN | Merge multiple paths into one |\n| ROUTE.REDIRECT | Reroute based on condition |\n| ROUTE.REPLAY | Reconstruct state from evidence log |

## Direction of Information Flow
Forward: state flows toward selected destination paths. Bidirectional: rejected path evidence flows back to routing decision record.

## Invariants
1. Every selected path has authority and verification crossings\n2. Routing decisions are recorded before execution proceeds\n3. No path is selected that lacks a recovery path

## Failure Modes and Recovery
**No valid path**: halt with evidence; cannot route.\n**Authority denied on selected path**: reroute to recovery path; record denial.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
✅ **IMPLEMENTED** — `braid_simulator/instructions.py`, `braid_simulator/execution.py`

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: Routing decisions in message queues and load balancers with separate logging. BCT embeds routing decisions in braid topology with structural evidence requirements.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
