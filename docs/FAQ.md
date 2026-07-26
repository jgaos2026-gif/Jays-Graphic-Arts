# Frequently Asked Questions

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## General

### What is Braided Computational Topology?

BCT is a research program investigating whether executable braid topologies can serve as computational structures for verification, authority, routing, recovery, memory, and provenance. It is a research prototype, not a production system.

### Who is this for?

Systems researchers, formal methods researchers, AI researchers, security researchers, and distributed systems researchers interested in alternative computational substrates. It is not currently intended for production deployment.

### Is this a replacement for conventional computing?

No. BCT is proposed as a new architectural family, not a replacement. Graphs did not replace trees. Matrices did not replace graphs. BCT, if validated, would represent an expansion of available computational structures, not a displacement.

### What is the current maturity level?

Early research prototype. Formal definitions exist. A prototype implementation is in early stages. Empirical benchmarks have not yet been run. No independent validation has occurred.

---

## Mathematics

### Is braid group theory established mathematics?

Yes. Braid groups were defined by Emil Artin in 1925. The algebraic structure, word problem decidability, invariants, and categorical properties of braid groups are well-established. BCT does not claim credit for any of this.

### What is original to this project?

The concept of **executable braids** — braids in which crossings carry computational instructions and perform work. The six instruction families (Integrity, Routing, Recovery, Role Exchange, Authority, Memory). The layered computational architecture. The braid ISA. The memory braid model.

### What mathematical fields does BCT build on?

Artin braid groups, algebraic topology, knot theory, category theory, directed algebraic topology, automata theory, lattice theory, Petri nets, tensor networks, persistent homology, and information theory. See `docs/REFERENCES.md`.

### Has the BCT mathematical framework been formally proved?

Some definitions have been formalized. Full proofs of the stated hypotheses do not yet exist. This is an active area of work. See `proofs/`.

---

## Architecture

### What are the ten core laws?

1. No active state becomes trusted without verification.
2. Evidence is append-only.
3. Trusted state is reproducible.
4. Authority cannot be bypassed.
5. Recovery preserves evidence.
6. Every trusted state has deterministic recovery.
7. History is never discarded.
8. Verification precedes promotion.
9. Every module has explicit authority.
10. Governing laws remain immutable.

These are architectural design laws governing the BCT system. They are hypotheses about what can be enforced structurally through braid topology.

### What is the difference between an active state and a trusted state?

An active state is currently executing but has not yet passed a verification crossing. A trusted state has passed an integrity crossing and is verified. The BCT architecture does not allow active states to be promoted to trusted states without verification (Law 1).

### What is the braid ISA?

The braid instruction set architecture defines crossing types, operand structures, and execution semantics for executable braids. It is an original research definition, not yet independently validated. See `architecture/ISA.md`.

### What is the memory braid architecture?

A three-tier model (hot, warm, cold) coordinated through braid crossing instructions. Circulation patterns (Figure-8, Möbius) define how state moves between tiers. See `architecture/MEMORY.md`.

---

## Research Status

### What are the main hypotheses?

See `research/HYPOTHESES.md` for the full list. In brief:

- H1: Braid architectures reduce net overhead for history-preserving computation classes.
- H2: Recovery braids achieve higher fidelity than checkpoint-based approaches.
- H3: Structural verification achieves higher completeness than post-hoc verification.
- H4: Authority braids reduce bypass vulnerability.
- H5: A braid ISA can be simulated on conventional hardware with acceptable overhead.
- H6: Braid provenance improves AI reasoning explainability.

None are currently validated.

### What would falsify this research?

- Proof that braid topologies cannot efficiently represent Turing-complete computation
- Empirical evidence that braid overhead always exceeds the overhead of adding preservation to conventional architectures
- Evidence that existing architectures already provide the claimed properties with lower overhead
- A demonstration that the instruction family definitions are mutually inconsistent

### What is the next milestone?

Completing the simulator and running initial benchmarks against defined baselines. See `docs/ROADMAP.md`.

### Can I contribute?

Yes. See `CONTRIBUTING.md`. Mathematical review, architecture review, prototype contributions, and independent benchmark runs are all welcome.

---

## Comparisons

### How does BCT relate to topological quantum computing?

*[INSPIRATION — not equivalence]* Topological quantum computing (Kitaev, Freedman et al.) uses braid operations on anyons for fault-tolerant quantum computation. BCT is inspired by the observation that braid structures preserve operational ordering and interaction history. BCT is classical computation theory, not quantum computing. The connection is structural inspiration, not technical derivation.

### How does BCT relate to blockchain or append-only logs?

Append-only evidence (Law 2) and history preservation (Law 7) share conceptual similarity with blockchain append-only ledgers. BCT is a computational architecture, not a distributed ledger. The similarity is in the design principle of preserving history structurally; the implementation approaches are different.

### How does BCT relate to functional programming?

Functional programming immutability and pure functions share the goal of preserving computation history through referential transparency. BCT approaches the same goal through topological structure rather than value immutability. These are complementary perspectives, not competing ones.

### How does BCT relate to event sourcing?

Event sourcing systems preserve the history of state changes as an append-only event log. BCT proposes that the topology of computation itself can carry this history structurally, rather than requiring a separate logging layer. Whether this offers advantages over event sourcing is an open empirical question (H1).

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
