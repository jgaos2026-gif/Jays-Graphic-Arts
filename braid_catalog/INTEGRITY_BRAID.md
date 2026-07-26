# Integrity Braid

## Purpose
Maintain provable computational correctness by verifying state transitions and preserving append-only evidence.

## Intended Computational Role
The Integrity Braid is the primary trust-building mechanism. It takes active (unverified) state as input and produces trusted state with attached verification evidence. It cannot produce trusted state without a verification crossing.

## Strand Types
- **Input strand**: carries active (unverified) state
- **Output strand**: carries trusted state with verification certificate
- **Evidence strand**: carries the accumulating verification record (append-only)

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `INTEG.VERIFY` | Apply verification function; promote to trusted on pass; route to recovery on fail |
| `INTEG.PROMOTE` | Formally elevate verified state to certified; requires valid certificate |
| `INTEG.ATTEST` | Attach external attestation to verified state |
| `INTEG.SEAL` | Mark state as immutable certified output |
| `INTEG.COMPARE` | Compare two states for equivalence; produce comparison record |

## Direction of Information Flow
Primarily forward (input → trusted output). Evidence flows forward and accumulates. The sealed output can be used as input to a reverse verification path.

## Allowed Transformations
- Active → Trusted (via VERIFY)
- Trusted → Certified (via PROMOTE)
- Certified → Sealed (via SEAL)
- Any state → Evidence record (always, for every crossing)

## Invariants
1. A trusted state always carries a verification certificate
2. A certified state always carries a promotion record
3. Every crossing appends to the evidence log (never modifies)
4. Trusted state is reproducible: replaying from evidence produces the same trusted state

## Failure Modes
- Verification function returns false → route to recovery; record failure
- Verification function is unavailable → halt; record missing function
- Certificate is malformed → quarantine; record malformation

## Recovery Behavior
On verification failure: state is quarantined with full evidence. Recovery path attempts re-verification with alternate function or restores from prior trusted checkpoint.

## Authority Requirements
A valid authority token is required on the verifying strand before INTEG.VERIFY executes. Verification by an unauthorized strand is an authority violation (logged, quarantined).

## Evidence Produced
Every crossing produces an evidence record containing: crossing tag, opcode, input hash, output hash, verification function identifier, result (PASS/FAIL), authority token id, timestamp.

## Complexity
- Per-crossing: O(1) crossing execution + O(|state|) for hash computation
- Evidence log: O(n) where n is number of crossings

## Current Implementation Status
✅ **IMPLEMENTED** — `braid_simulator/instructions.py`, `braid_simulator/execution.py`  
Tests: `tests/unit/test_braid.py`, `tests/adversarial/test_tamper.py`

## Test Coverage
- Unit: crossing execution, evidence append, certificate attachment
- Adversarial: attempt promotion without verification (fails), attempt evidence deletion (fails)
- Replay: deterministic replay from evidence log

## Known Limitations
- Verification functions are currently limited to HMAC and equality checks
- Multi-party attestation not yet implemented
- Formal proof of verification completeness (H3) not yet done

## Comparison Baseline
**Conventional**: Post-hoc HMAC on output only. Does not detect intermediate state corruption.  
**BCT integrity braid**: Verifies each state transition. Detects intermediate corruption at the crossing where it occurs.  
**[HYPOTHESIS]** BCT achieves higher completeness for intermediate state violations (H3).
