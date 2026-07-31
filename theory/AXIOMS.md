# Axioms

> **[ORIGINAL — HYPOTHESIS]** The following are the architectural axioms of BCT.  
> They are the ten governing laws expressed as formal axioms.  
> Proof that the execution model satisfies each axiom is a proof obligation in `theory/PROOF_OBLIGATIONS.md`.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

**Axiom 1 (Verification Gate):**  
For all strand states s, s.trust = TRUSTED implies there exists a crossing E in the execution history of s with E.opcode = INTEG.VERIFY and E.result = PASS.

**Axiom 2 (Evidence Monotonicity):**  
For all times t < t': |L_t| < |L_{t'}|, and for all i ≤ t: L_{t'}[i] = L_t[i].

**Axiom 3 (Reproducibility):**  
For all trusted states s, there exists a deterministic function R(checkpoint, log_segment) such that R produces a state s' with hash(s') = hash(s).

**Axiom 4 (Authority Non-Bypass):**  
For all crossings E with E.opcode ∈ {INTEG.PROMOTE, INTEG.SEAL}: there exists a crossing E' earlier in the execution sequence with E'.opcode = AUTH.CHECK and E'.result = PASS and E'.strand = E.strand.

**Axiom 5 (Recovery Evidence Preservation):**  
For all crossings E with E.family = RECOV: E appends to L and does not modify any existing element of L.

**Axiom 6 (Deterministic Recovery):**  
For all certified states s: there exists a recovery checkpoint C reachable from s such that R(C, log_segment) reconstructs s.

**Axiom 7 (History Permanence):**  
For all evidence records r ∈ L: r is never removed from L during any execution step.

**Axiom 8 (Verification Precedence):**  
Axiom 8 is a consequence of Axiom 1 and Axiom 4: verification crossing precedes promotion crossing on every execution path.

**Axiom 9 (Explicit Authority):**  
For all braids B = (n, I, [E_1, …, E_k]): for all i ∈ 1..n, there exists at least one crossing E_j with E_j.strand = i and E_j.family = AUTH.

**Axiom 10 (Law Immutability):**  
No opcode in I modifies the definitions of Axioms 1–10.

---

**Status:** All axioms are **[OPEN OBLIGATIONS]** — they must be proved as theorems of the formal execution model (see `theory/PROOF_OBLIGATIONS.md` PO-7a through PO-7j).

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
