# Formal Model

> **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Overview

The BCT formal model defines the mathematical objects that the simulator implements. It is a research definition in progress. Items marked **[OPEN]** require formal proof.

---

## 1. System State

**Definition:** A BCT system state at time t is a tuple:

```
Σ_t = (S_t, A_t, L_t)
```

Where:
- **S_t** = (s_1, s_2, …, s_n) — the strand state vector; each s_i ∈ StrandState
- **A_t** = (a_1, a_2, …, a_n) — the authority assignment; each a_i ∈ AuthorityToken ∪ {∅}
- **L_t** — the evidence log at time t; a finite sequence of EvidenceRecord

---

## 2. StrandState

```
StrandState ::= {
  value:       V       (any serializable value)
  trust:       TrustLevel ∈ {ACTIVE, TRUSTED, CERTIFIED, QUARANTINED}
  history:     [CrossingTag]   (ordered list of crossing tags; append-only)
  certificate: VerificationCertificate | null
}
```

Trust level ordering: ACTIVE < TRUSTED < CERTIFIED. QUARANTINED is a terminal absorbing state under normal execution.

---

## 3. EvidenceRecord

```
EvidenceRecord ::= {
  tag:         CrossingTag         (unique per crossing)
  family:      InstructionFamily
  opcode:      Opcode
  timestamp:   ℕ                   (crossing index, strictly increasing)
  strand_i:    ℕ
  strand_j:    ℕ
  input_hash:  Hash
  output_hash: Hash
  authority:   TokenId | null
  result:      PASS | FAIL | QUARANTINED
}
```

---

## 4. Execution Step

**Definition:** A single execution step applies crossing E_t = (i, j, dir, instr, tag) to system state Σ_t:

```
Step(Σ_t, E_t) → Σ_{t+1}
```

Where:

```
1. Check: A_t[i] satisfies authority requirement of instr
2. Execute: (s'_i, s'_j, ev) = instr.exec(s_i, s_j)
3. Append: L_{t+1} = L_t ++ [ev]          (append-only; never replace)
4. Update: S_{t+1} = S_t with s_i ← s'_i, s_j ← s'_j
5. Σ_{t+1} = (S_{t+1}, A_t, L_{t+1})
```

If step 1 fails: ev records the authority violation; s'_i is quarantined; execution routes to recovery.

---

## 5. Braid Execution

**Definition:** A braid execution B = (n, I, [E_1, …, E_k]) starting from initial state Σ_0 produces:

```
Σ_k = Step(Step(…Step(Σ_0, E_1)…, E_{k-1}), E_k)
```

**Final result:** (S_k, A_k, L_k)

---

## 6. Invariants (Proof Obligations)

See `theory/PROOF_OBLIGATIONS.md` for formal obligations. Summary:

| Invariant | Status |
|---|---|
| Evidence monotonicity: \|L_{t+1}\| = \|L_t\| + 1 | Locally Verified |
| Trust monotonicity: TRUSTED requires INTEG.VERIFY | Locally Verified |
| Authority non-duplication | Locally Verified |
| Structural law enforcement (Laws 1–10) | Open |
| Turing completeness | Open |

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
