# Proof Obligations

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.1  
**Status:** Formal definitions in progress — proofs are open obligations, not completed results.

> Each section states a claim, provides its formalization, and names the proof obligation.  
> Nothing here is asserted as proved unless explicitly marked **[PROVED]**.  
> All others are **[OPEN OBLIGATION]**.

---

## 1. The Two-Regime Ordering Invariant (Tamper Detection vs. Safe Concurrency)

**Claim**  
The Braid ISA distinguishes three cases: operations that are causally independent (safe to reorder freely), operations that are adjacent and interacting (safe to reorder *only* in the one way permitted by the braid relation), and any other reordering of interacting operations (tamper-evident).

**Formalization**

Let **B**_n be the Artin braid group on generators σ_1, …, σ_{n−1}, subject to the defining relations:

- **Far commutativity**: σ_i σ_j = σ_j σ_i, for all i, j with |i − j| ≥ 2  
- **Braid relation**: σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}, for all valid i

**Regime A — Independent Concurrency (|i − j| ≥ 2)**

If operations op_i and op_j act on disjoint state and authority boundaries, then:

```
σ_i σ_j = σ_j σ_i
```

Reordering these produces an isomorphic braid word. Out-of-order execution among independent strands is provably harmless.

**Regime B — Adjacent Interacting Strands (|i − j| = 1)**

Adjacent generators do not commute in general:

```
σ_i σ_{i+1} ≠ σ_{i+1} σ_i
```

However, they satisfy the braid relation above, which means exactly one nontrivial three-crossing reordering is legitimate:

```
σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}
```

The correct claim is therefore: any permutation of adjacent crossings that is *not* an instance of far-commutativity (Regime A) or the braid relation (this identity) produces a braid word that is not isomorphic to the original, and is therefore tamper-evident.

> **The braid relation is not a loophole. It is the exact boundary that the tamper detector must be built around.**

An adversary who reorders adjacent crossings in a way that *satisfies* the braid relation is not tampering — the detector must not flag it as such, or it will produce false positives on legitimate execution and undermine trust in every other fault it reports.

**Proof Obligation (PO-1)**  
*Status: **[OPEN]***

