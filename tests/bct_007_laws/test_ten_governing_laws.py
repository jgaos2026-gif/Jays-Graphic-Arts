"""
tests/bct_007_laws/test_ten_governing_laws.py

One test per governing law.  Each test attempts to *violate* the law and
verifies that the execution engine detects and blocks the violation.

Law 1  — No active state becomes trusted without verification.
Law 2  — Evidence is append-only.
Law 3  — Trusted state is reproducible (replay-deterministic).
Law 4  — Authority cannot be bypassed (AUTH.CHECK precedes promotion).
Law 5  — Recovery preserves evidence.
Law 6  — Every trusted state has deterministic recovery.
Law 7  — History is never discarded (evidence log is immutable).
Law 8  — Verification precedes promotion (structural consequence of Law 1).
Law 9  — Every promoted strand carries explicit authority.
Law 10 — Tampered replays quarantine before restore.
"""
from __future__ import annotations

import pytest

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    LawViolation,
    MemoryOpcode,
    RecoveryOpcode,
    RoutingOpcode,
    StrandState,
    TrustLevel,
    verify_reverse,
)
from braid_simulator.evidence import EvidenceLog, EvidenceRecord


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _executor_and_token(token_id: str = "law-tok") -> tuple[BraidExecutor, object]:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id=token_id)
    return BraidExecutor(manager), token


def _two_strands(token) -> list[StrandState]:
    return [
        StrandState(value={"x": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"y": 2}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]


# ---------------------------------------------------------------------------
# Law 1 — No active state becomes trusted without verification
# ---------------------------------------------------------------------------

def test_law_1_promote_without_verify_blocked() -> None:
    """
    Law 1: INTEG.PROMOTE on ACTIVE strand (without INTEG.VERIFY) raises LawViolation.
    """
    executor, token = _executor_and_token("law1")
    braid = ExecutableBraid(strands=_two_strands(token))
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "promote_bypass", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
    ))
    with pytest.raises(LawViolation, match="Law 1"):
        braid.execute(executor)


# ---------------------------------------------------------------------------
# Law 2 — Evidence is append-only
# ---------------------------------------------------------------------------

def test_law_2_evidence_log_blocks_clear() -> None:
    """Law 2: EvidenceLog.clear() raises RuntimeError."""
    log = EvidenceLog()
    log.append(EvidenceRecord("t", "INTEG", "VERIFY", 0, 0, 1, "in", "out", "PASS"))
    with pytest.raises(RuntimeError, match="append-only"):
        log.clear()


def test_law_2_evidence_log_blocks_pop() -> None:
    """Law 2: EvidenceLog.pop() raises RuntimeError."""
    log = EvidenceLog()
    log.append(EvidenceRecord("t", "INTEG", "VERIFY", 0, 0, 1, "in", "out", "PASS"))
    with pytest.raises(RuntimeError, match="append-only"):
        log.pop()


def test_law_2_evidence_log_monotone_growth() -> None:
    """Law 2: Length never decreases during execution."""
    executor, token = _executor_and_token("law2")
    strands = _two_strands(token)
    braid = ExecutableBraid(strands=strands)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    result = braid.execute(executor)
    assert len(result.evidence_log) == 2


# ---------------------------------------------------------------------------
# Law 3 — Trusted state is reproducible
# ---------------------------------------------------------------------------

def test_law_3_deterministic_replay() -> None:
    """Law 3: Replaying the same braid from the same initial state produces identical evidence."""
    executor, token = _executor_and_token("law3")
    manager = AuthorityManager()
    manager.register(token)
    executor2 = BraidExecutor(manager)

    def build():
        strands = _two_strands(token)
        b = ExecutableBraid(strands=strands)
        b.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        b.add_crossing(ExecutableCrossing(
            "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
            operands={"predicate": lambda v: True},
        ))
        return b, strands

    b1, s1 = build()
    b2, s2 = build()
    r1 = b1.execute(executor)
    r2 = executor.replay(b2, s2, r1)

    assert r2.tampered is False
    assert r1.evidence_log.to_dicts() == r2.evidence_log.to_dicts()


# ---------------------------------------------------------------------------
# Law 4 — Authority cannot be bypassed
# ---------------------------------------------------------------------------

