# Computational Topology

> **[ESTABLISHED]** unless labeled **[ORIGINAL]** or **[HYPOTHESIS]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## 1. What Is Computational Topology?

**[ESTABLISHED]** Computational topology is the field studying topological properties of spaces and structures using computational methods, and conversely applying topological ideas to computation. Key areas include:

- Computing topological invariants algorithmically
- Persistent homology and topological data analysis
- Discrete Morse theory
- Simplicial complexes in computation
- Directed algebraic topology for concurrent systems

---

## 2. Relevant Established Fields

### 2.1 Persistent Homology

**[ESTABLISHED]** Persistent homology (Edelsbrunner, Letscher & Zomorodian, 2002) tracks how topological features (connected components, loops, voids) appear and disappear as a parameter changes. The **persistence diagram** encodes feature lifetimes as a multiset of birth-death pairs.

Applications include shape recognition, data analysis, and sensor networks.

**[HYPOTHESIS — BCT]** Persistent homology may apply to evolving braid computation structures: tracking how computational features (authority regions, verification domains, recovery paths) persist across execution time. This is an open research direction.

### 2.2 Directed Algebraic Topology

**[ESTABLISHED]** Directed algebraic topology (Grandis, 2009) extends classical algebraic topology to spaces with a directionality — paths that cannot be traversed in both directions. This models concurrent systems where execution paths have a defined time ordering.

**[ESTABLISHED]** Directed spaces, d-spaces, and their directed homotopy groups capture the structure of concurrent execution in ways that undirected topology cannot.

**[HYPOTHESIS — BCT]** Directed algebraic topology is directly applicable to BCT: execution paths through a braid are directed (top to bottom), and the directed homotopy structure of an executable braid may capture the equivalence classes of computation with identical evidence traces.

### 2.3 Simplicial Complexes

**[ESTABLISHED]** A simplicial complex is a combinatorial structure built from vertices, edges, triangles, tetrahedra, and their higher-dimensional analogs (simplices), satisfying closure properties.

**[ESTABLISHED]** Simplicial complexes are used in computational topology as discrete approximations to continuous spaces.

**[HYPOTHESIS — BCT]** Braid crossing structures may be modeled as simplicial complexes, enabling the application of computational topology algorithms to braid analysis.

### 2.4 Discrete Morse Theory

**[ESTABLISHED]** Discrete Morse theory (Forman, 1998) provides a combinatorial analog of smooth Morse theory, enabling the topological simplification of cell complexes while preserving homology.

**[HYPOTHESIS — BCT]** Discrete Morse theory may provide a framework for simplifying executable braid structures — collapsing sequences of crossings that do not change the topological or computational outcome — enabling efficient braid representation.

---

## 3. BCT Topological Framework

### 3.1 The Braid as a Directed Space

**[HYPOTHESIS]** An executable braid defines a directed topological space:

- **Points**: strand positions at each moment of execution
- **Directed paths**: execution traces along strands from top to bottom
- **Crossings**: interaction events between paths

The directed homotopy of two execution traces is well-defined when they traverse the same crossings in the same order. Two traces are homotopic if one can be continuously deformed into the other while preserving the crossing structure.

### 3.2 Topological Properties of Instruction Families

**[HYPOTHESIS]** Each instruction family defines a distinct topological property of the braid:

| Family | Topological property |
|---|---|
| Integrity | The integrity crossing set is contractible (no verification can be circumvented by homotopy) |
| Authority | Authority crossings form a connected subcomplex |
| Recovery | Recovery paths form an alternative connected component |
| Memory | Memory state forms a stratified space across hot/warm/cold tiers |

These are research hypotheses. Formal topological proofs are open problems.

### 3.3 Invariants as Computational Signatures

**[ESTABLISHED]** Classical braid invariants (Alexander polynomial, Jones polynomial, HOMFLY polynomial) are topological invariants — they depend only on the isotopy class of the braid, not the specific geometric representation.

**[HYPOTHESIS]** In executable braids, these invariants may serve as computational verification signatures: two executable braids that are topologically equivalent (same invariants) may produce equivalent computation results. If this can be proved, invariant computation becomes a verification mechanism.

This is an open research question requiring formal investigation.

---

## 4. Relationship to Concurrent Systems

**[ESTABLISHED]** Concurrent programs are modeled using various topological structures:

- **Higher-dimensional automata** (Pratt, 1991; van Glabbeek, 2006): cells represent concurrent events; topology captures independence vs. conflict
- **Petri nets**: a well-established formalism for concurrent computation with firing sequences and reachability
- **Directed algebraic topology**: provides homotopy invariants for concurrent executions

**[HYPOTHESIS]** BCT's braid model is a specific instance of a concurrent execution structure. The directed algebraic topology of executable braids should be related to higher-dimensional automata. Establishing this relationship formally is an open problem.

**[OPEN]** What is the precise relationship between the language of an executable braid automaton and the language of a Petri net with the same concurrency structure?

---

## 5. Open Topological Problems in BCT

1. **Braid equivalence and computation:** When are two executable braids topologically equivalent in a way that implies computational equivalence?
2. **Persistent homology of execution:** Can persistent homology identify which computational features are stable across execution variants?
3. **Directed homotopy and evidence:** Do two execution traces with the same directed homotopy class always produce the same evidence log?
4. **Invariant verification:** Can Jones or HOMFLY polynomial invariants serve as efficient verification signatures for completed executable braid computations?
5. **Simplification:** Can discrete Morse theory eliminate redundant crossings from executable braids without changing their computational behavior?

---

## References

- Edelsbrunner, H., Letscher, D., & Zomorodian, A. (2002). Topological persistence and simplification. *Discrete and Computational Geometry*, 28(4), 511–533.
- Grandis, M. (2009). *Directed Algebraic Topology.* Cambridge University Press.
- Forman, R. (1998). Morse theory for cell complexes. *Advances in Mathematics*, 134(1), 90–145.
- Fajstrup, L. et al. (2016). *Directed Algebraic Topology and Concurrency.* Springer.
- Pratt, V. (1991). Modeling concurrency with geometry. *POPL 1991*.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
