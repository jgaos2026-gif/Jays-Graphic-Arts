# Thesis: Braided Computational Topology as a Research Program

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  
**Status:** Working thesis document — not yet peer reviewed

> **Layer labels used throughout:** [ESTABLISHED], [HYPOTHESIS], [INSPIRATION], [OPEN]

---

## Thesis Statement

**[HYPOTHESIS]** Families of executable braid topologies can serve as computational structures that preserve execution history, authority, verification evidence, and recovery pathways structurally — offering potential architectural advantages for computation classes where these properties are mandatory.

---

## Chapter 1: The Problem

### 1.1 What Architecture Discards

**[ESTABLISHED]** The von Neumann architecture and its descendants optimize computation by discarding information not required for future execution. A state machine in state S₁ does not need to remember state S₀ to continue computing. This is not a bug; it is a deliberate and correct design choice that enables efficient computation.

**[ESTABLISHED]** The consequence of this choice is that recovering historical information requires either retaining it explicitly (logging, checkpointing, journaling, write-ahead logs) or re-executing the computation. These mechanisms work. They are widely used. They add overhead proportional to the amount of history required.

**[HYPOTHESIS]** For computation classes where history preservation, authority tracking, and verification are not optional but mandatory, this overhead is unavoidable within the conventional architectural model. The question BCT investigates is whether a different architectural model carries these requirements structurally, potentially reducing or eliminating this overhead.

### 1.2 The Class of Problems

**[HYPOTHESIS]** The computation classes where BCT structural advantages may apply include:

1. **Audited computation** — every state transition must be reconstructible from an immutable record
2. **High-assurance computation** — verification completeness is a hard requirement
3. **Recovery-critical computation** — execution must be restorable from any failure point with evidence preserved
4. **Provenance-critical computation** — data lineage must be traceable through the full computation
5. **Authority-sensitive computation** — permission checking must be structurally un-bypassable
6. **AI reasoning with explainability requirements** — the reasoning path must be preserved alongside the result

These are not rare applications. They describe substantial portions of financial systems, medical systems, security infrastructure, legal systems, and AI governance requirements.

### 1.3 The Research Question

**[HYPOTHESIS]** Can executable braid topologies provide the structural properties required for these computation classes with lower overhead than adding those properties to conventional architectures?

This is the organizing question of the BCT research program. It is testable. It may be answered affirmatively, negatively, or with nuance (some properties, some classes). All outcomes are valuable.

---

## Chapter 2: The Mathematical Foundation

### 2.1 Braid Groups

**[ESTABLISHED]** Emil Artin defined braid groups in 1925. The braid group Bₙ on n strands has generators σ₁, σ₂, ..., σₙ₋₁ subject to:

- **Braid relations:** σᵢσᵢ₊₁σᵢ = σᵢ₊₁σᵢσᵢ₊₁ for all valid i
- **Commutativity relations:** σᵢσⱼ = σⱼσᵢ for |i − j| ≥ 2

Each generator σᵢ represents strand i crossing over strand i+1. The inverse σᵢ⁻¹ represents strand i+1 crossing over strand i.

**[ESTABLISHED]** Braids compose by concatenation: given braids β₁ and β₂ on n strands, their product β₁β₂ is the braid obtained by placing β₁ above β₂. This composition is associative. The identity element is the braid with no crossings.

**[ESTABLISHED]** The word problem for braid groups is decidable. Multiple efficient algorithms exist, including the Garside normal form algorithm.

### 2.2 Relevant Properties of Braid Groups

**[ESTABLISHED]** Properties of braid groups that motivate BCT:

**History preservation:** A braid is a record of all crossings in sequence. The topology encodes the full history of strand interactions, not merely the final permutation of strands.

**Non-commutativity:** Braid groups are non-abelian for n ≥ 3. The order of crossings matters. σ₁σ₂ ≠ σ₂σ₁ in general. This models computational processes where operational ordering is significant.

**Invertibility:** Every braid has an inverse. This supports bidirectional traversal and reversal of execution sequences.

**Closure:** Connecting the top endpoints of a braid to its bottom endpoints produces a knot or link. This models completed computation cycles.

**Rich invariant theory:** Braid invariants (Alexander polynomial, Jones polynomial, HOMFLY polynomial) provide powerful tools for analyzing braid equivalence and structure.

### 2.3 The Gap Between Mathematics and Computation

**[ESTABLISHED]** Classical braid groups are passive mathematical objects. Their crossings are abstract relationships encoding strand order. They do not perform computation.

**[ORIGINAL]** BCT proposes to close this gap by defining **executable crossings**: crossings that carry and execute computational instructions. This is the fundamental original contribution.

**[HYPOTHESIS]** Executable crossings transform braid topology from a mathematical representation into an active computational substrate.

---

## Chapter 3: Executable Braids

### 3.1 Formal Definition

**[ORIGINAL]** An **executable crossing** is a 4-tuple:

```
C = (strand_i, strand_j, direction, instruction)
```

Where:
- `strand_i` — the index of the first crossing strand
- `strand_j` — the index of the second crossing strand (|i − j| = 1 in standard braids)
- `direction` ∈ {over, under}
- `instruction` ∈ I, where I is a defined instruction set

**[ORIGINAL]** An **executable braid** is a finite sequence of executable crossings forming a valid braid word under Artin's relations, where every crossing is an executable crossing.

**[OPEN]** Formal characterization of the computation class of executable braids — what functions can be computed by executable braids of bounded width, length, and instruction set?

### 3.2 Execution Semantics

**[HYPOTHESIS]** The execution of an executable braid proceeds sequentially through crossings from top to bottom. At each crossing:

