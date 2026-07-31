# Braid Family Template

> Use this template for every new braid family document in `braid_catalog/`.
> A template applied consistently turns concepts into a science, not a stack of powerful names.

---

# [Braid Name]

**BCT ID:** BCT-XXX
**BFR Level:** Level 0 / 1 / 2 / 3 / 4 / 5
**Canonical Question:** "?"

## Purpose

*One paragraph describing what computational problem this braid family solves and why it cannot be
addressed by a simpler mechanism.*

## Intended Computational Role

*Describe the role this braid plays in a larger BCT computation. What does it receive? What does it
produce? What invariant does it maintain?*

## Strand Types

- **Input strand**: *description*
- **Output strand**: *description*
- **Evidence strand**: *description*
- *(add additional strand types as required)*

## Crossing Semantics

| Opcode | Behavior |
|---|---|
| `FAMILY.OPCODE` | *Description of what the crossing does to strand state* |

## Direction of Information Flow

*Describe the primary direction of state flow (forward / reverse / bidirectional) and any
feedback loops.*

## Allowed Transformations

*List the permitted state transitions produced by crossings in this family, e.g.:*
- Active → Trusted (via VERIFY)
- Trusted → Certified (via PROMOTE)

## Invariants

*List the mathematical or logical properties that must hold before and after every crossing. Any
violation is a law violation and must halt execution.*

1. *Invariant 1*
2. *Invariant 2*

## Failure Modes

| Failure | Trigger Condition | Required Response |
|---|---|---|
| *Name* | *Condition that causes the failure* | *What the braid must do* |

## Recovery Behavior

*Describe how this braid interacts with BCT-005 (Recovery) and BCT-003 (Protection) when a failure
mode is triggered.*

## Authority Requirements

*List the authority scopes that crossings in this family require. Which crossings gate on
`AUTH.CHECK`?*

## Evidence Produced

*Describe what evidence records this braid emits to the BCT-008 (Evidence) log. Every crossing must
appear here.*

## Complexity

*Describe the computational complexity of the braid's critical path. Include space complexity for
the evidence strand.*

## Current Implementation Status

*Describe what exists in `braid_simulator/` that implements this family. Reference specific files
and classes.*

## Test Coverage

| Test File | What It Covers |
|---|---|
| `tests/...` | *Description* |

## Known Limitations

*List any open research questions, missing implementation details, or known gaps in the formal
specification.*

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
*Braided Computational Topology, 2026*
