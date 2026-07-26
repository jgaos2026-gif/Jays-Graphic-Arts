# Braid Operations

> **[ESTABLISHED]** unless labeled **[ORIGINAL]** or **[HYPOTHESIS]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## 1. Composition

**[ESTABLISHED]** Two braids β₁, β₂ ∈ Bₙ compose by concatenation: stack β₁ on top of β₂, connecting the bottom endpoints of β₁ to the top endpoints of β₂. The result β₁β₂ is a valid braid in Bₙ.

Composition is associative: (β₁β₂)β₃ = β₁(β₂β₃).

The identity element e ∈ Bₙ is the braid with no crossings (n parallel vertical strands).

**[ORIGINAL — BCT]** In executable braids, composition concatenates the crossing sequences and requires that the output types of β₁ match the input types of β₂ for each strand.

---

## 2. Inversion

**[ESTABLISHED]** Every braid β ∈ Bₙ has a unique inverse β⁻¹ such that ββ⁻¹ = β⁻¹β = e.

Geometrically, β⁻¹ is obtained by reflecting β through a horizontal axis and reversing all crossing directions (over ↔ under).

Algebraically: if β = σᵢ₁^ε₁ σᵢ₂^ε₂ ... σᵢₖ^εₖ, then β⁻¹ = σᵢₖ^{-εₖ} ... σᵢ₂^{-ε₂} σᵢ₁^{-ε₁}.

**[HYPOTHESIS — BCT]** In executable braids, inversion may define a recovery operation: running the inverse braid reconstructs the execution history in reverse. Whether this provides computationally useful reverse execution is an open research question.

---

## 3. Conjugation

**[ESTABLISHED]** The conjugate of β by α is α⁻¹βα ∈ Bₙ. Conjugate braids have isotopic closures (Markov's theorem). The conjugacy problem — deciding whether two braids are conjugate — is decidable in polynomial time.

**[HYPOTHESIS — BCT]** Conjugation may model execution context wrapping: executing β in the context established by α. Authority braids may use conjugation to represent scoped permission contexts.

---

## 4. Stabilization

**[ESTABLISHED]** A braid β ∈ Bₙ can be stabilized to a braid in Bₙ₊₁ by appending σₙ^±¹, adding a new strand that crosses over or under the last existing strand. The closure of βσₙ is isotopic to the closure of β.

Markov's theorem states that two braids have isotopic closures if and only if they are related by a sequence of conjugations and stabilizations.

---

## 5. Tensor Product (Juxtaposition)

**[ESTABLISHED]** Two braids β₁ ∈ Bₙ and β₂ ∈ Bₘ can be placed side by side to form a braid in Bₙ₊ₘ. This is the tensor product in the braided monoidal category of braid groups.

**[HYPOTHESIS — BCT]** Juxtaposition models the parallel composition of independent braid computations. Two independent BCT subsystems can be juxtaposed into a combined braid without interaction unless crossings between the two halves are explicitly defined.

---

## 6. Closure

**[ESTABLISHED]** The closure β̂ of β ∈ Bₙ connects the i-th top endpoint to the i-th bottom endpoint for each i, producing a knot or link.

By Alexander's theorem (1923), every link is the closure of some braid.

**[HYPOTHESIS — BCT]** In executable braids, closure represents the completion of a computation cycle. The evidence accumulated during execution is preserved in the closed structure. The closure invariants (Jones polynomial, Alexander polynomial) may serve as verification signatures for completed computation. This is an open research question.

---

## 7. Permutation

**[ESTABLISHED]** Every braid β ∈ Bₙ induces a permutation π(β) ∈ Sₙ by reading where each strand ends. The map π : Bₙ → Sₙ is a group homomorphism. Its kernel is the pure braid group PBₙ — braids where every strand returns to its starting position.

**[HYPOTHESIS — BCT]** The permutation induced by an executable braid records which execution roles occupied which strand positions at completion. Role exchange crossings modify this permutation in controlled, verified ways.

---

## 8. Garside Normal Form

**[ESTABLISHED]** Every braid β ∈ Bₙ has a unique Garside normal form:

```
β = Δᵐ · A₁ · A₂ · ... · Aₖ
```

Where Δ is the fundamental braid (the half-twist permuting all strands), m ∈ ℤ, and each Aᵢ is a **simple element** (a positive permutation braid representable as a subword of Δ).

The Garside normal form provides an efficient solution to the word problem and is used in braid cryptography.

**[HYPOTHESIS — BCT]** Garside normal form may provide a canonical representation for executable braids, enabling efficient comparison of computationally equivalent execution sequences.

---

## 9. Dehornoy Ordering

**[ESTABLISHED]** Braid groups admit a strict left-invariant total order (the Dehornoy order), making them **left-orderable groups**. This is a deep structural property: Bₙ has no torsion and its elements can be consistently ordered.

**[HYPOTHESIS — BCT]** The Dehornoy order may provide a natural ordering of authority levels in authority braids — a mathematical foundation for the partial order structure of trust hierarchies.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