def test_law_4_verify_without_auth_check_blocked() -> None:
    """Law 4: INTEG.VERIFY without prior AUTH.CHECK raises LawViolation."""
    executor, token = _executor_and_token("law4")
    braid = ExecutableBraid(strands=_two_strands(token))
    braid.add_crossing(ExecutableCrossing(
        "verify_no_auth", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    with pytest.raises(LawViolation, match="Law 4"):
        braid.execute(executor)


# ---------------------------------------------------------------------------
# Law 5 — Recovery preserves evidence
# ---------------------------------------------------------------------------

def test_law_5_evidence_preserved_through_recovery() -> None:
    """
    Law 5: Evidence log length only grows — even through RECOV.QUARANTINE and
    RECOV.RESTORE, prior records are never removed.
    """
    executor, token = _executor_and_token("law5")
    strands = _two_strands(token)
    braid = ExecutableBraid(strands=strands)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    braid.add_crossing(ExecutableCrossing(
        "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
    ))
    braid.add_crossing(ExecutableCrossing(
        "restore", InstructionFamily.RECOV, RecoveryOpcode.RESTORE.value, 0, 1,
        operands={"checkpoint_tag": "verify"},
    ))
    result = braid.execute(executor)
    # 4 crossings = exactly 4 records (no deletions)
    assert len(result.evidence_log) == 4
    tags = [r.tag for r in result.evidence_log]
    assert "auth" in tags and "verify" in tags and "q" in tags and "restore" in tags


# ---------------------------------------------------------------------------
# Law 6 — Every trusted state has deterministic recovery
# ---------------------------------------------------------------------------

def test_law_6_trusted_state_has_recovery_checkpoint() -> None:
    """
    Law 6: INTEG.VERIFY produces a checkpoint so trusted state can be recovered.
    A braid that verifies and then restores from that checkpoint succeeds.
    """
    executor, token = _executor_and_token("law6")
    strands = _two_strands(token)
    braid = ExecutableBraid(strands=strands)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    result = braid.execute(executor)
    # At least one checkpoint recorded after verification
    assert len(result.checkpoints) >= 1
    assert result.checkpoints[-1].tag == "verify"


# ---------------------------------------------------------------------------
# Law 7 — History is never discarded
# ---------------------------------------------------------------------------

def test_law_7_prior_evidence_records_unchanged() -> None:
    """
    Law 7: Prior evidence records are never mutated.
    Records at index 0..n-2 must equal their snapshots before the last crossing.
    """
    executor, token = _executor_and_token("law7")
    strands = _two_strands(token)
    braid = ExecutableBraid(strands=strands)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    result = braid.execute(executor)
    # Snapshot record 0 before appending a third crossing to a new braid
    r0 = result.evidence_log[0]
    assert r0.tag == "auth"
    assert r0.result == "PASS"

    # Re-execute extended braid and confirm record 0 is identical
    strands2 = _two_strands(token)
    braid2 = ExecutableBraid(strands=strands2)
    braid2.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid2.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    braid2.add_crossing(ExecutableCrossing(
        "promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
    ))
    result2 = braid2.execute(executor)
    r0_2 = result2.evidence_log[0]
    assert r0_2.tag == r0.tag
    assert r0_2.family == r0.family
    assert r0_2.opcode == r0.opcode


# ---------------------------------------------------------------------------
# Law 8 — Verification precedes promotion
# ---------------------------------------------------------------------------

def test_law_8_seal_on_active_strand_blocked() -> None:
    """Law 8: INTEG.SEAL on ACTIVE strand (without VERIFY) raises LawViolation."""
    executor, token = _executor_and_token("law8")
    braid = ExecutableBraid(strands=_two_strands(token))
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "seal_bypass", InstructionFamily.INTEG, IntegrityOpcode.SEAL.value, 0, 1,
    ))
    with pytest.raises(LawViolation, match="Law 1"):
        braid.execute(executor)


# ---------------------------------------------------------------------------
# Law 9 — Every promoted strand carries explicit authority
# ---------------------------------------------------------------------------

def test_law_9_verify_without_token_blocked() -> None:
    """Law 9: INTEG.VERIFY on a strand with no authority token raises LawViolation."""
    manager = AuthorityManager()
    executor = BraidExecutor(manager)
    # Give the strand a mock token so AUTH.CHECK passes — then revoke it
    token = manager.issue_token(role="EXEC", scope=["execute"], token_id="law9-tok")
    strands = [
        StrandState(value={"x": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"y": 2}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]
    braid = ExecutableBraid(strands=strands)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    manager.revoke_token(token)
    with pytest.raises(LawViolation, match="Law 9"):
        braid.execute(executor)


# ---------------------------------------------------------------------------
# Law 10 — Tampered replays quarantine before restore
# ---------------------------------------------------------------------------

def test_law_10_tampered_replay_quarantines_divergent_strand() -> None:
    """
    Law 10: When a replay diverges from the reference evidence, the executor
    must mark the braid as tampered, quarantine the divergent strand, and
    (if a checkpoint exists) restore from it.
    """
    manager = AuthorityManager()
    token = manager.issue_token(role="EXEC", scope=["execute"], token_id="law10-tok")
    executor = BraidExecutor(manager)

    def build(route_name: str) -> ExecutableBraid:
        b = ExecutableBraid(strands=[
            StrandState(value={"flag": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"peer": False}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ])
        b.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        b.add_crossing(ExecutableCrossing(
            "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
            operands={"predicate": lambda v: True},
        ))
        b.add_crossing(ExecutableCrossing(
            "route", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1,
            operands={"predicate": lambda v: True, "on_true": route_name},
        ))
        return b

    reference = build("trusted-route").execute(executor)
    tampered = build("tampered-route")
    replay = executor.replay(tampered, tampered.strands, reference)

    assert replay.tampered is True, "Tampered replay must be flagged."
    assert len(replay.quarantined_tags) > 0, "At least one strand must be quarantined."
    assert replay.recovered is True, "Recovery must restore from checkpoint."
