# Compression Braid

> **Status:** See [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Reduce the structural size of braids and evidence through deduplication and shared structure, without deleting any provenance information.

## Intended Computational Role
The Compression Braid identifies structurally equivalent regions in the braid and collapses them to shared representations, reducing storage without losing any provenance information.

## Strand Types
- **Input strand**: carries full-size braid structure
- **Equivalence strand**: carries identified equivalences
- **Compressed strand**: carries the compressed representation
- **Provenance strand**: maps compressed back to original

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `COMP.IDENTIFY` | Find structurally equivalent regions |
| `COMP.COLLAPSE` | Replace equivalent regions with shared reference |
| `COMP.VERIFY` | Confirm compressed form preserves provenance |
| `COMP.EXPAND` | Reconstruct full form from compressed reference |

## Direction of Information Flow
Forward: full representation flows in; compressed representation flows out. Provenance mapping flows both directions.

## Invariants
1. Compression never deletes provenance records
2. Full form is reconstructible from compressed form
3. Compression is only applied to verified-equivalent regions

## Failure Modes and Recovery
**Non-equivalent compression attempted**: reject and record.
**Provenance gap after compression**: reject and restore.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
🔭 **FUTURE WORK** — Direction identified; awaiting OP-1 (Turing completeness) and OP-3 (invariant interpretation)

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: Lossless compression (gzip, zstd) without provenance awareness. BCT compression is provenance-preserving.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
