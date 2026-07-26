# Design Philosophy

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  

---

## The Twelve Principles

### 1. Structure over Policy
Authority, verification, and evidence preservation are structural properties of the braid topology — not policies enforced by a software layer on top.

A software policy can be bypassed when the code has a bug, is misconfigured, or is circumvented. A structural property cannot be bypassed without changing the structure itself.

### 2. History Is Architecture
The path of a computation is as meaningful as its result. BCT treats history as a first-class architectural element, not a logging afterthought.

### 3. Evidence Is Permanent
Evidence is append-only. Nothing that happened is ever deleted. Recovery does not erase failure — failure becomes evidence.

### 4. One Purpose, One Braid
Each braid family has exactly one primary computational purpose. Mixing purposes within a single family violates the design. See `manifesto/WHY_MANY_BRAIDS.md`.

### 5. Verification Precedes Promotion
No state becomes trusted without a verification crossing. This is not a rule that can be waived — it is a structural invariant.

### 6. Authority Is Explicit
Every strand carries an explicit authority token. There is no implicit permission. If no authority token is present, no promotion occurs.

### 7. Failure Is Knowledge
When execution fails, the failure event is preserved with full context. The system does not pretend failure did not happen. Quarantine preserves the failed state as evidence.

### 8. Recovery Is Repair, Not Erasure
BCT recovery restores execution while preserving all prior evidence. It does not roll back to a prior state and discard intermediate history. The history of the failure is part of the evidence record.

### 9. Novelty Is Insufficient
An architectural proposal that cannot be implemented, measured, and reproduced is an interesting idea — not engineering. BCT is designed to be testable. Every hypothesis is falsifiable.

### 10. Honesty of Claims
Every claim in this repository is classified. Established mathematics is not presented as original. Hypotheses are not presented as results. Speculation is labeled as speculation.

### 11. The Separation Principle
Established foundations, original contributions, research hypotheses, and speculative directions are always kept in separate lanes. Mixing them without labels is the most common way a research program loses credibility.

### 12. The Smallest Working Piece First
The most credible path forward is demonstrating that the smallest working piece is coherent, executable, testable, and original. The rest of the architecture unfolds braid by braid — not as one magnificent thundercloud.

---

## What These Principles Reject

- Security through obscurity
- Claims without evidence
- History as an afterthought
- Policy substituting for structure
- Complexity as a substitute for correctness
- Philosophy as a substitute for implementation

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
