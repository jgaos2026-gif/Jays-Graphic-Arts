# BFR Registry: Braid Family Registry Canonical Standard

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois
**Version:** 0.1.0 Canonical
**Supersedes:** All previous maturity assignments

> **STRICT AUDIT RULE:** Maturity levels are awarded ONLY to named BCT software artifacts that execute
> dedicated test suites and generate reproducible evidence logs. Inheritance of test validity from
> ancestor protocols (such as SB-712) is explicitly prohibited.

---

## Maturity Level Definitions

| Level | Name | Criteria |
|---|---|---|
| **LEVEL 0** | Concept | Theoretical motivation and hypothesis formulated. |
| **LEVEL 1** | Formal Definition | Braid Constitution complete; crossings and invariants mathematically specified. |
| **LEVEL 2** | Executable Prototype | Minimal implementation running in research kernel simulator. |
| **LEVEL 3** | Locally Verified | Passes dedicated unit, property, adversarial, and fault tests with a reproducible command and machine-readable result artifact tied to the tested commit. |
| **LEVEL 4** | Independently Reproduced | Verified and benchmarked by an external laboratory. |
| **LEVEL 5** | Production Validated | Operating in production environments under live workloads. |

> **Level 3 Gate:** No braid advances to Level 3 without a dedicated test suite, a reproducible
> execution command, and an immutable proof artifact generated at runtime.

---

## Auditable Baseline Matrix (v0.1.0 Canonical)

| BFR ID | Braid Family | Canonical Question | Current Level | Level Justification & Blocking Dependency |
|---|---|---|---|---|
| BCT-008 | Evidence | "What is the complete chain of proof?" | Level 2 | Executable in kernel. Blocker for Level 3: Must record denied security events/rejections in append-only log. |
| BCT-002 | Authority | "Who is allowed to do this?" | Level 1 | Formally defined. Blocker for Level 2/3: HMAC-SHA256 token lifecycle & capability delegation repair. |
| BCT-001 | Integrity | "Is this state still true?" | Level 2 | Executable in kernel. Blocker for Level 3: Dedicated adversarial suite for non-commutative crossing checks. |
| BCT-010 | Execution | "What work is actually being performed?" | Level 2 | Executable worker strand. Blocker for Level 3: Isolated execution harness with BCT-008 trace emission. |
| BCT-004 | Routing | "Where does this instruction go?" | Level 2 | Executable dispatch logic. Blocker for Level 3: Topological instruction routing fuzzing harness. |
| BCT-006 | Role Exchange | "How are permissions safely handed off?" | Level 1 | Formally defined. Blocker for Level 2: Execution harness tied to HMAC capability promotion/revocation. |
| BCT-003 | Protection | "How do we isolate this failure?" | Level 1 | Formally defined. Blocker for Level 2: Bounded neighborhood quarantine implementation. |
| BCT-005 | Recovery | "How do we restore a valid checkpoint?" | Level 1 | Formally defined. Blocker for Level 2: Ingestion of complete BCT-008 evidence trace (including denied actions). |
| BCT-007 | Memory | "Where does this state live over time?" | Level 0 | Pure hypothesis. Blocker for Level 1: Mathematical formalization of memory topology & hot/cold rotation. |
| BCT-009 | Consensus | "How do independent nodes reconcile?" | Level 0 | Pure hypothesis. Blocker for Level 1: Formalization of multi-agent disagreement-preserving state models. |

---

## Promotion Path Dependency Order

```
[BCT-008: Evidence] ──► [BCT-002: Authority] ──► [BCT-001: Integrity] ──► [BCT-010: Execution]
        │
[BCT-005: Recovery] ◄── [BCT-003: Protection] ◄── [BCT-006: Role Exchange] ◄───┘
```

BCT-008 (Evidence) must reach Level 3 before any downstream braid can claim Level 3. BCT-002
(Authority) is the second dependency in the chain because authenticated capability tokens are
required before integrity and execution braids can generate auditable proof artifacts.

---

## Canonical Status Summary

- **10** Canonical Active Braid Families registered.
- **4** Executable at Level 2: BCT-001, BCT-004, BCT-008, BCT-010.
- **4** Formally Defined at Level 1: BCT-002, BCT-003, BCT-005, BCT-006.
- **2** Conceptual at Level 0: BCT-007, BCT-009.
- **SB-712** positioned as the cross-braid Duplex Continuity Protocol (see `architecture/SB712_DUPLEX_CONTINUITY_PROTOCOL.md`). Does NOT grant automatic maturity to BCT braids.
- **T-800 OMEGA72** cordoned off in `research/GUARDIAN_MODEL.md` as a proposed hypothesis pending three independent verification requirements.

---

## Related Documents

| Document | Role |
|---|---|
| `braid_catalog/TEMPLATE.md` | Uniform engineering contract template for each braid family. |
| `architecture/SB712_DUPLEX_CONTINUITY_PROTOCOL.md` | Cross-braid verification and transport specification. |
| `research/GUARDIAN_MODEL.md` | T-800 OMEGA72 Guardian Runtime hypothesis and open governance blockers. |
| `research/HYPOTHESES.md` | Empirical hypotheses requiring experimental falsification. |
| `theory/PROOF_OBLIGATIONS.md` | Formal proof obligations across all braid families. |
| `tests/bct_008_evidence/` | BCT-008 Level 3 gate test suite. |
| `tests/bct_002_authority/` | BCT-002 HMAC capability token test suite. |
| `tests/bct_001_integrity/` | BCT-001 non-commutative crossing adversarial suite. |

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
*Braided Computational Topology — BFR Registry v0.1.0, 2026*
