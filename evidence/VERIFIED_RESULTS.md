# Verified Results

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Status:** Results are locally verified unless labeled INDEPENDENTLY REPRODUCED.

---

## v0.1.0-alpha Results

### Test Suite: 7/7 Passing

| Test | File | Status |
|---|---|---|
| Evidence log is append-only | `tests/unit/test_evidence.py` | ✅ PASS |
| Crossing execution promotes state | `tests/unit/test_crossing.py` | ✅ PASS |
| Authority token issue/delegate/revoke | `tests/unit/test_authority.py` | ✅ PASS |
| Braid composition records evidence | `tests/unit/test_braid.py` | ✅ PASS |
| Evidence log length monotonically increases | `tests/property/test_invariants.py` | ✅ PASS |
| Tampered replay is detected and quarantined | `tests/adversarial/test_tamper.py` | ✅ PASS |
| Replay is deterministic | `tests/replay/test_replay.py` | ✅ PASS |

### Demo: integrity_demo Proof Report

Run `python -m braid_simulator examples/integrity_demo` to reproduce.

Output: JSON proof report containing:
- Execution summary
- Evidence log hash
- Tamper detection result
- Recovery result
- Final trust state

---

## Pending Results

| Benchmark | Status | Expected Phase |
|---|---|---|
| BENCH-H1 (history overhead) | Pending simulator Phase 2 | Phase 3 |
| BENCH-H2 (recovery fidelity) | Pending | Phase 3 |
| BENCH-H3 (verification completeness) | Pending | Phase 3 |
| BENCH-H4 (authority bypass resistance) | Pending | Phase 3 |
| BENCH-H5 (ISA overhead) | Pending | Phase 3 |
| BENCH-H6 (AI explainability) | Pending | Phase 5 |

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
