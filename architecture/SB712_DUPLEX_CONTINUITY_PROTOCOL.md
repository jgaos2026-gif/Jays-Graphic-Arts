# SB-712 Duplex Continuity Protocol

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois
**Classification:** Cross-Braid Verification & Transport Specification
**Version:** 0.1.0

> **IMPORTANT SCOPE RULE:** SB-712 is a transport and continuity protocol that operates *between*
> braid families. It does NOT grant automatic maturity levels to BCT braids. Each BCT braid family
> (BCT-001 through BCT-010) must achieve its own dedicated test suite and reproducible evidence
> artifacts independently. Inherited verification from SB-712 is explicitly prohibited.

---

## 1. Purpose

The SB-712 Duplex Continuity Protocol defines how verified state and evidence artifacts are
transported across braid family boundaries within a BCT computation. It ensures that:

1. Evidence records produced by one braid family are accepted as valid inputs by downstream braids.
2. The authority chain is preserved and cryptographically verifiable across boundary crossings.
3. No state crossing a braid boundary can silently lose its evidence lineage.

SB-712 is named for the fundamental duplex property: every forward transport of state is paired
with a reverse transport of its evidence trail. Neither can proceed without the other.

---

## 2. Protocol Boundary Rules

| Rule | Description |
|---|---|
| SB-712-R1 | A state record crossing a braid family boundary MUST carry its complete BCT-008 evidence log segment. |
| SB-712-R2 | The receiving braid MUST validate the evidence log segment against the originating braid's published invariants before accepting the state. |
| SB-712-R3 | Authority tokens MUST remain valid (non-revoked) at the moment of boundary crossing. A revoked token invalidates the entire transport. |
| SB-712-R4 | If the receiving braid cannot validate the incoming evidence segment, it MUST reject the crossing and emit a `DENIED` record to its own BCT-008 log. |
| SB-712-R5 | SB-712 transport does not elevate the maturity level of any braid. Maturity is a property of the braid's own test artifacts, not of its transports. |

---

## 3. Duplex Channel Model

```
  Originating Braid                     Receiving Braid
  ─────────────────                     ───────────────
  [ State Record ]  ──── forward ────►  [ Validation ]
  [ Evidence Log ] ──── forward ────►  [ BCT-008 Check ]
                                                │
  [ Acknowledgement ] ◄─── reverse ───  [ Accept / DENIED ]
  [ Evidence Receipt ] ◄── reverse ───  [ Receipt Token ]
```

The duplex channel guarantees that the originating braid always receives confirmation of whether
its crossing was accepted or denied. Silence (no acknowledgement) is treated as a denial.

---

## 4. Evidence Segment Format

Each SB-712 transport packet carries an evidence segment with the following structure:

```json
{
  "protocol": "SB-712",
  "version": "0.1.0",
  "originating_braid": "BCT-XXX",
  "receiving_braid": "BCT-YYY",
  "transport_id": "<uuid>",
  "timestamp_ns": 0,
  "authority_token_id": "<token-id>",
  "evidence_records": [],
  "segment_hash": "<sha256-of-records>"
}
```

The `segment_hash` is a SHA-256 digest of the canonical JSON serialization of `evidence_records`.
The receiving braid recomputes this hash independently before accepting the segment.

---

## 5. Denied Crossing Protocol

When a receiving braid rejects an SB-712 transport (Rule SB-712-R4), it MUST:

1. Emit a `DENIED` event record to its local BCT-008 log with:
   - `event_type`: `"SB712_BOUNDARY_REJECTION"`
   - `originating_braid`: the source braid ID
   - `reason`: one of `EVIDENCE_INVALID`, `TOKEN_REVOKED`, `HASH_MISMATCH`, `INVARIANT_VIOLATION`
2. Return a `DENIED` receipt to the originating braid via the reverse channel.
3. Quarantine the inbound state record under BCT-003 (Protection) rules.

---

## 6. Relationship to Other BCT Components

| Component | Relationship |
|---|---|
| BCT-008 (Evidence) | SB-712 transports are recorded in the BCT-008 evidence log of both originating and receiving braids. |
| BCT-002 (Authority) | Authority tokens are validated at every SB-712 boundary crossing. |
| BCT-003 (Protection) | Rejected SB-712 crossings trigger BCT-003 quarantine of the inbound state. |
| BCT-005 (Recovery) | SB-712 denial records are part of the BCT-008 trace required by BCT-005 for checkpoint restoration. |
| T-800 OMEGA72 | T-800 OMEGA72 is a proposed guardian hypothesis (see `research/GUARDIAN_MODEL.md`) and is NOT part of the SB-712 specification. |

---

## 7. Open Specification Items

The following aspects of SB-712 require further formalization before the protocol can advance to
a reference implementation:

- [ ] Formal definition of the canonical evidence segment serialization format.
- [ ] Specification of timeout semantics for the reverse acknowledgement channel.
- [ ] Integration with BCT-009 (Consensus) for multi-node boundary crossings.
- [ ] Formal proof that the duplex property cannot be broken by a misbehaving originating braid.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
*Braided Computational Topology — SB-712 Protocol v0.1.0, 2026*
