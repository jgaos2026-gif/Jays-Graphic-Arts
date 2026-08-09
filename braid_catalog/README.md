# Braid Catalog

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  

> Every braid family uses the same template.  
> A template applied consistently turns concepts into a science, not a stack of powerful names.

---

## Standard Template

Each braid family document uses this structure:

```
# [Braid Name]
## Purpose
## Intended Computational Role
## Strand Types
## Crossing Semantics
## Direction of Information Flow
## Allowed Transformations
## Invariants
## Failure Modes
## Recovery Behavior
## Authority Requirements
## Evidence Produced
## Complexity
## Current Implementation Status
## Test Coverage
## Known Limitations
## Comparison Baseline
```

---

## Braid Families

### Tier 1 — Trust and Correctness
| Family | Purpose | Status |
|---|---|---|
| [Integrity Braid](INTEGRITY_BRAID.md) | Verify state; preserve evidence | ✅ Implemented |
| [Verification Braid](VERIFICATION_BRAID.md) | Challenge claims against independent evidence | 🔬 Defined |
| [Authority Braid](AUTHORITY_BRAID.md) | Enforce structural permissions | ✅ Implemented |
| [Provenance Braid](PROVENANCE_BRAID.md) | Track origin and transformation of every value | 🔬 Defined |

### Tier 2 — Execution and Navigation
| Family | Purpose | Status |
|---|---|---|
| [Routing Braid](ROUTING_BRAID.md) | Select execution paths with authority | ✅ Implemented |
| [Scheduling Braid](SCHEDULING_BRAID.md) | Coordinate interleaved work with ordering | 🔬 Defined |
| [Communication Braid](COMMUNICATION_BRAID.md) | Move messages with delivery proof | 🔬 Defined |

### Tier 3 — Resilience
| Family | Purpose | Status |
|---|---|---|
| [Recovery Braid](RECOVERY_BRAID.md) | Repair execution while preserving evidence | ✅ Implemented |
| [Role Exchange Braid](ROLE_EXCHANGE_BRAID.md) | Transfer authority atomically | ✅ Implemented |

### Tier 4 — State Management
| Family | Purpose | Status |
|---|---|---|
| [Memory Braid](MEMORY_BRAID.md) | Coordinate hot/warm/cold state | ✅ Implemented |
| [Compression Braid](COMPRESSION_BRAID.md) | Reduce size while preserving provenance | 🔭 Future Work |

### Tier 5 — Future Families
| Family | Purpose | Status |
|---|---|---|
| [Consensus Braid](CONSENSUS_BRAID.md) | Distributed agreement with disagreement history | 💭 Speculative |
| [Learning Braid](LEARNING_BRAID.md) | Verified model adaptation | 💭 Speculative |
| [Simulation Braid](SIMULATION_BRAID.md) | Branching possible worlds | 💭 Speculative |

---

## Status Key

| Symbol | Meaning |
|---|---|
| ✅ Implemented | Code exists and tests pass (`CLAIMS_REGISTER.md` — LOCALLY VERIFIED) |
| 🔬 Defined | Formal definition written; not yet implemented |
| 🔭 Future Work | Concept described; formal definition pending |
| 💭 Speculative | Direction identified; no formal definition |
