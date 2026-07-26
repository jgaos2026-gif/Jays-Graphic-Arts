# Executable Braids

> Content in this document is **[ORIGINAL]** unless labeled **[ESTABLISHED]**.  
> Original content is research hypothesis, not validated result.

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## 1. Motivation

**[ESTABLISHED]** Classical braid groups are passive mathematical objects. A crossing σᵢ records that strand i passed over strand i+1. It encodes a structural relationship. It does not perform computation.

**[ORIGINAL]** Executable braids transform this passive structure into an active computational substrate by assigning computational instructions to crossings. This is the foundational original contribution of the BCT research program.

---

## 2. Formal Definitions

### 2.1 Instruction Set

**[ORIGINAL — Definition]** An **instruction set** I for n-strand executable braids is a finite set of instructions, each defined by:

- A name
- An input signature: a tuple of types (one per crossing strand)
- An output signature: a tuple of types (one per continuing strand)
- An execution function: `exec : State × State → State × State × Evidence`
- A verification predicate: `verify : State × State → {trusted, untrusted}`

### 2.2 Executable Crossing

**[ORIGINAL — Definition]** An **executable crossing** E is a 5-tuple:

```
E = (i, j, direction, instruction, evidence_tag)
```

Where:
- `i` — index of first strand
- `j` — index of second strand; standard braids require |i − j| = 1
- `direction` ∈ {over, under}
- `instruction` ∈ I — a member of the instruction set
- `evidence_tag` — a unique identifier for this crossing's evidence record

### 2.3 Executable Braid

**[ORIGINAL — Definition]** An **executable braid** B on n strands with instruction set I is:

```
B = (n, I, [E₁, E₂, ..., Eₖ])
```

Where:
- `n` — strand count
- `I` — instruction set
- `[E₁, ..., Eₖ]` — a sequence of executable crossings forming a valid braid word

**Validity condition:** The sequence of crossings must form a valid braid in Bₙ when the instruction and evidence components are stripped.

---

## 3. Execution Model

**[HYPOTHESIS]** The execution of an executable braid B = (n, I, [E₁, ..., Eₖ]) proceeds as follows:

**State:** At each step t, the system state is:

```
Σₜ = (s₁, s₂, ..., sₙ, Log)
```

Where sᵢ is the current state of strand i, and Log is the append-only evidence log.

**Execution step:** For crossing Eₜ = (i, j, direction, instruction, tag):

```
1. (s'ᵢ, s'ⱼ, ev) = exec(sᵢ, sⱼ)      // execute instruction
2. Log' = Log ++ [(tag, ev)]             // append evidence (never overwrite)
3. Σₜ₊₁ = (s₁, ..., s'ᵢ, ..., s'ⱼ, ..., sₙ, Log')
```

**Termination:** Execution terminates after all k crossings are executed. The final state is Σₖ.

**[HYPOTHESIS]** The evidence log is monotonically growing. No crossing removes or modifies prior evidence records.

---

## 4. Relation to Classical Braids

**[ESTABLISHED]** Classical braids can be recovered from executable braids by stripping all instruction and evidence components and retaining only strand indices and crossing directions. The underlying braid structure is unchanged.

**[HYPOTHESIS]** All algebraic properties of the underlying classical braid are preserved in the executable braid. The instruction execution adds computational semantics without changing the topological structure.

**[OPEN]** Formal proof that executable braid equivalence (same computation result and evidence) is consistent with classical braid isotopy.

---

## 5. Composition

**[HYPOTHESIS]** Executable braids compose by concatenation, consistent with classical braid composition:

Given B₁ = (n, I, [E₁, ..., Eₖ]) and B₂ = (n, I, [F₁, ..., Fₘ]):

```
B₁ · B₂ = (n, I, [E₁, ..., Eₖ, F₁, ..., Fₘ])
```

The final state of B₁ becomes the initial state of B₂. The evidence logs concatenate.

**[HYPOTHESIS]** Composition is associative (inherited from classical braid group associativity).

**[OPEN]** Does the identity executable braid (no crossings) act as identity under composition? What instruction does it carry?

---

## 6. Turing Completeness

**[OPEN]** Whether the executable braid model is Turing-complete is an open question.

**[HYPOTHESIS]** For sufficiently expressive instruction sets I (specifically, instruction sets capable of conditional branching and unbounded iteration through braid width), the executable braid model may be Turing-complete.

**Approach to proof:** Reduce to a known complete model. One approach: show that executable braids with appropriate instruction sets can simulate arbitrary Turing machine transitions. Another approach: use known results on computation in monoidal categories.

**Known obstacle:** Standard braids have fixed width (n strands). Unbounded computation may require unbounded width or a family of braids indexed by width.

This is a priority open problem. See `research/OPEN_PROBLEMS.md` — OP-1.

---

## 7. Relationship to Topological Quantum Computing

**[ESTABLISHED]** Topological quantum computing uses braid operations on anyons to implement quantum gates. Non-abelian anyons have the property that braiding two anyons applies a unitary transformation to the quantum state. This is topological fault tolerance: the computation depends only on the topology of the braid, not the precise path.

**[INSPIRATION — not equivalence]** BCT is inspired by the observation that braid operations in quantum computing carry computational meaning (the unitary transformation) through their topological structure. BCT applies an analogous idea in classical computation: crossings carry classical computational instructions.

**BCT is not quantum computing.** It does not use anyons, superposition, entanglement, or quantum hardware. The analogy is structural: both use braid topology to encode computational meaning. The implementations and mathematical frameworks are distinct.

---

## 8. Open Problems

1. **Turing completeness:** Is the executable braid model Turing-complete for expressive instruction sets?
2. **Encoding efficiency:** What is the minimum braid width and length required to simulate n steps of a Turing machine?
3. **Invariant interpretation:** Can braid invariants (Jones polynomial, HOMFLY) be interpreted as computational verification signatures for executable braids?
4. **Categorical formalization:** What is the correct categorical description of executable braid composition, including instruction semantics?
5. **Isotopy and computation:** Under what conditions are two executable braids computationally equivalent (same result and evidence trace)?

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
