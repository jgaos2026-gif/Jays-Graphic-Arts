"""
tests/bct_005_role/test_role_exchange.py — ROLE Family Test Suite

Tests every ROLE opcode: TRANSFER, DELEGATE, REVOKE, VERIFY_ROLE.
"""
from __future__ import annotations

import pytest

from braid_simulator import (
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    LawViolation,
    RoleOpcode,
    StrandState,
    TrustLevel,
)


def _make() -> tuple[BraidExecutor, AuthorityManager, object]:
    manager = AuthorityManager()
    token = manager.issue_token(role="ADMIN", scope=["execute", "store"], token_id="role-admin")
    executor = BraidExecutor(manager)
    return executor, manager, token


# ---------------------------------------------------------------------------
# ROLE.TRANSFER
# ---------------------------------------------------------------------------

class TestRoleTransfer:
    def test_transfer_moves_token_to_target(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value={"src": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"dst": True}, trust_level=TrustLevel.ACTIVE),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "transfer", InstructionFamily.ROLE, RoleOpcode.TRANSFER.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].authority_token is None
        assert result.final_strands[1].authority_token is not None
        assert result.final_strands[1].authority_token.id == token.id

    def test_transfer_appends_evidence(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "transfer", InstructionFamily.ROLE, RoleOpcode.TRANSFER.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert any(r.tag == "transfer" for r in result.evidence_log)

    def test_transfer_result_is_pass(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "transfer", InstructionFamily.ROLE, RoleOpcode.TRANSFER.value, 0, 1,
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "transfer")
        assert record.result == "PASS"

    def test_transfer_touches_both_histories(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "transfer", InstructionFamily.ROLE, RoleOpcode.TRANSFER.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert "transfer" in result.final_strands[0].history
        assert "transfer" in result.final_strands[1].history


# ---------------------------------------------------------------------------
# ROLE.DELEGATE
# ---------------------------------------------------------------------------

class TestRoleDelegate:
    def test_delegate_creates_scoped_child_token(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "delegate", InstructionFamily.ROLE, RoleOpcode.DELEGATE.value, 0, 1,
            operands={"scope": ["execute"], "role": "WORKER"},
        ))
        result = braid.execute(executor)
        child_token = result.final_strands[1].authority_token
        assert child_token is not None
        assert "execute" in child_token.scope
        assert "store" not in child_token.scope

    def test_delegate_without_token_raises(self) -> None:
        executor, manager, _ = _make()
        strands = [
            StrandState(value=None),  # no token
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "delegate", InstructionFamily.ROLE, RoleOpcode.DELEGATE.value, 0, 1,
            operands={"scope": ["execute"]},
        ))
        with pytest.raises(LawViolation):
            braid.execute(executor)

    def test_delegate_to_target_i_with_target_operand(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "delegate", InstructionFamily.ROLE, RoleOpcode.DELEGATE.value, 0, 1,
            operands={"scope": ["execute"], "target": "i"},
        ))
        result = braid.execute(executor)
        # When target="i", the delegation goes back to strand i
        assert result.final_strands[0].authority_token is not None

    def test_delegate_appends_evidence(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "delegate", InstructionFamily.ROLE, RoleOpcode.DELEGATE.value, 0, 1,
            operands={"scope": ["execute"]},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "delegate" for r in result.evidence_log)


# ---------------------------------------------------------------------------
# ROLE.REVOKE
# ---------------------------------------------------------------------------

class TestRoleRevoke:
    def test_revoke_marks_token_as_revoked(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "revoke", InstructionFamily.ROLE, RoleOpcode.REVOKE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].authority_token is not None
        assert result.final_strands[0].authority_token.revoked is True

    def test_revoke_without_token_raises(self) -> None:
        executor, manager, _ = _make()
        strands = [
            StrandState(value=None),  # no token
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "revoke", InstructionFamily.ROLE, RoleOpcode.REVOKE.value, 0, 1,
        ))
        with pytest.raises(LawViolation):
            braid.execute(executor)

    def test_revoke_appends_evidence(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "revoke", InstructionFamily.ROLE, RoleOpcode.REVOKE.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert any(r.tag == "revoke" for r in result.evidence_log)


# ---------------------------------------------------------------------------
# ROLE.VERIFY_ROLE
# ---------------------------------------------------------------------------

class TestRoleVerifyRole:
    def test_verify_role_passes_for_correct_role(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "check_role", InstructionFamily.ROLE, RoleOpcode.VERIFY_ROLE.value, 0, 1,
            operands={"role": "ADMIN"},
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "check_role")
        assert record.result == "PASS"

    def test_verify_role_fails_for_wrong_role(self) -> None:
        executor, manager, token = _make()
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "check_role", InstructionFamily.ROLE, RoleOpcode.VERIFY_ROLE.value, 0, 1,
            operands={"role": "WRONG_ROLE"},
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "check_role")
        assert record.result == "FAIL"

    def test_verify_role_fails_without_token(self) -> None:
        executor, manager, _ = _make()
        strands = [
            StrandState(value=None),  # no token
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "check_role", InstructionFamily.ROLE, RoleOpcode.VERIFY_ROLE.value, 0, 1,
            operands={"role": "ADMIN"},
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "check_role")
        assert record.result == "FAIL"

    def test_verify_role_fails_for_revoked_token(self) -> None:
        executor, manager, token = _make()
        manager.revoke_token(token)
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "check_role", InstructionFamily.ROLE, RoleOpcode.VERIFY_ROLE.value, 0, 1,
            operands={"role": "ADMIN"},
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "check_role")
        assert record.result == "FAIL"
