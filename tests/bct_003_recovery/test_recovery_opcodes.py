"""
tests/bct_003_recovery/test_recovery_opcodes.py — RECOV Family Test Suite

Tests every RECOV opcode:  DETECT, QUARANTINE, RESTORE, HEAL, ARCHIVE.

These tests verify that:
  • RECOV.DETECT correctly identifies anomalies via detector callables and
    expected-hash matching.
  • RECOV.QUARANTINE transitions a strand to QUARANTINED and records it.
  • RECOV.RESTORE reinstates strands from the last trusted checkpoint.
  • RECOV.HEAL resets trust level to ACTIVE and applies repair functions.
  • RECOV.ARCHIVE moves state to cold storage (quarantines the live strand).
  • Evidence is appended for every crossing (Law 2, Law 5).
  • Recovery never discards prior evidence records (Law 7).
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
    RecoveryOpcode,
    StrandState,
    TrustLevel,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make(n: int = 2) -> tuple[BraidExecutor, list[StrandState]]:
    manager = AuthorityManager()
    token = manager.issue_token(role="RECOV", scope=["execute"], token_id="recov-base-tok")
    executor = BraidExecutor(manager)
    strands = [
        StrandState(value={"v": i}, trust_level=TrustLevel.ACTIVE, authority_token=token)
        for i in range(n)
    ]
    return executor, strands


def _build_verified_braid(strands: list[StrandState], executor: BraidExecutor) -> ExecutableBraid:
    """Return a braid that takes strand 0 to TRUSTED and records a checkpoint."""
    braid = ExecutableBraid(strands=strands)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    return braid


# ---------------------------------------------------------------------------
# RECOV.DETECT
# ---------------------------------------------------------------------------

class TestRecovDetect:
    def test_detect_no_anomaly_returns_pass(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
            operands={"detector": lambda v: False},  # no anomaly
        ))
        result = braid.execute(executor)
        detect_record = next(r for r in result.evidence_log if r.tag == "detect")
        assert detect_record.result == "PASS"

    def test_detect_anomaly_returns_fail(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
            operands={"detector": lambda v: True},  # always anomaly
        ))
        result = braid.execute(executor)
        detect_record = next(r for r in result.evidence_log if r.tag == "detect")
        assert detect_record.result == "FAIL"

    def test_detect_via_expected_hash(self) -> None:
        executor, strands = _make()
        from braid_simulator.evidence import stable_hash
        correct_hash = stable_hash(strands[0].value)
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
            operands={"expected_hash": correct_hash},
        ))
        result = braid.execute(executor)
        detect_record = next(r for r in result.evidence_log if r.tag == "detect")
        assert detect_record.result == "PASS"

    def test_detect_hash_mismatch_returns_fail(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
            operands={"expected_hash": "WRONG_HASH"},
        ))
        result = braid.execute(executor)
        detect_record = next(r for r in result.evidence_log if r.tag == "detect")
        assert detect_record.result == "FAIL"

    def test_detect_appends_evidence(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        n_before = 2
        braid.add_crossing(ExecutableCrossing(
            "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
            operands={"detector": lambda v: False},
        ))
        result = braid.execute(executor)
        assert len(result.evidence_log) == n_before + 1


# ---------------------------------------------------------------------------
# RECOV.QUARANTINE
# ---------------------------------------------------------------------------

class TestRecovQuarantine:
    def test_quarantine_sets_trust_level(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].trust_level == TrustLevel.QUARANTINED

    def test_quarantine_tag_recorded(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert "q" in result.quarantined_tags

    def test_quarantine_does_not_affect_other_strand(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[1].trust_level == TrustLevel.ACTIVE

    def test_quarantine_result_is_quarantined(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        result = braid.execute(executor)
        q_record = next(r for r in result.evidence_log if r.tag == "q")
        assert q_record.result == "QUARANTINED"


# ---------------------------------------------------------------------------
# RECOV.RESTORE
# ---------------------------------------------------------------------------

class TestRecovRestore:
    def test_restore_returns_to_trusted_checkpoint(self) -> None:
        executor, strands = _make()
        # Build: auth → verify (creates checkpoint "verify") → quarantine → restore
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
        restore_record = next(r for r in result.evidence_log if r.tag == "restore")
        assert restore_record.result == "PASS"

    def test_restore_without_checkpoint_raises(self) -> None:
        manager = AuthorityManager()
        executor = BraidExecutor(manager)
        strands = [StrandState(value=None), StrandState(value=None)]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "restore", InstructionFamily.RECOV, RecoveryOpcode.RESTORE.value, 0, 1,
        ))
        with pytest.raises(LawViolation):
            braid.execute(executor)

    def test_restore_appends_evidence(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "restore", InstructionFamily.RECOV, RecoveryOpcode.RESTORE.value, 0, 1,
            operands={"checkpoint_tag": "verify"},
        ))
        result = braid.execute(executor)
        tags = [r.tag for r in result.evidence_log]
        assert "restore" in tags


# ---------------------------------------------------------------------------
# RECOV.HEAL
# ---------------------------------------------------------------------------

class TestRecovHeal:
    def test_heal_resets_trust_to_active(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "heal", InstructionFamily.RECOV, RecoveryOpcode.HEAL.value, 0, 1,
            operands={"replacement": {"v": 0, "healed": True}},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].trust_level == TrustLevel.ACTIVE

    def test_heal_applies_repair_function(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "heal", InstructionFamily.RECOV, RecoveryOpcode.HEAL.value, 0, 1,
            operands={"repair_fn": lambda v: {"repaired": True}},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value == {"repaired": True}

    def test_heal_applies_replacement(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "heal", InstructionFamily.RECOV, RecoveryOpcode.HEAL.value, 0, 1,
            operands={"replacement": {"fixed": True}},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value == {"fixed": True}


# ---------------------------------------------------------------------------
# RECOV.ARCHIVE
# ---------------------------------------------------------------------------

class TestRecovArchive:
    def test_archive_quarantines_live_strand(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "archive", InstructionFamily.RECOV, RecoveryOpcode.ARCHIVE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].trust_level == TrustLevel.QUARANTINED

    def test_archive_result_is_quarantined(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "archive", InstructionFamily.RECOV, RecoveryOpcode.ARCHIVE.value, 0, 1,
        ))
        result = braid.execute(executor)
        archive_record = next(r for r in result.evidence_log if r.tag == "archive")
        assert archive_record.result == "QUARANTINED"

    def test_archive_appends_evidence(self) -> None:
        executor, strands = _make()
        braid = _build_verified_braid(strands, executor)
        braid.add_crossing(ExecutableCrossing(
            "archive", InstructionFamily.RECOV, RecoveryOpcode.ARCHIVE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert any(r.tag == "archive" for r in result.evidence_log)
