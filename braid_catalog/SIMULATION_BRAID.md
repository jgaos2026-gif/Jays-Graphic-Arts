# SIMULATION BRAID (SIMULATION BRAID)

> **Status:** See  for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Maintain branching possible worlds simultaneously, collapse rejected branches when decisions are made, and preserve the record of why rejected branches were abandoned.

## Intended Computational Role
The Simulation Braid maintains multiple concurrent hypothetical worlds and records the evidence that leads to collapsing each branch.

## Strand Types
- **World strands**: one per hypothetical branch\n- **Decision strand**: carries the collapsing event\n- **Archive strand**: preserves collapsed branches with reason\n- **Survivor strand**: carries the selected world forward

## Crossing Semantics
| SIM.BRANCH | Create new hypothetical world strand |\n| SIM.OBSERVE | Record evidence in a world strand |\n| SIM.COLLAPSE | Archive rejected world with collapse evidence |\n| SIM.COMMIT | Promote surviving world to primary |

## Direction of Information Flow
Divergent: one world strand becomes many on BRANCH. Convergent: many collapse to one on COMMIT.

## Invariants
1. Collapsed world strands are archived, not deleted\n2. Every collapse event records the reason\n3. Only one world can be committed

## Failure Modes and Recovery
**All branches collapse**: record total simulation failure.\n**Contradiction between worlds**: create contradiction knot record.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
💭 **SPECULATIVE** — Direction identified; formal definition pending Phase 5+

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: Monte Carlo / tree search without collapse records. BCT preserves why branches were rejected.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
