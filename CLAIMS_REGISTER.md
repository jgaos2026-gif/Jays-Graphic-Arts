# Claims Register

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  

> This file is the authoritative record of every claim made in this repository.  
> It prevents architecture, implementation, tests, and future vision from being mixed together.  
> Every claim has a classification, evidence pointer, and status.  
> **No claim may be promoted to a higher status without documented evidence.**

---

## Classification Definitions

| Classification | Meaning |
|---|---|
| **ESTABLISHED** | Prior mathematics or computer science; independently verified by prior literature; cited |
| **IMPLEMENTED** | Code exists in this repository performing the described function |
| **LOCALLY VERIFIED** | Implemented and passing tests in this repository; not yet independently reproduced |
| **INDEPENDENTLY REPRODUCED** | Confirmed by parties unaffiliated with this project |
| **HYPOTHESIS** | Testable proposition; no current empirical or formal support |
| **SPECULATIVE** | Conceptual direction; not yet a testable proposition |
| **FUTURE WORK** | Planned but not started; no claim of current existence |

---

## Register

| ID | Claim | Classification | Evidence | Status |
|---|---|---|---|---|
| **BCT-001** | Braid groups are a well-defined algebraic structure (Artin, 1925) | ESTABLISHED | `foundations/ARTIN_BRAID_GROUPS.md`, Artin 1925 | ✅ Established |
| **BCT-002** | Braid groups are non-abelian for n ≥ 3 | ESTABLISHED | `foundations/ARTIN_BRAID_GROUPS.md` | ✅ Established |
| **BCT-003** | The word problem for Bₙ is decidable | ESTABLISHED | `foundations/ARTIN_BRAID_GROUPS.md`, Garside 1969 | ✅ Established |
| **BCT-004** | Topological quantum computing uses braid operations (Kitaev, 2003) | ESTABLISHED | `foundations/TOPOLOGICAL_QUANTUM_COMPUTING.md` | ✅ Established |
| **BCT-005** | Executable braid crossings carry and execute computational instructions | IMPLEMENTED | `braid_simulator/crossing.py`, `braid_simulator/instructions.py` | 🔬 Locally Verified |
| **BCT-006** | Evidence log is append-only; no crossing may delete records | IMPLEMENTED | `braid_simulator/evidence.py`, `tests/unit/test_evidence.py` | 🔬 Locally Verified |
| **BCT-007** | Active state cannot become trusted without INTEG.VERIFY crossing | IMPLEMENTED | `braid_simulator/execution.py`, `tests/adversarial/test_tamper.py` | 🔬 Locally Verified |
| **BCT-008** | Authority cannot be bypassed (AUTH.CHECK precedes promotion) | IMPLEMENTED | `braid_simulator/authority.py`, `tests/adversarial/test_tamper.py` | 🔬 Locally Verified |
| **BCT-009** | Tampered execution is detected by evidence hash divergence on replay | IMPLEMENTED | `braid_simulator/execution.py`, `tests/replay/test_replay.py` | 🔬 Locally Verified |
| **BCT-010** | Recovery restores to last trusted checkpoint without discarding evidence | IMPLEMENTED | `braid_simulator/execution.py`, `tests/unit/test_braid.py` | 🔬 Locally Verified |
| **BCT-011** | Six instruction families cover integrity, routing, recovery, role exchange, authority, memory | IMPLEMENTED | `braid_simulator/instructions.py`, `isa/INSTRUCTION_FAMILIES.md` | 🔬 Locally Verified |
| **BCT-012** | Braid architectures reduce overhead for history-preserving computation (H1) | HYPOTHESIS | `research/HYPOTHESES.md` — H1; `benchmarks/BENCHMARK_PROTOCOL.md` | ❓ Unproven |
| **BCT-013** | Recovery braids achieve higher fidelity than checkpoint-based approaches (H2) | HYPOTHESIS | `research/HYPOTHESES.md` — H2 | ❓ Unproven |
| **BCT-014** | Structural verification achieves higher completeness than post-hoc verification (H3) | HYPOTHESIS | `research/HYPOTHESES.md` — H3 | ❓ Unproven |
| **BCT-015** | Authority braids reduce bypass vulnerability vs. software-layer enforcement (H4) | HYPOTHESIS | `research/HYPOTHESES.md` — H4 | ❓ Unproven |
| **BCT-016** | Braid ISA can be simulated with acceptable overhead on commodity hardware (H5) | HYPOTHESIS | `research/HYPOTHESES.md` — H5 | ❓ Unproven |
| **BCT-017** | Braid provenance improves AI reasoning explainability (H6) | HYPOTHESIS | `research/HYPOTHESES.md` — H6 | ❓ Unproven |
| **BCT-018** | Executable braid model is Turing-complete (Conjecture C1) | HYPOTHESIS | `research/OPEN_PROBLEMS.md` — OP-1 | ❓ Open conjecture |
| **BCT-019** | Braid invariants classify computational equivalence classes (Conjecture C2) | HYPOTHESIS | `research/OPEN_PROBLEMS.md` — OP-3 | ❓ Open conjecture |
| **BCT-020** | Braided AI architecture improves reasoning provenance | SPECULATIVE | `ai/BRAIDED_AI_ARCHITECTURE.md` | 💭 Speculative |
| **BCT-021** | Consensus braid preserves disagreement history in distributed agreement | SPECULATIVE | `braid_catalog/CONSENSUS_BRAID.md` | 💭 Speculative |
| **BCT-022** | Learning braid can express model adaptation as executable crossings | FUTURE WORK | `braid_catalog/LEARNING_BRAID.md` | 🔭 Future Work |
| **BCT-023** | Compression braid reduces braid size while preserving semantics | FUTURE WORK | `braid_catalog/COMPRESSION_BRAID.md` | 🔭 Future Work |
| **BCT-024** | BCT architectures are suitable for production deployment | **NOT CLAIMED** | — | ⛔ Not a claim of this project |
| **BCT-025** | BCT replaces conventional computing architectures | **NOT CLAIMED** | — | ⛔ Not a claim of this project |

---

## How to Update This Register

When code is written and tested:
1. Change classification from HYPOTHESIS → IMPLEMENTED
2. Add evidence pointer (file path + test name)
3. Change status to 🔬 Locally Verified

When independently reproduced:
1. Change classification to INDEPENDENTLY REPRODUCED
2. Add external citation or reproduction report in `evidence/`

When a hypothesis is falsified:
1. Change classification to `FALSIFIED`
2. Document the falsification evidence
3. Update the relevant hypothesis file

**Falsification is a valid and important research outcome.**

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
