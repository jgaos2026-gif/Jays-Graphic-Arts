# T-800 OMEGA72 Guardian Runtime Model

> **CLASSIFICATION:** HYPOTHESIS (Outside Formal BCT Stack)
> **STATUS:** Research Proposal & Governance Challenge

---

## Overview

T-800 OMEGA72 is a proposed guardian-runtime architecture designed to monitor topological
invariants across BCT streams. It is explicitly kept outside the formal BCT stack until the
following three requirements are solved and independently verified.

---

## Open Governance Blockers

T-800 OMEGA72 MUST NOT be integrated into the formal BCT stack until all three blockers below are
closed with independently verifiable artifacts. No exceptions.

### Blocker 1 — Non-Circular Trust Model

**Requirement:** Establish a formal proof that the guardian cannot be corrupted by the same state
transitions it monitors.

**Problem:** A guardian that uses BCT crossings to verify BCT crossings creates a circular
dependency. If the guardian's authority token is issued by the same `AuthorityManager` it
oversees, an adversary who compromises the manager compromises the guardian simultaneously.

**Resolution criteria:** A mathematical proof, committed as a proof artifact in `proofs/`, that
demonstrates a non-circular trust chain from guardian to monitored system. The proof must be
checked by an independent reviewer.

**Current status:** Open.

---

### Blocker 2 — Bounded Detection-Latency Specification

**Requirement:** Establish a mathematical upper bound on the time elapsed between topological fault
injection and guardian isolation hook execution.

**Problem:** Without a latency bound, the guardian provides no security guarantee. An adversary who
can inject a fault and exfiltrate state before the guardian isolates the fault has bypassed the
guardian entirely.

**Resolution criteria:** A published latency bound of the form `L ≤ f(n, d)` where `n` is the
number of monitored strands and `d` is the braid depth, with a simulator benchmark demonstrating
the bound holds for the tested configuration.

**Current status:** Open.

---

### Blocker 3 — Independent Guardian-Verification Mechanism

**Requirement:** Build a secondary, decoupled observer protocol capable of verifying the
guardian's own health and decisions.

**Problem:** A guardian that is the sole authority on its own correctness cannot be audited. If
the guardian malfunctions or is compromised, there is no mechanism to detect it.

**Resolution criteria:** A working implementation of a secondary observer that reads the
guardian's BCT-008 evidence log, independently replays decisions, and emits disagreement records
to a separate append-only log not writable by the guardian.

**Current status:** Open.

---

## Canonical Status

T-800 OMEGA72 remains a **Proposed Guardian Hypothesis** until all three blockers above are
resolved. It is filed in `research/` rather than `architecture/` or `braid_catalog/` to make
this classification unambiguous.

It is not a BCT braid family. It does not have a BCT ID. It does not appear in BFR_REGISTRY.md.

---

## Relationship to SB-712

SB-712 (see `architecture/SB712_DUPLEX_CONTINUITY_PROTOCOL.md`) is the cross-braid continuity
protocol and is part of the formal BCT stack. T-800 OMEGA72 is a proposed layer *on top of*
SB-712, not a replacement for it. SB-712 does not depend on T-800 OMEGA72.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
*Braided Computational Topology, 2026*
