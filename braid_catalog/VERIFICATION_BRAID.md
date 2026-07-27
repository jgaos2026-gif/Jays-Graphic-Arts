# Verification Braid

> **Status:** See [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Challenge candidate conclusions by running forward claims against reverse evidence and independent checks, producing only claims that survive the challenge.

## Intended Computational Role
The Verification Braid is the skeptic. It does not accept a candidate conclusion until it has been challenged from at least one independent direction. It coordinates forward claims and reverse evidence checks.

## Strand Types
- **Claim strand**: carries forward candidate conclusion
- **Evidence strand**: carries reverse evidence for checking
- **Check strand**: independent verification path
- **Verdict strand**: carries verified or rejected result

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `VERIF.CHALLENGE` | Apply challenge function to candidate claim |
| `VERIF.CROSS_CHECK` | Compare claim against independent evidence |
| `VERIF.REJECT` | Record rejection with full challenge evidence |
| `VERIF.CERTIFY` | Promote claim that survives all challenges |

## Direction of Information Flow
Bidirectional: forward claims flow one direction; reverse evidence flows the other. The two strands cross at the challenge point.

## Invariants
1. A claim is never certified without surviving at least one challenge
2. Rejected claims are preserved in evidence
3. Challenge functions are recorded with their results

## Failure Modes and Recovery
**Challenge fails**: reject claim with full challenge evidence.
**Independent evidence unavailable**: suspend claim; record suspension.

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
**Conventional**: Post-hoc verification (checksums, signatures). BCT challenges claims bidirectionally during execution.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
