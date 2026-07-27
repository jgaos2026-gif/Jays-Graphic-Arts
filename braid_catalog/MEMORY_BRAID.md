# Memory Braid

> **Status:** See [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Coordinate three-tier state (hot/warm/cold) through executable crossing instructions, with full history preservation and deterministic retrieval.

## Intended Computational Role
The Memory Braid manages state lifecycle across three tiers. It determines when state moves from active working memory (hot) to recent-inactive (warm) to archived (cold), and coordinates retrieval paths.

## Strand Types
- **Hot strand**: active execution state, high bandwidth
- **Warm strand**: recent inactive state
- **Cold strand**: archived state, append-only
- **Circulation strand**: manages tier transitions

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `MEM.STORE_HOT` | Write to active memory |
| `MEM.LOAD_HOT` | Read from active memory |
| `MEM.DEMOTE_WARM` | Move hot state to warm tier |
| `MEM.PROMOTE_HOT` | Move warm state back to hot |
| `MEM.ARCHIVE_COLD` | Archive warm state permanently |
| `MEM.RETRIEVE_COLD` | Fetch archived state to warm |

## Direction of Information Flow
Forward: state moves toward archival (hot → warm → cold). Backward: retrieval moves state toward active use (cold → warm → hot).

## Invariants
1. State in cold storage is never deleted
2. Every tier transition is recorded
3. Retrieval path is deterministic from evidence log

## Failure Modes and Recovery
**Hot memory capacity exceeded**: demote oldest strand to warm; record demotion.
**Cold retrieval failure**: halt with evidence; manual intervention required.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
✅ **IMPLEMENTED** — `braid_simulator/state.py`, `braid_simulator/execution.py`

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: LRU cache + persistent storage + separate logging. BCT unifies tier management and history into one structure.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
