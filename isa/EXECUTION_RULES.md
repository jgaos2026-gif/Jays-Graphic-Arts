# Execution Rules

> **[ORIGINAL — HYPOTHESIS]**  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## The Execution Contract

Every crossing execution must satisfy these rules. Violation of any rule triggers an authority fault or evidence fault, routes to recovery, and records the violation.

### Rule 1: Authority Before Execution
AUTH.CHECK or AUTH.GATE must precede any crossing whose opcode produces TRUSTED, CERTIFIED, or SEALED state.

```
∀ E with E.opcode ∈ {INTEG.PROMOTE, INTEG.SEAL}:
  ∃ E' before E in sequence with E'.opcode = AUTH.CHECK and E'.result = PASS
```

### Rule 2: Evidence Always Appended
Every crossing appends exactly one EvidenceRecord to L. No crossing may be executed without producing an evidence record. Evidence records are never omitted.

### Rule 3: Evidence Never Modified
No crossing may modify or delete a prior evidence record. The evidence log is strictly append-only.

### Rule 4: Verification Before Trust
No state may carry trust level TRUSTED or higher without an INTEG.VERIFY crossing in its history.

### Rule 5: Tamper Detection (Two-Regime Ordering)
See `theory/PROOF_OBLIGATIONS.md` PO-1. Reorderings of crossings are validated against braid equivalence:
- Far-commutativity (|i−j| ≥ 2): always valid
- Braid relation (σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}): valid
- All other reorderings of adjacent crossings: tamper fault

### Rule 6: Quarantine Preservation
Quarantined state is never deleted. It is preserved in evidence storage and may be re-examined during recovery or audit.

### Rule 7: Recovery Without Erasure
RECOV.* opcodes may not remove prior evidence records. Recovery appends new records describing the recovery event.

### Rule 8: Authority Token Non-Duplication
ROLE.TRANSFER atomically moves a token. After transfer, the source strand holds no token; the target holds the token. No transient duplication.
