# Computational Invariants

> **[ESTABLISHED]** unless labeled **[ORIGINAL]** or **[HYPOTHESIS]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## 1. Classical Braid Invariants

### 1.1 The Permutation

**[ESTABLISHED]** The simplest invariant of a braid β ∈ Bₙ is its permutation π(β) ∈ Sₙ. Two braids with different permutations are not isotopic.

**[HYPOTHESIS — BCT]** In executable braids, the permutation records which strand ends in which position — the final authority assignment after all role exchange crossings have executed.

### 1.2 The Burau Representation

**[ESTABLISHED]** The Burau representation maps Bₙ → GL(n, ℤ[t, t⁻¹]). Each generator maps to a specific matrix:

```
σᵢ ↦ Iᵢ₋₁ ⊕ [1-t  t] ⊕ Iₙ₋ᵢ₋₁
              [ 1   0]
```

The reduced Burau representation (n-1 × n-1 matrix) is faithful for n ≤ 3 but not for n ≥ 5.

**[ESTABLISHED]** The Alexander polynomial of the closure of β can be computed from the Burau representation.

### 1.3 The Jones Polynomial

**[ESTABLISHED]** The Jones polynomial V(β̂)(t) is an invariant of the closure of β, discovered by Vaughan Jones (1985) using the Temperley-Lieb algebra representation of the braid group. It is a Laurent polynomial in t^{1/2}.

The Jones polynomial distinguishes many knots that the Alexander polynomial cannot.

**[ESTABLISHED]** The Jones polynomial has connections to statistical mechanics (Potts model) and topological quantum field theory.

### 1.4 The HOMFLY Polynomial

**[ESTABLISHED]** The HOMFLY polynomial P(β̂)(v, z) generalizes both the Alexander polynomial (at v=1) and the Jones polynomial (at specific substitution). It is computed from the braid using skein relations.

### 1.5 The Lawrence-Krammer-Bigelow Representation

**[ESTABLISHED]** The LKB representation is a faithful linear representation of Bₙ into GL(n(n-1)/2, ℤ[t^±¹, q^±¹]) for all n ≥ 1. This was proved independently by Bigelow (2001) and Krammer (2002), resolving a long-standing question about whether braid groups are linear.

---

## 2. BCT Computational Invariants

**[ORIGINAL — HYPOTHESIS]** BCT defines computational invariants for executable braids. These are properties that are preserved under defined equivalence relations on executable braids.

### 2.1 Evidence Invariant

**[HYPOTHESIS]** The evidence log E(β) of an executable braid β is an invariant under computational equivalence: two computationally equivalent executable braids (same result and same authority structure) have the same evidence log up to relabeling of evidence tags.

*This requires formal proof. It is a hypothesis.*

### 2.2 Authority Invariant

**[HYPOTHESIS]** The authority state of each strand is preserved as a computational invariant under the five laws governing authority (Laws 4, 5, 6, 8, 9). Specifically:

- The total number of authority tokens is conserved under role exchange
- Authority tokens cannot be created or destroyed by non-authority crossings
- The authority permutation induced by all role exchange crossings is a well-defined element of Sₙ

*These require formal proof.*

### 2.3 Verification Invariant

**[HYPOTHESIS]** A state that has passed a verification crossing carries a verification certificate that is preserved through all subsequent non-destructive crossings. The verification status is monotone: once trusted, always trusted until explicit demotion through a defined procedure.

*This requires formal proof.*

### 2.4 Recovery Invariant

**[HYPOTHESIS]** Every trusted state has a deterministic recovery path encoded in the braid structure (Law 6). The recovery braid invariant is the set of recovery paths available at each point in execution.

*This requires formal proof.*

---

## 3. Invariant Computation as Verification

**[HYPOTHESIS — Open]** A fundamental open question in BCT:

> Can classical braid invariants (Jones polynomial, HOMFLY polynomial) serve as verification signatures for completed executable braid computations?

**Argument for plausibility:** Two executable braids that are topologically equivalent (same Jones polynomial) may produce computationally equivalent results. If this relationship can be formalized, then computing a braid invariant becomes an efficient verification mechanism — potentially faster than replaying the full execution.

**Current obstacle:** The relationship between classical braid invariants (defined on the closure) and execution semantics (defined on the sequential crossing structure) is not yet established for executable braids.

**Path to resolution:** Define a mapping from executable braid execution traces to braid words; prove that computationally equivalent traces produce isotopic braids; conclude that invariants classify computational equivalence.

This is listed as Open Problem OP-3 in `research/OPEN_PROBLEMS.md`.

---

## 4. Quantum Invariants and BCT

**[ESTABLISHED]** Quantum invariants of knots and links (Jones polynomial, Witten-Reshetikhin-Turaev invariants) arise from representations of quantum groups and topological quantum field theories. They are computable polynomials with deep connections to physics.

**[ESTABLISHED]** In topological quantum computing, the computation performed by braiding anyons is described by these quantum invariants — the invariant encodes the quantum gate applied.

**[INSPIRATION — not equivalence]** BCT is inspired by the prospect that similar invariant structure might classify classical executable braid computations. The analogy is structural; the mathematical machinery is different.

---

## 5. Open Problems

1. What is the correct definition of computational equivalence for executable braids?
2. Do classical braid invariants classify computational equivalence?
3. Can the LKB representation be extended to capture execution semantics?
4. What is the complexity of computing BCT computational invariants?
5. Can invariant computation replace full execution replay for verification purposes?

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
