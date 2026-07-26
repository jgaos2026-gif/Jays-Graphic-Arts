# PROVENANCE BRAID (PROVENANCE BRAID)

> **Status:** See  for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Track the complete origin and transformation chain of every value throughout computation, so that any output can be traced to its sources.

## Intended Computational Role
The Provenance Braid acts as the permanent record-keeper. Every value carries its full origin story — what it was derived from, by what transformation, under what authority, with what verification.

## Strand Types
- **Value strand**: carries the current value\n- **Origin strand**: carries the complete derivation chain\n- **Transform strand**: records each transformation applied\n- **Evidence strand**: permanent provenance record

## Crossing Semantics
| PROV.RECORD_ORIGIN | Attach origin information to a value |\n| PROV.RECORD_TRANSFORM | Record a transformation with input/output hashes |\n| PROV.VERIFY_CHAIN | Verify the complete provenance chain |\n| PROV.QUERY | Retrieve provenance record for a value |

## Direction of Information Flow
Forward only: provenance accumulates as computation proceeds. The provenance record is immutable once written.

## Invariants
1. Every value carries its complete derivation chain\n2. Provenance records are append-only\n3. Any output can be traced to its input sources

## Failure Modes and Recovery
**Chain break detected**: quarantine affected value; record break location.\n**Transformation hash mismatch**: quarantine and record.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
🔬 **DEFINED** — Formal definition complete; implementation planned Phase 2

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: W3C PROV data model as a separate layer. BCT embeds provenance in the braid topology.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
