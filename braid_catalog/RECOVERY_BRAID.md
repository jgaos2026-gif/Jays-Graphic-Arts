# Recovery Braid

## Purpose
Navigate computational damage by repairing execution in-place while preserving all evidence, including the evidence of the failure itself.

## Intended Computational Role
When execution encounters a failure, the Recovery Braid detects it, preserves the failure evidence, isolates the damaged state, and restores the execution path from the nearest trusted checkpoint — without discarding any prior evidence.

## Strand Types
- **Primary strand**: carries execution state that may be damaged
- **Quarantine strand**: receives isolated damaged state (write-only; state cannot be promoted from quarantine without re-verification)
- **Checkpoint strand**: carries the last trusted state available for restoration
- **Evidence strand**: append-only record of the entire recovery event

## Crossing Semantics
| Opcode | Behavior |
|---|---|
| `RECOV.DETECT` | Examine strand state for anomalies; produce anomaly flag |
| `RECOV.QUARANTINE` | Move suspect state to isolated quarantine strand with full evidence |
| `RECOV.RESTORE` | Retrieve last trusted checkpoint; initiate re-execution from that point |
| `RECOV.HEAL` | Apply repair function to damaged state; healed state must pass INTEG.VERIFY |
| `RECOV.ARCHIVE` | Move permanently failed state to cold evidence storage |

## Direction of Information Flow
Bidirectional: forward detection, backward restoration. The recovery path runs against the direction of primary execution — it traverses the evidence log backward to find the last trusted checkpoint.

## Allowed Transformations
- Active/Trusted → Quarantined (via QUARANTINE; never promotes quarantined state without re-verification)
- Checkpoint reference → Restored trusted state (via RESTORE)
- Damaged state → Healed active state (via HEAL; must then pass INTEG.VERIFY)

## Invariants
1. Quarantined state is preserved, not deleted
2. Recovery never discards prior evidence records
3. Every restoration is itself recorded in the evidence log
4. A restored state begins as active; it must be re-verified before trusted promotion

## Failure Modes
- No trusted checkpoint available → halt with evidence; cannot recover
- Heal function fails → archive damaged state; escalate
- Contradiction between restored state and current evidence → contradiction knot

## Recovery Behavior
Recovery is self-applying: if the recovery path itself encounters a failure, it has its own recovery path (one level deeper). Maximum recovery depth is defined at braid construction time.

## Authority Requirements
RECOV.RESTORE requires the same authority as the original execution. Recovery cannot silently bypass authority requirements.

## Evidence Produced
Full record of: anomaly detection event, quarantine event, checkpoint reference used, restoration event, re-verification result, final state classification.

## Complexity
- Detection: O(|state|) for anomaly check
- Restoration: O(k) where k is the distance from the current crossing to the last trusted checkpoint

## Current Implementation Status
✅ **IMPLEMENTED** — `braid_simulator/execution.py`  
Tests: `tests/unit/test_braid.py`, `tests/adversarial/test_tamper.py`, `tests/crash_recovery/`

## Test Coverage
- Unit: quarantine, restore, heal
- Adversarial: recovery that attempts to bypass authority (fails)
- Crash recovery: simulated mid-execution failures with evidence verification

## Known Limitations
- Maximum recovery depth is fixed at braid construction time
- Contradiction knot resolution is not yet fully implemented
- Distributed recovery across multiple nodes not yet designed

## Comparison Baseline
**Conventional checkpoint rollback**: Discards all computation since last checkpoint. Evidence of intermediate work is lost.  
**BCT recovery braid**: Preserves all evidence including failure. Repairs in place when possible. Restores from checkpoint only when repair is impossible.  
**[HYPOTHESIS]** BCT achieves higher recovery fidelity for failures that corrupt state but leave surrounding context intact (H2).
