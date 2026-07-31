# Why Many Braids

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  

> **[ORIGINAL]** The insight that there is no universal braid — that different computational purposes require different braid families — is the conceptual heart of this research program.

---

## The Single-Braid Temptation

When you first encounter braid groups, there is a natural temptation to ask:

> *Can all computation be expressed as one braid?*

The answer is almost certainly yes — in the same way that all computation can be expressed as Turing machine operations or lambda calculus. Universal models exist.

But that is not the right question for engineering.

The right question is:

> *Which braid topology best serves which computational purpose?*

---

## The Core Insight

**A braid is not a universal structure. Different braid patterns provide different strengths, constraints, failure behavior, information flow, and computational properties.**

This means: choosing the wrong braid family for a problem produces an architecture that fights its own structure.

Just as:
- A stack is the right structure for recursive function calls but wrong for associative lookup
- A queue is right for fair scheduling but wrong for priority ordering
- A tree is right for hierarchical data but wrong for cyclic relationships

Different braid families are right for different computational problems.

---

## The Design Rule

```
One computational purpose
        ↓
One selected braid family
        ↓
Defined crossing semantics
        ↓
Defined invariants
        ↓
Measured behavior
```

This is the complete design rule for BCT.

Every braid family in `braid_catalog/` was selected by asking: *what is the one computational purpose this braid serves?* The crossing semantics, invariants, and failure behavior follow from that purpose.

---

## Why This Matters

If you build a single braid to handle everything, you get an architecture where:
- Verification semantics conflict with routing semantics
- Recovery semantics compromise authority semantics
- Memory semantics obscure provenance semantics

Each compromise weakens all of them.

**[HYPOTHESIS]** Separate braid families with defined interactions compose without semantic conflict because each family governs only its own crossing semantics. Interactions between families are defined at the crossing points between families — they are explicit, not implicit.

---

## The Family Taxonomy

**[ORIGINAL]** BCT defines fourteen braid families, organized by purpose:

### Tier 1 — Trust and Correctness
| Family | Core purpose |
|---|---|
| Integrity | Verify state; preserve evidence |
| Verification | Challenge claims against independent evidence |
| Authority | Enforce structural permissions |
| Provenance | Track origin and transformation of every value |

### Tier 2 — Execution and Navigation
| Family | Core purpose |
|---|---|
| Routing | Select execution paths with authority |
| Scheduling | Coordinate interleaved work with dependency history |
| Communication | Move messages with delivery proof |

### Tier 3 — Resilience
| Family | Core purpose |
|---|---|
| Recovery | Repair execution while preserving evidence |
| Role Exchange | Transfer authority atomically |

### Tier 4 — State Management
| Family | Core purpose |
|---|---|
| Memory | Coordinate hot/warm/cold state transitions |
| Compression | Reduce size while preserving provenance |

### Tier 5 — Future Families
| Family | Core purpose |
|---|---|
| Consensus | Distributed agreement with disagreement history |
| Learning | Verified model adaptation |
| Simulation | Branching possible worlds with collapse records |

---

## How Families Interact

**[HYPOTHESIS]** Braid families interact at defined crossing points:

```
Integrity Braid ──────────╮
                    AUTH.CHECK crossing
Authority Braid ───────────╯
        ↓
INTEG.VERIFY crossing
        ↓
Verified state enters Routing Braid
```

A crossing between two families is always an explicit instruction. There is no implicit interaction.

This means: the interaction protocol between any two families is a research question with a defined answer, not an emergent behavior.

---

## The Anti-Pattern

**Do not do this:**

```
One mega-braid with all crossings from all families mixed together
```

**[HYPOTHESIS]** This produces an architecture where:
- Invariants of one family conflict with invariants of another
- Evidence from one family obscures evidence from another
- Recovery in one family cannot distinguish its failures from failures in adjacent families

Separation of families is an architectural requirement, not a style preference.

---

## Comparison to Other Multi-Structure Architectures

**[CS-TRAJECTORY]** Modern computing already uses multiple specialized structures for specialized purposes:

- Databases: B-trees for indexes, LSM-trees for write-heavy workloads, heaps for free-space management
- Networking: spanning trees for broadcast, shortest-path trees for routing, clique topologies for fault tolerance
- AI: attention mechanisms for sequence relationships, convolutional structures for spatial patterns, recurrent structures for temporal dependencies

BCT applies the same principle to computational history and authority preservation: one structure per computational purpose.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
