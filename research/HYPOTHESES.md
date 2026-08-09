# Research Hypotheses

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  

> Hypotheses are stated precisely so they can be tested and potentially falsified.  
> None of the following hypotheses are currently validated.  
> Each is marked with its current status.

---

## H1 — History Preservation Efficiency

**Statement:**
For computation classes where history preservation is mandatory, executable braid architectures will achieve lower total overhead than adding history preservation mechanisms (logging, event sourcing, journaling) on top of conventional architectures.

**Rationale:**
Conventional architectures discard history by design. Adding preservation requires separate logging infrastructure, storage overhead, and consistency management. BCT carries preservation structurally. For classes where preservation cannot be avoided, BCT may reduce net overhead.

**Falsification condition:**
H1 is falsified if, on defined benchmarks, braid overhead always equals or exceeds the overhead of conventional architecture + logging across all tested computation classes.

**Current status:** Untested. Requires simulator (Phase 2) and benchmark suite (Phase 3).

**Related benchmark:** BENCH-H1 in `research/BENCHMARK_PLAN.md`.

---

## H2 — Recovery Fidelity

**Statement:**
Recovery braid instructions will achieve higher fidelity restoration than checkpoint-based approaches for defined failure classes — specifically, failures that corrupt state but leave the surrounding execution context intact.

**Rationale:**
Checkpoint-based recovery restores to the nearest prior checkpoint, losing all computation since the checkpoint. BCT recovery preserves all intermediate evidence and repairs in place, potentially recovering computation that would be lost in checkpoint rollback.

**Falsification condition:**
H2 is falsified if checkpoint-based recovery consistently achieves equal or higher fidelity on defined failure benchmarks, and BCT recovery does not.

**Current status:** Untested.

**Related benchmark:** BENCH-H2 in `research/BENCHMARK_PLAN.md`.

---

## H3 — Verification Completeness

**Statement:**
Structural verification (woven into braid topology) will achieve higher completeness than post-hoc verification for defined computation classes — specifically, classes where intermediate state is as security-relevant as final state.

**Rationale:**
Post-hoc verification checks only the output. Structural verification verifies each state transition. For computations where a compromised intermediate state can produce a valid-looking output, structural verification catches violations that post-hoc verification misses.

**Falsification condition:**
H3 is falsified if post-hoc verification achieves equal completeness on defined benchmarks, or if BCT structural verification introduces unacceptable false positive rates.

**Current status:** Untested.

**Related benchmark:** BENCH-H3 in `research/BENCHMARK_PLAN.md`.

---

## H4 — Authority Bypass Resistance

**Statement:**
Authority braid crossings will reduce authority bypass vulnerability compared to software-layer authority enforcement, for defined threat models.

**Rationale:**
Software-layer authority can be bypassed when the enforcement code has bugs, is misconfigured, or is circumvented. BCT authority crossings are structural: the topology prevents execution without authority by construction. This reduces the attack surface for authority bypass.

**Falsification condition:**
H4 is falsified if a threat model is defined under which BCT authority crossings can be bypassed without modifying the braid structure, or if the bypass resistance improvement is not measurable on defined benchmarks.

**Current status:** Untested. Requires formal security analysis and threat model definition.

**Related benchmark:** BENCH-H4 in `research/BENCHMARK_PLAN.md`.

---

## H5 — Practical ISA

**Statement:**
A braid ISA can be simulated on conventional hardware (x86 or ARM) with acceptable overhead for at least one non-trivial application class.

**Operational definition of "acceptable overhead":**
Total overhead (BCT execution time / conventional execution time) ≤ 3× for a defined application class, where the conventional approach adds equivalent history preservation and verification.

**Rationale:**
If BCT cannot be implemented with reasonable efficiency on existing hardware, it cannot be evaluated empirically. H5 is a prerequisite for testing H1–H4.

**Falsification condition:**
H5 is falsified if the minimum achievable overhead on x86 and ARM exceeds the defined threshold for all tested application classes.

**Current status:** Untested. Requires simulator implementation (Phase 2).

**Related benchmark:** BENCH-H5 in `research/BENCHMARK_PLAN.md`.

---

## H6 — AI Reasoning Explainability

**Statement:**
Braid provenance structures will improve explainability metrics for AI reasoning systems on at least one defined benchmark compared to systems without braid provenance.

**Rationale:**
Current AI systems often produce outputs without preserving the causal chain of reasoning steps. Braid provenance attaches the evidence trail to the output structurally. This may improve explainability metrics (human evaluation, faithfulness, completeness of explanation).

**Falsification condition:**
H6 is falsified if braid provenance does not produce measurable improvement on defined explainability benchmarks, or if the improvement does not exceed the overhead cost.

**Current status:** Untested. Requires AI application prototype (Phase 5).

**Related benchmark:** BENCH-H6 in `research/BENCHMARK_PLAN.md`.

---

## Conjecture C1 — Turing Completeness

**Statement (mathematical conjecture, not empirical hypothesis):**
For sufficiently expressive instruction sets, the executable braid model is Turing-complete.

**Current status:** Open. No proof or disproof exists. This is a priority problem.

**See:** `research/OPEN_PROBLEMS.md` — OP-1.

---

## Conjecture C2 — Invariant Verification

**Statement:**
Classical braid invariants (Jones polynomial) classify computational equivalence classes of executable braids.

**Current status:** Open. No formal investigation has been completed.

**See:** `research/OPEN_PROBLEMS.md` — OP-3.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
