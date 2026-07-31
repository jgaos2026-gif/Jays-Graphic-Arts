# Benchmark Plan

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  

> This document defines the evaluation methodology for each hypothesis.  
> Benchmarks cannot be run until the simulator (Phase 2) is complete.

---

## Methodology Principles

1. **Baselines first:** For every BCT benchmark, define the conventional baseline before defining the BCT approach
2. **Controlled comparison:** BCT and baseline must solve the same problem with equivalent correctness guarantees
3. **Multiple metrics:** Measure latency, throughput, storage overhead, and correctness — not a single metric
4. **Reproducibility:** All benchmarks must be runnable from the published simulator with documented parameters
5. **Negative results are valid:** A benchmark showing that BCT does not outperform the baseline is a valid and important result

---

## BENCH-H1: History Preservation Efficiency

**Hypothesis tested:** H1 — Braid architectures reduce overhead for history-preserving computation.

**Baseline system:** PostgreSQL with write-ahead logging + event sourcing layer (equivalent history preservation)

**BCT system:** BCT simulator with integrity and memory instruction families

**Benchmark scenarios:**

| Scenario | Description |
|---|---|
| B1-A | Sequential state transitions with full history required |
| B1-B | Concurrent state transitions with consistency requirements |
| B1-C | Long-running computation with periodic audit checkpoints |
| B1-D | Computation with frequent rollback requirements |

**Metrics:**
- Wall-clock time (ms) per 10,000 state transitions
- Storage overhead (bytes) per state transition
- History reconstruction latency: time to replay N prior transitions
- Memory overhead during execution

**Success criterion for H1:** BCT overhead ≤ 1.5× baseline overhead on at least one scenario, where the baseline includes equivalent history preservation.

---

## BENCH-H2: Recovery Fidelity

**Hypothesis tested:** H2 — Recovery braids achieve higher fidelity than checkpoint-based approaches.

**Baseline:** PostgreSQL WAL-based recovery; in-memory checkpointing every N transitions

**BCT system:** BCT simulator with recovery instruction family

**Failure scenarios:**

| Scenario | Failure type |
|---|---|
| B2-A | Corruption of single state value mid-computation |
| B2-B | Corruption of authority token |
| B2-C | Loss of last N transitions before checkpoint |
| B2-D | Contradiction between two concurrent execution branches |

**Metrics:**
- Recovery completeness: percentage of execution state successfully restored
- Recovery latency: time from failure detection to resumed execution
- Evidence preservation: percentage of pre-failure evidence retained post-recovery

**Success criterion for H2:** BCT achieves ≥ 95% recovery completeness on scenarios B2-A and B2-D, where checkpoint rollback loses computation since the last checkpoint.

---

## BENCH-H3: Verification Completeness

**Hypothesis tested:** H3 — Structural verification achieves higher completeness than post-hoc verification.

**Baseline:** HMAC-based output verification; TLS for transport verification

**BCT system:** BCT simulator with integrity instruction family

**Test scenarios:**

| Scenario | Description |
|---|---|
| B3-A | Compromised intermediate state producing valid-looking output |
| B3-B | Authority bypass at intermediate execution stage |
| B3-C | State promotion without verification |
| B3-D | Tampered evidence log detection |

**Metrics:**
- Detection rate: percentage of injected violations detected
- False positive rate: percentage of valid computations incorrectly flagged
- Detection latency: crossing index at which violation is detected

**Success criterion for H3:** BCT detects 100% of injected violations in scenarios B3-A through B3-C. Baseline detects ≤ 50% of B3-A (by design — post-hoc verification cannot detect intermediate violations).

---

## BENCH-H4: Authority Bypass Resistance

**Hypothesis tested:** H4 — Authority braids reduce bypass vulnerability.

**Threat model:** An adversary who can:
- Modify in-memory state values
- Inject crossing instructions
- Remove crossing instructions
- Reorder crossing instructions

But cannot: Modify the braid topology structure itself.

**Baseline:** RBAC implementation in Linux kernel (comparable software-layer authority)

**BCT system:** BCT simulator with authority instruction family

**Attack scenarios:**

| Scenario | Attack type |
|---|---|
| B4-A | State promotion without authority crossing |
| B4-B | Authority token duplication attempt |
| B4-C | Routing bypass of authority crossing |
| B4-D | Authority token revocation bypass |

**Metrics:**
- Attack success rate: percentage of injected attacks that succeed (lower is better for BCT)
- Detection rate: percentage of attacks detected and evidence-logged
- False denial rate: percentage of legitimate operations incorrectly blocked

**Success criterion for H4:** BCT attack success rate ≤ 5% across all scenarios under the defined threat model. Baseline attack success rate ≥ 30% for B4-A (software-layer RBAC does not structurally prevent state promotion).

---

## BENCH-H5: ISA Simulation Overhead

**Hypothesis tested:** H5 — Braid ISA can be simulated with acceptable overhead.

**Baseline:** Equivalent computation without BCT crossing overhead

**BCT system:** BCT simulator on x86 and ARM hardware

**Benchmark scenarios:**

| Scenario | Description |
|---|---|
| B5-A | Minimum crossing execution: empty INTEG.VERIFY |
| B5-B | Authority chain: AUTH.CHECK + INTEG.VERIFY + MEM.STORE_HOT |
| B5-C | Full eight-layer execution cycle |
| B5-D | 1,000-crossing braid with all families represented |

**Metrics:**
- Crossings per second (throughput)
- Latency per crossing (ns)
- Memory footprint for N-strand braid
- Evidence log write throughput

**Success criterion for H5:** Full eight-layer cycle (B5-C) executes at ≥ 1,000 cycles/second on commodity hardware with ≤ 3× overhead vs. equivalent unsupported computation.

---

## BENCH-H6: AI Reasoning Explainability

**Hypothesis tested:** H6 — Braid provenance improves AI reasoning explainability.

**Baseline:** Standard LLM with chain-of-thought prompting (no braid provenance)

**BCT system:** LLM with braid provenance layer (Evidence Braid + Verification Braid)

**Benchmark datasets:** TruthfulQA, HotpotQA (multi-hop reasoning), FactScore, custom contradiction detection set

**Metrics:**
- Faithfulness: does the explanation accurately reflect the reasoning? (human evaluation + automated)
- Citation precision: are cited sources actually used in the reasoning?
- Contradiction detection rate: does the system detect and flag self-contradictions?
- Recovery accuracy: when contradictions are detected, does correction improve factual accuracy?

**Success criterion for H6:** BCT provenance layer achieves ≥ 10% improvement on citation precision on HotpotQA and ≥ 10% improvement on contradiction detection rate vs. baseline, with latency overhead ≤ 2×.

---

## Benchmark Infrastructure Requirements

- BCT simulator (Phase 2 deliverable)
- Baseline system implementations (PostgreSQL WAL, Linux RBAC, baseline LLM)
- Automated test harness for all scenarios
- Statistical analysis tooling (significance testing for all metrics)
- Reproducibility documentation: exact versions, hardware specs, random seeds

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
