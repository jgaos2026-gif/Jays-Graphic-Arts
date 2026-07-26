# Topological Quantum Computing

> **[ESTABLISHED]** — prior work that provides the strongest direct support for BCT's core intuitions.  
> BCT builds on this inspiration but is not quantum computing.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois (compilation)

---

## Core Result

**[ESTABLISHED]** Topological quantum computing (TQC) uses braid operations on non-Abelian anyons — quasiparticles in certain two-dimensional quantum systems — to implement fault-tolerant quantum gates.

The key property: the quantum gate performed depends only on the *topology* of the braid (the sequence of crossings), not on the precise geometric path taken. Small local perturbations that preserve the braid topology do not change the computation.

**This establishes, in physics: a braid can be an operation, not merely a picture.**

---

## Foundational Papers

**Kitaev, A. (2003).** Fault-tolerant quantum computation by anyons. *Annals of Physics*, 303(1), 2–30.  
Introduces the toric code and proposes using non-Abelian anyons for topological quantum computation.

**Freedman, M., Kitaev, A., Larsen, M., & Wang, Z. (2003).** Topological quantum computation. *Bulletin of the AMS*, 40(1), 31–38.  
Formalizes the connection between braid group representations and quantum gate sets.

**Nayak, C., Simon, S. H., Stern, A., Freedman, M., & Das Sarma, S. (2008).** Non-Abelian anyons and topological quantum computation. *Reviews of Modern Physics*, 80(3), 1083.  
Comprehensive review of the field.

---

## What BCT Borrows

**[INSPIRATION — not equivalence]**

BCT borrows the structural intuition that braid crossings can carry and execute computational meaning. The implementation is entirely different:

| Topological QC | BCT |
|---|---|
| Non-Abelian anyons | Software strand states |
| Quantum superposition | Classical parallel execution |
| Unitary transformations | Defined crossing instruction functions |
| Quantum fault tolerance | Structural evidence preservation |
| Quantum hardware | Conventional hardware simulation |

The connection is: in both cases, a crossing in a braid changes the computational state according to a defined rule, and the topology of the crossing sequence matters.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
