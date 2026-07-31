# Version Timeline

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Research Stage Timeline

| Version | Date | Milestone | Status |
|---|---|---|---|
| Concept | 2025 | Initial observation: history preservation gap in conventional architectures | Historical |
| v0.0.1 | 2025 | First executable crossing definition | Historical |
| v0.0.2 | 2025 | First instruction family definitions (Integrity, Recovery) | Historical |
| v0.0.3 | 2026 | Six instruction families defined | Historical |
| v0.0.4 | 2026 | Braid ISA Alpha specification | Historical |
| v0.1.0-alpha | 2026-07-26 | First full repository: simulator, tests, documentation | **Current** |
| v0.2.0 | Planned | Formal semantics (OP-2); Garside/Dehornoy reduction for PO-1 | Phase 1 |
| v0.3.0 | Planned | Simulator Phase 2: persistence, atomic proof core | Phase 2 |
| v1.0.0 | Planned | Stable ISA; formal semantics complete; external review | Phase 4 |

---

## Checkpoint: BRAID ISA Alpha Research Kernel

**Date:** 2026-07-26  
**Status:** Implemented and locally verified

What exists at this checkpoint:
- Six instruction families with 28 opcodes
- Working Python simulator
- Eight-layer execution model
- Append-only evidence log with HMAC validation
- Tamper detection via evidence hash comparison
- Quarantine and checkpoint recovery
- 7 passing tests across 5 test suites
- Complete documentation (manifesto, white paper, thesis, foundations, theory, braid catalog, ISA, AI applications, physics inspiration)

What does not exist at this checkpoint:
- Formal semantics
- Atomic Proof Core
- Independent validation
- Benchmark results

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