1. The crossing strands are identified
2. The direction determines which strand is dominant
3. The instruction is executed with the current strand states as operands
4. The resulting state is assigned to the continuing strands
5. The crossing is recorded in the evidence log

**[HYPOTHESIS]** The evidence log is append-only. Executed crossings are never removed from the log.

**[OPEN]** Formal proof of the following: for any two execution traces producing identical final strand states, the evidence logs are distinguishable if and only if the execution histories differ.

---

## Chapter 4: Instruction Families

**[ORIGINAL]** Six instruction families are currently defined. Each is a hypothesis about a computational function that can be implemented through executable crossings.

### 4.1 Integrity Family

**Purpose:** Verify state transitions and maintain append-only evidence.

**[HYPOTHESIS]** An integrity crossing:
- Takes input state from two strands
- Applies a verification function (hash, signature, formal check)
- Either promotes the state to trusted (both strands carry verified state) or routes to recovery
- Records the verification event in the evidence log

**Governing laws:** Law 1, Law 2, Law 8.

### 4.2 Routing Family

**Purpose:** Direct execution through dynamically selected paths.

**[HYPOTHESIS]** A routing crossing:
- Evaluates a routing predicate on the current strand states
- Selects among available braid paths
- Ensures authority and verification crossings are present on all selected paths
- Records the routing decision

**Governing laws:** Law 4, Law 9.

### 4.3 Recovery Family

**Purpose:** Restore execution from defined failure states.

**[HYPOTHESIS]** A recovery crossing:
- Detects an anomaly in strand state
- Preserves current evidence (no discarding)
- Invokes a defined recovery procedure (checkpoint restoration, alternate path, state reconstruction)
- Records the recovery event

**Governing laws:** Law 5, Law 6, Law 7.

### 4.4 Role Exchange Family

**Purpose:** Transfer authority tokens between strands.

**[HYPOTHESIS]** A role exchange crossing:
- Identifies a source strand carrying an authority token
- Transfers the token to a target strand
- Removes the token from the source strand (no duplication)
- Requires verification of the transfer
- Records the transfer

**Governing laws:** Law 4, Law 9.

### 4.5 Authority Family

**Purpose:** Enforce permission requirements.

**[HYPOTHESIS]** An authority crossing:
- Evaluates the authority state of a strand
- Permits or denies the requested operation
- Routes to recovery if authority is insufficient
- Records the authority check

**Governing laws:** Law 4, Law 8, Law 9.

### 4.6 Memory Family

**Purpose:** Coordinate hot, warm, and cold state tiers.

**[HYPOTHESIS]** Memory crossings implement transitions between tiers:
- Hot-to-warm: active state moved to recent-inactive tier
- Warm-to-cold: recent state archived
- Cold-to-warm: archived state retrieved to recent-inactive tier
- Warm-to-hot: recent state promoted to active tier

**[HYPOTHESIS]** Circulation patterns (Figure-8, Möbius) determine the default movement of state between tiers.

---

## Chapter 5: The Governing Laws

**[HYPOTHESIS]** The ten governing laws are structural constraints that BCT proposes to enforce through braid topology, not software policy.

| Law | Statement | Enforcing Family |
|---|---|---|
| 1 | No active state becomes trusted without verification | Integrity |
| 2 | Evidence is append-only | All families |
| 3 | Trusted state is reproducible | Integrity, Recovery |
| 4 | Authority cannot be bypassed | Authority, Routing |
| 5 | Recovery preserves evidence | Recovery |
| 6 | Every trusted state has deterministic recovery | Recovery |
| 7 | History is never discarded | All families |
| 8 | Verification precedes promotion | Integrity |
| 9 | Every module has explicit authority | Authority |
| 10 | Governing laws remain immutable | Architecture |

**[OPEN]** Formal proof that the braid architecture enforces each law structurally — i.e., that no execution of a valid executable braid can violate the law, by construction.

---

## Chapter 6: Research Methodology

### 6.1 Falsifiability

The BCT hypotheses are designed to be falsifiable:

- H1 (efficiency): falsified if braid overhead exceeds conventional overhead on all tested computation classes
- H2 (recovery): falsified if checkpoint-based recovery consistently achieves higher fidelity
- H3 (verification): falsified if post-hoc verification consistently achieves equal or higher completeness
- H4 (authority): falsified if authority braids show no measurable bypass resistance improvement
- H5 (ISA): falsified if no acceptable overhead implementation exists on conventional hardware
- H6 (AI): falsified if no measurable explainability improvement is achieved

### 6.2 Validation Plan

See `research/BENCHMARK_PLAN.md` for detailed methodology.

### 6.3 Independent Validation

This thesis explicitly invites:
- Independent mathematical review of all definitions
- Independent replication of all benchmarks
- Peer review submission
- Critical analysis and attempted falsification

---

## Chapter 7: Open Problems

See `research/OPEN_PROBLEMS.md` for the full list. Key open problems:

1. Is the executable braid model Turing-complete?
2. What is the optimal crossing encoding for each instruction family on conventional hardware?
3. Can braid invariants (Jones polynomial, HOMFLY) serve as computational verification signatures?
4. What is the formal relationship between executable braids and Petri nets?
5. Can learning be defined as an executable braid operation?

---

## Conclusion

BCT proposes that executable braid topologies are worth investigating as computational substrates for history-preserving, authority-enforcing, verification-complete computation.

The thesis is grounded in established braid group mathematics. The original contributions are the definition of executable crossings, six instruction families, the layered architecture, and the ten governing laws.

The hypotheses are stated precisely. The validation plan is defined. The open problems are enumerated.

This is a research program, not a finished result. The thesis will be updated as evidence accumulates.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
