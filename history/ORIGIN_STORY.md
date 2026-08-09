# Origin Story

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## The Starting Observation

The research began with a structural observation about conventional computing:

Modern architectures are optimized to answer *where information ends up*. The most difficult problems in systems engineering — debugging, auditing, recovery, provenance, authority tracking — all require knowing *how information got there*.

This is not a flaw in conventional architectures. It is a correct design choice for general-purpose computation. But it raises a question: for computation classes where history preservation is mandatory, does there exist a structural model that carries this requirement natively?

---

## The Braid Insight

Braid groups preserve ordered interaction, crossing history, and structural consequence as inherent properties — not as added-on features. Two braids can have identical closures (final states) while having completely different strand histories. The topology records the difference.

This structural property matched exactly what systems engineering kept needing to reconstruct.

---

## The Executable Crossing

The key original step: making crossings *executable*. Classical braid groups are passive mathematical objects. Their crossings encode relationships. They do not perform computation.

The question became: what if each crossing carries an instruction and performs computational work?

This transformation — from passive mathematical structure to active computational substrate — is the foundational original contribution.

---

## Many Braids, Not One

The second key insight: there is no universal braid. Different computational purposes require different braid families. The integrity properties of verification crossings conflict with the permissiveness requirements of routing crossings. They should be separate families.

This led to the design rule: one purpose → one braid family → defined crossing semantics → defined invariants → measured behavior.

---

## From JGA to BCT

This research originated within and was separated from other work to stand independently as a research program. The BCT research program is now documented in this repository.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
