# Glossary

**Braided Computational Topology (BCT)**  
The research program investigating whether executable braid topologies can serve as computational structures. An original contribution of this project.

**Braid Group (Bₙ)**  
*[ESTABLISHED]* The algebraic group of braids on n strands, with generators σ₁…σₙ₋₁ subject to Artin's relations. Defined by Emil Artin, 1925.

**Braid**  
*[ESTABLISHED]* A collection of n non-intersecting monotone paths connecting n top points to n bottom points. Braids compose by stacking; every braid has an inverse.

**Executable Braid**  
*[ORIGINAL]* A braid in which each crossing is an executable crossing — carrying a computational instruction from a defined family. The core original concept of BCT.

**Executable Crossing**  
*[ORIGINAL]* A 4-tuple `(strand_i, strand_j, direction, instruction)` in which the crossing performs computational work. Distinguished from a classical braid crossing, which is a passive mathematical relationship.

**Instruction Family**  
*[ORIGINAL]* A defined class of executable crossing instructions grouped by computational purpose. Current families: Integrity, Routing, Recovery, Role Exchange, Authority, Memory.

**Integrity Braid**  
*[ORIGINAL — HYPOTHESIS]* A braid whose crossings perform verification instructions, maintaining provable computational correctness and append-only evidence.

**Routing Braid**  
*[ORIGINAL — HYPOTHESIS]* A braid whose crossings perform routing instructions, moving information through dynamically selected verified paths.

**Recovery Braid**  
*[ORIGINAL — HYPOTHESIS]* A braid whose crossings perform recovery instructions, repairing damaged execution while preserving evidence.

**Authority Braid**  
*[ORIGINAL — HYPOTHESIS]* A braid whose crossings perform authority instructions, structurally enforcing permission requirements.

**Role Exchange**  
*[ORIGINAL — HYPOTHESIS]* The transfer of an authority token from one strand to another through a defined crossing instruction. The transfer is atomic and the source strand loses the token.

**Memory Braid**  
*[ORIGINAL — HYPOTHESIS]* A braid coordinating hot, warm, and cold memory tiers through defined crossing instructions.

**Hot Memory**  
*[ORIGINAL — HYPOTHESIS]* The active execution tier of the memory braid. High bandwidth, limited capacity.

**Warm Memory**  
*[ORIGINAL — HYPOTHESIS]* The recent-but-inactive tier. Moderate availability.

**Cold Memory**  
*[ORIGINAL — HYPOTHESIS]* The archived tier. Unlimited capacity with deterministic retrieval.

**Figure-8 Circulation**  
*[ORIGINAL — HYPOTHESIS]* A memory circulation pattern in which state circulates through a figure-eight braid path between hot and warm tiers, supporting temporal locality.

**Möbius Circulation**  
*[ORIGINAL — HYPOTHESIS]* A memory circulation pattern using a Möbius topology for symmetric access across all execution contexts.

**Memory Pocket**  
*[ORIGINAL — HYPOTHESIS]* A bounded region of the braid where state is held temporarily during computation, created and closed by memory crossing instructions.

**Stitched Storage**  
*[ORIGINAL — HYPOTHESIS]* A storage pattern connecting non-adjacent braid regions through stitch crossings, enabling efficient access to related state.

**Trusted State**  
*[ORIGINAL — HYPOTHESIS]* A state that has passed an integrity crossing. Distinguished from an active (unverified) state. Governed by Law 1 and Law 8.

**Evidence**  
*[ORIGINAL — HYPOTHESIS]* The complete append-only record of state transitions, verifications, and recovery events. Governed by Law 2 and Law 7.

**Authority Token**  
*[ORIGINAL — HYPOTHESIS]* A token carried by a strand that determines its permissions. Transferable through role exchange crossings; not duplicable.

**Deterministic Replay**  
*[ORIGINAL — HYPOTHESIS]* The property that a computation can be re-executed from its braid record to produce identical results.

**Braid ISA**  
*[ORIGINAL — HYPOTHESIS]* The instruction set architecture defined for executable braids. Specifies crossing types, operand structures, and execution semantics.

**Computational Layer**  
*[ORIGINAL — HYPOTHESIS]* One of eight defined processing stages: Input, Authority, Verification, Execution, Recovery, Certification, Persistence, Evidence.

**Closure**  
*[ESTABLISHED]* The operation connecting the top endpoints of a braid to its bottom endpoints, producing a knot or link. Used in BCT to define completed computation cycles.

**Braid Word**  
*[ESTABLISHED]* A sequence of generators and their inverses representing a braid. The word problem for braid groups is decidable.

**Isotopy**  
*[ESTABLISHED]* The equivalence relation on braids: two braids are isotopic if one can be continuously deformed into the other through defined Reidemeister-type moves.

**Algebraic Topology**  
*[ESTABLISHED]* The mathematical field studying topological spaces through algebraic invariants. One of the foundational fields for BCT.

**Category Theory**  
*[ESTABLISHED]* The mathematical study of abstract structures and composition. Provides formal language for braid instruction composition in BCT.

**Persistent Homology**  
*[ESTABLISHED]* A computational topology technique for analyzing how topological features persist across scales. Relevant for analyzing evolving braid computation structures.

**Petri Net**  
*[ESTABLISHED]* A mathematical model of concurrent computation. A comparison baseline for BCT execution models.

**Tensor Network**  
*[ESTABLISHED]* A graphical representation of multi-linear maps. Relevant for structured information flow in multi-strand braid operations.
