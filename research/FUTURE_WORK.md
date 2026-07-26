# Future Work

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

> This document describes planned research directions beyond the current roadmap.  
> All items here are **[HYPOTHESIS]** or **[OPEN]** — none are committed deliverables.

---

## Near-Term (Post Phase 3)

### FW-1: Consensus Braid

**Description:** Formally define a consensus braid instruction family for distributed agreement problems.

**Motivation:** Distributed systems require consensus — multiple agents agreeing on a shared state. Current consensus algorithms (Raft, Paxos, BFT variants) agree on a final state but discard the history of the consensus process. A consensus braid would preserve the full history of agreement and disagreement, producing an auditable consensus record.

**Research questions:**
- Can a consensus braid be defined with equivalent safety and liveness properties to Raft?
- Does the evidence preservation of consensus braids provide auditability benefits?
- What is the overhead compared to Raft/Paxos?

**Prerequisites:** OP-7 (distributed braids), Phase 3 benchmark results.

---

### FW-2: Learning Braid

**Description:** Formally define a learning braid instruction family where model adaptation is expressed as braid operations.

**Motivation:** Neural network training updates parameters without preserving provenance of individual updates. A learning braid would express each weight update as a crossing with full evidence — who authorized the update, what data drove it, what the update value was, and what verification was applied.

**Research questions:**
- Can gradient descent be expressed as a sequence of learning crossings?
- Does learning braid provenance improve model auditability?
- Can learning braids support unlearning (removing a specific training contribution)?

**Prerequisites:** H6 validation, Phase 5 AI application work.

---

### FW-3: Compression Braid

**Description:** Define a compression braid instruction family for structural braid simplification.

**Motivation:** Long-running braids accumulate large evidence logs. A compression braid would reduce the structural size of a braid while preserving its computational semantics and evidence invariants.

**Research questions:**
- Can discrete Morse theory (OP-2) guide braid compression?
- What is the minimum evidence required to preserve deterministic replay?
- Can braid invariants certify that compression is semantics-preserving?

**Prerequisites:** OP-1 (Turing completeness), OP-3 (invariant interpretation).

---

## Medium-Term (Post Phase 4)

### FW-4: Hardware Prototype

**Description:** Implement a BCT execution engine on FPGA hardware.

**Motivation:** Software simulation (Phase 2) establishes feasibility but not performance characteristics at hardware speed. An FPGA implementation would provide real performance data and explore hardware-level optimization opportunities.

**Prerequisites:** H5 validation (acceptable simulation overhead), Phase 3 benchmarks.

---

### FW-5: Domain-Specific Braid Languages

**Description:** Define domain-specific languages (DSLs) for expressing executable braids in specific application domains.

**Candidates:**
- Financial transaction braids (audit, authority, recovery requirements)
- Medical record braids (provenance, access control, immutable history)
- AI governance braids (decision provenance, authority tracking)
- Security audit braids (tamper-evident execution records)

**Prerequisites:** Phase 3 results identifying strongest application classes.

---

### FW-6: Formal Verification of BCT Implementations

**Description:** Formally verify the correctness of BCT simulator and prototype implementations against the formal semantics.

**Tools candidates:** Coq, Isabelle/HOL, Lean 4, TLA+.

**Prerequisites:** OP-2 (formal semantics).

---

## Long-Term (Phase 6+)

### FW-7: Topological Complexity Theory

**Description:** Develop a complexity theory for executable braids — defining complexity classes, reductions, and completeness results analogous to classical computational complexity theory.

**Research questions:**
- What is the braid-width complexity of defined problem classes?
- Are there problems with polynomial-width braid solutions but no polynomial-time conventional solution?
- How do braid complexity classes relate to classical complexity classes (P, NP, PSPACE)?

---

### FW-8: Quantum BCT

**Description:** Investigate whether BCT instruction families can be implemented using topological quantum computing operations (non-Abelian anyons).

**Motivation:** Topological quantum computing already uses braid operations for fault-tolerant quantum gates. A quantum BCT implementation would combine the structural history preservation of BCT with the fault tolerance of topological quantum computing.

**Note:** This is speculative. It depends on advances in topological quantum hardware that do not yet exist.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
