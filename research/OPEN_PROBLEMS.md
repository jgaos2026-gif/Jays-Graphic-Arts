# Open Problems

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  

> This document lists unsolved problems in the BCT research program.  
> Open problems are questions, not claims.  
> Progress on any open problem should be documented here.

---

## OP-1 — Turing Completeness

**Problem:** Is the executable braid model Turing-complete for sufficiently expressive instruction sets?

**Why it matters:** If the model is not Turing-complete, there exist computable functions that cannot be expressed as executable braids, limiting the architectural applicability. If it is Turing-complete, the architectural question becomes one of overhead and structural advantage, not capability.

**Current approach:** None established. Candidates:
1. Construct a simulation of a Turing machine using executable braids with a defined instruction set
2. Use known results on computation in braided monoidal categories
3. Define a cellular automaton encoding in braid crossings and appeal to CA universality results

**Blocker:** Fixed braid width may prevent unbounded computation. A family of braids indexed by width may be required.

**Priority:** High.

---

## OP-2 — Formal Semantics

**Problem:** What is the correct formal semantics (operational, denotational, or axiomatic) for the BCT execution model?

**Why it matters:** Formal semantics are required for proof of the governing laws, for comparison with other models, and for implementation correctness.

**Current state:** Informal descriptions exist in `architecture/EXECUTION.md`. No formal semantic definition has been written.

**Approach candidates:**
- Structural operational semantics (SOS) for the execution cycle
- Denotational semantics via functor from braid category to computation category
- Axiomatic semantics for pre/postcondition reasoning about crossing instructions

**Priority:** High.

---

## OP-3 — Invariant Interpretation

**Problem:** Can classical braid invariants (Jones polynomial, HOMFLY polynomial) be interpreted as computational verification signatures for executable braids?

**Why it matters:** If braid invariants classify computational equivalence classes, invariant computation becomes an efficient verification mechanism — potentially faster than replaying the full execution.

**Current state:** The relationship between invariants (defined on braid closures) and execution semantics (defined on sequential crossings) has not been investigated for executable braids.

**Approach candidates:**
- Define a trace invariant for executable braids analogous to the Markov trace for classical braids
- Investigate whether computationally equivalent execution traces produce isotopic underlying braids
- Explore connections to the theory of invariants in traced monoidal categories

**Priority:** Medium.

---

## OP-4 — Categorical Formalization

**Problem:** What is the correct categorical description of executable braid composition, including instruction semantics?

**Why it matters:** Category theory provides the canonical language for compositional structures. A categorical formalization would connect BCT to established algebraic results and enable the use of categorical proof techniques.

**Current state:** The underlying braid structure has well-known categorical descriptions (braided monoidal categories). Extending this to executable braids requires additional structure (instruction semantics as morphisms).

**Approach candidates:**
- Enriched category: enrich the braid category over a category of instruction sets
- Traced monoidal category with execution semantics
- Operad structure for instruction family composition

**Priority:** Medium.

---

## OP-5 — Relationship to Petri Nets

**Problem:** What is the precise relationship between executable braids and Petri nets?

**Why it matters:** Petri nets are an established formalism for concurrent computation with well-studied properties (reachability, liveness, boundedness). Establishing the relationship would position BCT relative to known results.

**Current state:** Informal similarities exist: both model concurrent processes with explicit interaction. No formal comparison has been made.

**Approach candidates:**
- Translate executable braid crossings to Petri net transitions
- Compare reachability sets
- Identify where the models diverge (braids preserve crossing order; Petri nets may not)

**Priority:** Medium.

---

## OP-6 — Structural Law Enforcement

**Problem:** Can it be formally proved that the ten governing laws are structurally enforced — i.e., that no execution of a valid executable braid can violate any law?

**Why it matters:** The BCT architecture claims structural enforcement, not policy enforcement. This claim requires proof.

**Current state:** The laws are stated. Arguments for their structural enforcement are given informally in `architecture/`. No formal proofs exist.

**Approach:** Requires OP-2 (formal semantics) as a prerequisite. Then prove each law as a theorem over the execution model.

**Priority:** High (prerequisite: OP-2).

---

## OP-7 — Distributed Braids

**Problem:** How are BCT braids defined and executed across distributed systems?

**Why it matters:** The routing braid, consensus braid, and memory braid hypotheses all require definitions for distributed execution. Single-machine execution cannot validate these hypotheses.

**Current state:** Undefined. All current definitions assume a single execution context.

**Approach candidates:**
- Concatenation of braid segments across nodes
- Partial braid execution with handoff protocols
- Merkel-tree-like evidence sharing between nodes

**Priority:** Low (Phase 6).

---

## OP-8 — Learning Braid Definition

**Problem:** Can learning be formally defined as an executable braid operation rather than a parameter update?

**Why it matters:** If learning can be expressed as a braid instruction family, AI training could preserve provenance of every learned transformation — a significant potential contribution to AI explainability and governance.

**Current state:** No formal definition exists. The learning braid is listed as future research.

**Approach candidates:**
- Define a learning crossing as a role exchange that modifies the strand's instruction set based on evidence
- Relate to adaptive computation and meta-learning frameworks
- Investigate connections to gradient-as-braid formalisms

**Priority:** Low (Phase 5+).

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*

---

## OP-9 — Braid-Relation Edge Case in Tamper Detection

**Problem:** The tamper detection engine must correctly distinguish *legitimate* reorderings of adjacent crossings (those satisfying the braid relation σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}) from actual tampering (any other reordering of adjacent crossings that produces a different normal form).

**Why it matters:** An adversary who constructs a crossing reordering that satisfies the braid relation is executing a legitimate topological equivalence — not tampering. A detector that flags this case produces false positives, which undermines trust in every genuine fault it reports. This is the exact boundary the verification engine must be built around.

**Formalization:** See `theory/PROOF_OBLIGATIONS.md` — PO-1, Regime B. The proof obligation is: implement Dehornoy handle-reduction or Garside normal form, and prove that any permutation reducible to the same normal form via the braid relation alone is accepted as valid.

**Adversarial test required:** `tests/adversarial/test_tamper.py` must include a test case that:
1. Constructs a crossing sequence w₁
2. Constructs w₂ = w₁ with a braid-relation reordering applied (w₁ and w₂ are topologically equivalent)
3. Asserts that the tamper detector does NOT flag w₂ as tampered
4. Then constructs w₃ = w₁ with a non-equivalent adjacent reordering applied
5. Asserts that the tamper detector DOES flag w₃ as tampered

**Priority:** High — this must be resolved before PO-1 can be closed.

**See also:** `theory/PROOF_OBLIGATIONS.md` — PO-1.
