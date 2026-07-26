# Recovery Architecture

> All content is **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Design Philosophy

**[HYPOTHESIS]** BCT recovery is fundamentally different from conventional restart-based recovery.

**Conventional recovery** discards failed state and reconstructs from a prior checkpoint:
```
Failure → Discard current state → Restore checkpoint → Re-execute
```

**BCT recovery** preserves all evidence and repairs the execution in place:
```
Failure → Record failure evidence → Quarantine suspect state → Reroute → Repair → Continue
```

Recovery in BCT is not a correction of a mistake. It is a navigation of a known failure path. Failure becomes knowledge, preserved in the evidence log.

---

## Governing Laws

| Law | Statement |
|---|---|
| 5 | Recovery preserves evidence |
| 6 | Every trusted state has deterministic recovery |
| 7 | History is never discarded |

---

## Failure Classes

**[HYPOTHESIS]** BCT defines four failure classes, each with a defined recovery procedure:

| Class | Description | Recovery |
|---|---|---|
| Verification failure | State failed integrity crossing | Quarantine, reroute to alternate path |
| Authority failure | Strand lacks required authority | Record violation, route to recovery handler |
| State corruption | State is structurally invalid | Restore from nearest verified checkpoint |
| Contradiction | Two trusted states are mutually inconsistent | Quarantine both, initiate contradiction resolution |

---

## Recovery Crossings

**DETECT crossing:** Examines a strand state for anomalies. Produces an anomaly flag and records the detection event. Does not modify the state.

**QUARANTINE crossing:** Moves a suspect state to an isolated region of the braid. The state is preserved (Law 7) but not promoted further. The quarantine is recorded in the evidence log.

**RESTORE crossing:** Retrieves a prior trusted state from the evidence log using its evidence reference. The restored state carries its original verification certificate plus a restoration record.

**HEAL crossing:** Applies a defined repair function to a damaged state. The repair function is a parameter. The healed state undergoes fresh verification before being promoted.

**ARCHIVE crossing:** Moves a failed or quarantined state to cold evidence storage. The state is permanently preserved but removed from active execution.

---

## Recovery Paths

**[HYPOTHESIS]** Every point in a BCT braid has a defined recovery path — an alternate braid route that is traversed when the primary path encounters a failure.

Recovery paths are:
- Defined at braid construction time (not generated at failure time)
- Subject to the same authority and verification requirements as primary paths
- Recorded in the evidence log when traversed

**[HYPOTHESIS H2]** Whether pre-defined recovery paths achieve higher fidelity than checkpoint-based approaches is the subject of Hypothesis H2. See `research/HYPOTHESES.md`.

---

## Contradiction Resolution

**[HYPOTHESIS]** A contradiction occurs when two trusted states in the same braid are mutually inconsistent. This can occur in:
- Distributed execution where two agents produce conflicting verified results
- Long-running computation where an early verification is invalidated by later evidence
- Recovery scenarios where a restored state conflicts with evolved state

Contradiction resolution procedure:
1. Both contradicting states are quarantined
2. Their complete evidence chains are compared
3. A contradiction resolution function is applied (defined by the braid)
4. One state is promoted; the other is archived as evidence of the contradiction
5. The entire resolution process is recorded in the evidence log

---

## Deterministic Recovery

**[HYPOTHESIS]** Law 6 requires that every trusted state have a deterministic recovery path. This means:

- Given the same failure state and the same evidence log, the recovery procedure produces the same result
- Recovery is reproducible
- Recovery can be audited after the fact by replaying the evidence log

---

## Open Problems

1. Formal proof that recovery crossings never discard evidence
2. Definition of contradiction resolution functions for distributed braids
3. Overhead of pre-defined recovery paths vs. on-demand recovery generation
4. Recovery depth: how many recovery levels can be nested before evidence overhead becomes prohibitive?

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
