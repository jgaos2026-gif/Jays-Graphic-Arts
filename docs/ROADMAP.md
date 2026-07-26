# Research Roadmap

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  

---

## Philosophy

This roadmap prioritizes foundational rigor over rapid feature expansion. Each milestone builds the mathematical backbone required to make the next milestone meaningful.

---

## Phase 0 — Foundations (Current)

**Goal:** Establish precise formal definitions across all components.

- [x] Define executable braid concept
- [x] Define six instruction families (Integrity, Routing, Recovery, Role Exchange, Authority, Memory)
- [x] Specify layered computational architecture
- [x] Define ten governing laws
- [x] Draft braid ISA (initial)
- [x] Draft memory braid architecture
- [ ] Formalize all definitions using category theory
- [ ] Relate braid ISA to established automata models
- [ ] Prove or disprove Turing completeness of executable braid model
- [ ] Submit formal definitions for peer review

---

## Phase 1 — Mathematical Backbone

**Goal:** Establish rigorous mathematical foundations for each instruction family.

- [ ] Formal proof: integrity crossing preserves append-only invariant
- [ ] Formal proof: authority crossing prevents bypass under defined threat model
- [ ] Formal proof: recovery crossing preserves evidence under defined failure model
- [ ] Categorical semantics for braid instruction composition
- [ ] Directed algebraic topology model of execution paths
- [ ] Persistent homology analysis of evolving braid computations
- [ ] Petri net translation: establish equivalence or difference with BCT concurrency model
- [ ] Publish mathematical definitions as technical report

---

## Phase 2 — Simulator

**Goal:** Build a working simulator for executable braids on conventional hardware.

- [ ] Simulator architecture design
- [ ] Implement core braid data structures
- [ ] Implement crossing execution engine
- [ ] Implement each instruction family
- [ ] Implement three-tier memory model
- [ ] Implement evidence log
- [ ] Run correctness tests against formal definitions
- [ ] Publish simulator source code with documentation

---

## Phase 3 — Benchmarks

**Goal:** Empirically test hypotheses H1–H5 using the simulator.

- [ ] Define baseline comparison systems (see `research/BENCHMARK_PLAN.md`)
- [ ] H1 benchmark: history preservation overhead vs. conventional + logging
- [ ] H2 benchmark: recovery fidelity vs. checkpoint-based recovery
- [ ] H3 benchmark: verification completeness vs. post-hoc verification
- [ ] H4 benchmark: authority bypass resistance under defined threat models
- [ ] H5 benchmark: overhead of braid ISA simulation on x86 and ARM
- [ ] Publish benchmark results with full methodology

---

## Phase 4 — Independent Validation

**Goal:** Obtain independent review of mathematical definitions and benchmark results.

- [ ] Submit to peer-reviewed venue (venue TBD based on scope)
- [ ] Invite independent replication of benchmark results
- [ ] Address reviewer feedback
- [ ] Revise definitions and claims based on validation outcomes
- [ ] Update this repository to reflect validated vs. unvalidated claims

---

## Phase 5 — AI Applications (H6)

**Goal:** Test braid provenance structures in AI reasoning contexts.

- [ ] Define AI explainability benchmark (see `research/AI_APPLICATIONS.md`)
- [ ] Implement braid provenance layer for a defined AI reasoning system
- [ ] H6 benchmark: explainability improvement vs. baseline
- [ ] Publish results

---

## Phase 6 — Distributed Runtime

**Goal:** Test consensus braid and routing braid hypotheses in distributed execution.

- [ ] Formally define consensus braid
- [ ] Implement distributed braid runtime prototype
- [ ] Benchmark consensus braid vs. established consensus algorithms (Raft, Paxos)
- [ ] Publish results

---

## Long-Term Research Directions

These are not scheduled milestones. They are possible future directions contingent on Phase 1–4 results.

- Learning braid family definition and implementation
- Compression braid family definition
- Hardware architecture exploration (FPGA prototype)
- Domain-specific applications (security, provenance tracking, AI infrastructure)

---

## What This Roadmap Does Not Include

- A release date for production software
- A claim that all hypotheses will be validated
- A promise that the architecture will outperform conventional systems

The roadmap is driven by evidence. If benchmarks show that braid architectures do not provide advantages for any tested class of problems, that is a valid and important result.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
