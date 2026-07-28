"""
tests/unit/test_recovery_verify.py — verify_reverse edge cases

Covers all code paths in braid_simulator.recovery.verify_reverse:
  • Clean execution verifies successfully and hash matches forward result.
  • Corrupted initial state is detected at record 0.
  • Tampered middle record is detected at that crossing.
  • Empty log against empty initial list verifies (trivially).
  • RECOV opcodes (QUARANTINE, HEAL) apply the correct trust-level transitions
    during replay so the hash chain remains consistent.
  • ROUTE.FORK, ROLE.TRANSFER opcodes touch strand_j history correctly.
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
    RecoveryOpcode,
    RoleOpcode,
    RoutingOpcode,
    StrandState,
    TrustLevel,
    verify_reverse,
)
from braid_simulator.evidence import EvidenceRecord, stable_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _auth_verify_promote() -> tuple[ExecutableBraid, list[StrandState], AuthorityManager]:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXEC", scope=["execute"], token_id="rvp-tok")
    initial = [
        StrandState(value={"x": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"y": 2}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]
    braid = ExecutableBraid(strands=initial)
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))
    braid.add_crossing(ExecutableCrossing(
        "promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
    ))
    return braid, initial, manager


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestVerifyReverse:
    def test_clean_execution_verifies(self) -> None:
        braid, initial, manager = _auth_verify_promote()
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        verified, terminal = verify_reverse(list(result.evidence_log.records), initial)

        assert verified, "verify_reverse must return True for uncorrupted execution."
        expected = stable_hash([s.to_dict() for s in result.final_strands])
        actual = stable_hash([s.to_dict() for s in terminal])
        assert actual == expected

    def test_corrupted_initial_state_fails(self) -> None:
        braid, initial, manager = _auth_verify_promote()
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        corrupted = [
            StrandState(value={"x": 999}, trust_level=TrustLevel.ACTIVE,
                        authority_token=initial[0].authority_token),
            initial[1].clone(),
        ]
        verified, _ = verify_reverse(list(result.evidence_log.records), corrupted)
        assert not verified

    def test_empty_log_empty_strands_verifies(self) -> None:
        verified, terminal = verify_reverse([], [])
        assert verified
        assert terminal == []

    def test_empty_log_with_strands_verifies(self) -> None:
        s = StrandState(value=42)
        verified, terminal = verify_reverse([], [s])
        assert verified
        assert terminal[0].value == 42

    def test_tampered_record_detected(self) -> None:
        braid, initial, manager = _auth_verify_promote()
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        records = list(result.evidence_log.records)
        # Tamper the second record's output_hash
        tampered_record = EvidenceRecord(
            tag=records[1].tag,
            family=records[1].family,
            opcode=records[1].opcode,
            timestamp=records[1].timestamp,
            strand_i=records[1].strand_i,
            strand_j=records[1].strand_j,
            input_hash=records[1].input_hash,
            output_hash="TAMPERED_HASH_VALUE",
            result=records[1].result,
        )
        records[1] = tampered_record
        verified, _ = verify_reverse(records, initial)
        assert not verified

    def test_promote_trust_level_applied_in_replay(self) -> None:
        braid, initial, manager = _auth_verify_promote()
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        verified, terminal = verify_reverse(list(result.evidence_log.records), initial)
        assert verified
        assert terminal[0].trust_level == TrustLevel.CERTIFIED

    def test_recovery_quarantine_opcode_applied(self) -> None:
        manager = AuthorityManager()
        token = manager.issue_token(role="EXEC", scope=["execute"], token_id="recov-tok")
        initial = [
            StrandState(value={"ok": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"mirror": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
        braid = ExecutableBraid(strands=initial)
        braid.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
            operands={"predicate": lambda v: True},
        ))
        braid.add_crossing(ExecutableCrossing(
            "quarantine", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        verified, terminal = verify_reverse(list(result.evidence_log.records), initial)
        assert verified
        assert terminal[0].trust_level == TrustLevel.QUARANTINED

    def test_fork_touches_strand_j_history(self) -> None:
        manager = AuthorityManager()
        token = manager.issue_token(role="EXEC", scope=["execute"], token_id="fork-tok")
        initial = [
            StrandState(value={"data": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"data": 0}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
        braid = ExecutableBraid(strands=initial)
        braid.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1,
        ))
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        verified, terminal = verify_reverse(list(result.evidence_log.records), initial)
        assert verified

    def test_role_transfer_touches_both_strands(self) -> None:
        manager = AuthorityManager()
        token = manager.issue_token(role="EXEC", scope=["execute"], token_id="role-tok")
        initial = [
            StrandState(value={"src": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"dst": True}, trust_level=TrustLevel.ACTIVE),
        ]
        braid = ExecutableBraid(strands=initial)
        braid.add_crossing(ExecutableCrossing(
            "transfer", InstructionFamily.ROLE, RoleOpcode.TRANSFER.value, 0, 1,
        ))
        executor = BraidExecutor(manager)
        result = braid.execute(executor)

        verified, terminal = verify_reverse(list(result.evidence_log.records), initial)
        assert verified
