# CONSENSUS BRAID (CONSENSUS BRAID)

> **Status:** See  for current implementation status.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Purpose
Produce distributed agreement between multiple agents or nodes without erasing the history of disagreement — the record of what was contested is as important as the final agreement.

## Intended Computational Role
The Consensus Braid coordinates multiple independent agents toward a shared conclusion without requiring any agent to discard its prior conclusions. The consensus record includes the full disagreement history.

## Strand Types
- **Agent strands**: one per participating agent (minimum 2)\n- **Proposal strand**: carries each agent's proposed conclusion\n- **Disagreement strand**: records contested positions\n- **Agreement strand**: carries the final consensus with full history

## Crossing Semantics
| CONS.PROPOSE | Record an agent's proposal |\n| CONS.CONTEST | Record disagreement with evidence |\n| CONS.RESOLVE | Apply resolution function to contested positions |\n| CONS.RATIFY | Certify final consensus with full history |

## Direction of Information Flow
Bidirectional: proposals flow from agents toward consensus; disagreement evidence flows between agents.

## Invariants
1. Disagreement history is preserved, not erased\n2. Final consensus references all prior positions\n3. No agent can unilaterally ratify consensus

## Failure Modes and Recovery
**Unresolvable disagreement**: record contradiction knot; escalate.\n**Agent unavailable**: record absence; continue with available agents.

## Authority Requirements
Authority token required on the operating strand for all promotion-type crossings. The specific role required depends on the operation:
- State-modifying crossings: EXECUTOR role minimum
- Promotion crossings: VERIFIER role minimum
- Revocation crossings: AUTHORITY_ADMIN role minimum

## Evidence Produced
Every crossing produces a minimum evidence record: crossing tag, family, opcode, timestamp, input hash, output hash, authority token id, result. Family-specific fields are added per crossing type.

## Current Implementation Status
💭 **SPECULATIVE** — Concept described; formal definition pending distributed runtime (Phase 6)

## Known Limitations
See `CLAIMS_REGISTER.md` for current claim status. All properties of this braid family are **[HYPOTHESIS]** unless marked LOCALLY VERIFIED in the register.

## Comparison Baseline
**Conventional**: Raft/Paxos — agree on final state; disagreement history discarded. BCT preserves disagreement history as a first-class record.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
