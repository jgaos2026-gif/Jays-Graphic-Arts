# Routing Architecture

> All content is **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Design Philosophy

**[HYPOTHESIS]** Routing braids move information through dynamically selected paths while preserving authority, verification, and evidence at every point. No routing decision is taken silently — every path selection is recorded.

---

## Routing Crossings

**SELECT crossing:** Evaluates a routing predicate against current strand state and selects among available paths. The predicate, the selected path, and the rejected paths are all recorded in the evidence log.

**FORK crossing:** Duplicates a state onto two strands for parallel processing. Both strands carry the same initial state; they diverge from this point. The fork event is recorded.

**JOIN crossing:** Merges two strand states into one. The join function is a parameter (e.g., union, intersection, consensus). Both input states must be trusted; the merged state begins as active and must pass verification.

**REDIRECT crossing:** Reroutes a strand from its current path to an alternate path based on a condition. Used for congestion avoidance and fault rerouting.

**REPLAY crossing:** Reconstructs a strand state from the evidence log by replaying recorded crossings. The replayed state is subject to fresh verification.

---

## Path Selection

**[HYPOTHESIS]** All available routing paths in a BCT braid must:
- Have defined authority crossings
- Have defined verification crossings
- Have defined recovery paths
- Be reachable from the current braid position

A routing crossing may only select among paths that satisfy these requirements. Paths that lack any of these properties cannot be selected by a routing crossing.

**[HYPOTHESIS]** This means that rerouting cannot bypass authority or verification, even in failure scenarios. If no valid path is available, execution routes to recovery.

---

## Adaptive Routing

**[HYPOTHESIS]** Routing predicates may evaluate:
- Current strand authority state
- Current braid load (number of active crossings in each region)
- Evidence log state (prior routing decisions and their outcomes)
- External signals (congestion indicators from neighboring braids)

This enables load balancing and congestion avoidance within defined authority bounds.

---

## Deterministic Replay

**[HYPOTHESIS]** A BCT execution is deterministically replayable: given the initial state and the evidence log, the complete execution can be reconstructed. This means:

- Routing decisions are recorded with full predicates and outcomes
- A replay can follow the same path or be directed to follow an alternate path
- Replayed execution produces the same result as original execution (given the same inputs)

---

## Relationship to Mixture-of-Experts

**[CS-TRAJECTORY]** Mixture-of-experts (MoE) architectures in AI models use routing mechanisms to select which expert subnetworks process each input. This is a form of computational routing already deployed at scale.

**[HYPOTHESIS]** BCT routing braids can be viewed as a formal generalization of MoE routing: the routing predicate selects among braid paths (analogous to expert selection), with defined authority, verification, and evidence requirements.

---

## Open Problems

1. Formal proof that routing crossings cannot select paths lacking authority or verification crossings
2. Optimal routing predicate evaluation under time constraints
3. Routing in distributed braids: how are routing decisions coordinated across multiple braid regions?
4. Relationship between BCT routing and established network routing algorithms

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
