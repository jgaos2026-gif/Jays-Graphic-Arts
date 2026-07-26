# SCHEDULING BRAID (SCHEDULING BRAID)

> **Status:** See  for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Coordinate interleaved work from multiple producers while preserving ordering constraints, dependency history, and the record of how priorities were resolved.

## Intended Computational Role
The Scheduling Braid coordinates work from multiple sources while enforcing dependency ordering and recording priority resolution decisions.

## Strand Types
- **Work item strands**: one per scheduled task\n- **Dependency strand**: encodes ordering constraints\n- **Priority strand**: carries priority state\n- **Resolution strand**: records how conflicts were resolved

## Crossing Semantics
| SCHED.ENQUEUE | Add work item with dependencies |\n| SCHED.DEQUEUE | Remove next ready work item |\n| SCHED.RESOLVE_CONFLICT | Apply priority resolution with record |\n| SCHED.COMPLETE | Mark work item completed with evidence |

## Direction of Information Flow
Forward: work items flow from enqueue to dequeue. Dependency ordering constrains forward flow.

## Invariants
1. Dependency ordering is enforced structurally\n2. Priority resolution decisions are recorded\n3. Every completed work item has a completion record

## Failure Modes and Recovery
**Dependency cycle**: detect and record; halt dependent work items.\n**Priority deadlock**: apply defined resolution; record intervention.

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
**Conventional**: Job schedulers with separate audit logs. BCT embeds scheduling decisions in braid structure.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