Implement braid word reduction (Dehornoy's handle-reduction algorithm or Garside normal form) in the kernel verification engine. Both algorithms natively encode far-commutativity and the braid relation. Then prove:

1. Any permutation reducible to the same normal form via far-commutativity alone (Regime A) preserves system state — zero-overhead concurrency.
2. Any permutation reducible to the same normal form via the braid relation alone (Regime B, legitimate case) is accepted as a valid reordering.
3. Any permutation that reduces to a *different* normal form — i.e., is not an instance of (1) or (2) — triggers an immediate topological mismatch fault.

**Adversarial test case (see also OPEN_PROBLEMS.md — OP-9):**  
An adversary who specifically constructs a crossing reordering that satisfies the braid relation must not trigger the fault. The test suite in `tests/adversarial/test_tamper.py` must include this case explicitly. Failure to handle it produces false positives that undermine the entire fault reporting mechanism.

---

## 2. Append-Only Evidence Invariant

**Claim**  
The evidence log is strictly monotone: its length increases by exactly one record per executed crossing, and no record is ever modified or removed.

**Formalization**

Let L_t = (r_1, r_2, …, r_t) be the evidence log after t crossings. For any crossing execution at step t+1:

```
L_{t+1} = L_t ++ [r_{t+1}]     (concatenation, not mutation)
|L_{t+1}| = |L_t| + 1
∀ i ≤ t: (L_{t+1})[i] = (L_t)[i]   (prior records unchanged)
```

**Proof Obligation (PO-2)**  
*Status: **[LOCALLY VERIFIED]** (property test in `tests/property/test_invariants.py`)*

Prove that no opcode in the Braid ISA has an execution path that modifies or removes a prior evidence record. The property test verifies this for all implemented opcodes. Full formal proof requires OP-2 (formal semantics).

---

## 3. Reconstructability via Decoupled Provenance (State Recovery)

**Claim**  
Given an uncorrupted, append-only braid log L = (σ_1, σ_2, …, σ_t), stored independently from the state vector, a corrupted state **Ṽ**_{t+k} can be deterministically restored to a verified historical checkpoint **V**_t.

**Boundary Condition and Scope**  
This claim does not assert that the state vector can repair itself in isolation. The claim depends entirely on L being intact and independently verified. If the log is also corrupted, this proof obligation does not apply — the system must fall back to whatever redundancy protects L itself. That is a separate proof obligation (PO-4), not this one.

**Formalization**

Let **V**_t be a verified state snapshot at step t. Let f_{σ_i} be the forward state-transition function for crossing σ_i, and let f_{σ_i}^{−1} be its structural inverse.

Every generator σ_i in **B**_n has an algebraic inverse σ_i^{−1}, guaranteeing that f_{σ_i}^{−1} exists for all σ_i in the braid group.

Forward composition from the verified log:

```
V_{t+k} = f_{σ_{t+k}} ∘ f_{σ_{t+k−1}} ∘ … ∘ f_{σ_{t+1}} (V_t)
```

Given a corrupted **Ṽ**_{t+k} and the intact log segment (σ_{t+1}, …, σ_{t+k}), recovery is defined as reverse composition:

```
V_t = f_{σ_{t+1}}^{−1} ∘ f_{σ_{t+2}}^{−1} ∘ … ∘ f_{σ_{t+k}}^{−1} (Ṽ_{t+k})
```

The log L — not the corrupted state — is the source of truth for which inverses to apply and in what order.

**Proof Obligation (PO-3)**  
*Status: **[OPEN]***

For every state-altering opcode in the Braid ISA, demonstrate a deterministic f^{−1}. Prove that applying the reverse-composed sequence above, driven entirely by L, reconstructs a state whose hash matches the signed checkpoint at step t — even when the working state vector at step t+k is *arbitrarily* corrupted, provided L was not.

**Implementation note:** `braid_simulator/execution.py` implements forward composition and checkpoint-based restoration. Reverse composition from log (the full inverse proof) is a Phase 2 deliverable.

---

## 4. Log Independence Invariant

**Claim**  
The evidence log L is structurally independent of the state vector V. Corruption of V cannot corrupt L; corruption of L cannot be caused by a valid crossing execution.

**Proof Obligation (PO-4)**  
*Status: **[OPEN]***

Requires architectural separation of the log storage from the state storage. Prove that no state-modifying crossing can write to the log storage layer except through the append-only interface, and that no log entry can be directed to the state storage layer.

In the current simulator, L and V are separate Python objects. A full proof requires a formal separation argument, which depends on PO-2 (formal semantics).

---

## 5. Authority Non-Duplication

**Claim**  
An authority token cannot exist on more than one strand simultaneously. ROLE.TRANSFER atomically removes the token from the source strand and places it on the target strand; there is no transient state in which the token is on both.

**Formalization**

Let T be an authority token. Let τ: Strands → {T, ∅} be the token assignment function.

Before transfer: τ(source) = T, τ(target) = ∅  
After transfer:  τ(source) = ∅, τ(target) = T  
At no point:     τ(source) = T ∧ τ(target) = T

**Proof Obligation (PO-5)**  
*Status: **[LOCALLY VERIFIED]** (unit test in `tests/unit/test_authority.py`)*

Full proof requires showing that the transfer operation in `braid_simulator/authority.py` is atomic under all defined failure modes — including a failure that occurs between the remove and the assign steps. This requires the Atomic Proof Core (Phase 2).

---

## 6. Trust Level Monotonicity

**Claim**  
Trust levels are strictly ordered: ACTIVE < TRUSTED < CERTIFIED < QUARANTINED. A strand can move up the trust ladder only through defined verification crossings. QUARANTINED is a terminal absorbing state under normal execution (exit only via RECOV.HEAL + re-verification).

**Formalization**

Let TrustLevel = {ACTIVE, TRUSTED, CERTIFIED, QUARANTINED} with the order above.

For any crossing execution, the resulting trust level tl' satisfies:

- tl' = TRUSTED only if the crossing was INTEG.VERIFY and the verification function returned PASS
- tl' = CERTIFIED only if the crossing was INTEG.PROMOTE and the strand carried a valid TRUSTED certificate
- tl' = QUARANTINED only if the crossing was RECOV.QUARANTINE
- tl' = ACTIVE in all other cases
- No crossing may produce tl' = TRUSTED from tl = QUARANTINED directly

**Proof Obligation (PO-6)**  
*Status: **[LOCALLY VERIFIED]** (unit tests in `tests/unit/test_braid.py`)*

Full proof requires exhaustive case analysis over all opcodes, which depends on PO-2 (formal semantics).

---

## 7. Governing Law Structural Enforcement

**Claim**  
The ten governing laws are structurally enforced: no valid execution of a well-formed executable braid can violate any law. The laws are not policies checked by software — they are invariants of the execution model.

**Proof Obligations (PO-7a through PO-7j)**  
*Status: All **[OPEN]** — depend on PO-2 (formal semantics)*

| Law | Proof obligation |
|---|---|
| 1. No active state becomes trusted without verification | Show INTEG.VERIFY is the only path to TrustLevel.TRUSTED (PO-6) |
| 2. Evidence is append-only | PO-2 |
| 3. Trusted state is reproducible | PO-3 |
| 4. Authority cannot be bypassed | Show AUTH.CHECK precedes every promotion crossing |
| 5. Recovery preserves evidence | Show RECOV.* opcodes only append to log |
| 6. Every trusted state has deterministic recovery | Show every TRUSTED state has a reachable checkpoint reference |
| 7. History is never discarded | PO-2 |
| 8. Verification precedes promotion | Structural consequence of Law 1 |
| 9. Every module has explicit authority | Show every braid has at least one AUTH crossing before any PROMOTE |
| 10. Governing laws remain immutable | Show no opcode modifies the law definitions |

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
