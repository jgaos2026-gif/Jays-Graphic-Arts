"""
tests/integration/test_pipeline.py — End-to-End Integration Tests

Full multi-family braid pipelines exercising interactions between families.
"""
from __future__ import annotations

import pytest

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    BraidSession,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    LawViolation,
    MemoryOpcode,
    PersistentEvidenceStore,
    RecoveryOpcode,
    RoleOpcode,
    RoutingOpcode,
    StrandState,
    TrustLevel,
    verify_reverse,
)
from braid_simulator.evidence import stable_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _executor(token_id: str = "integ-tok") -> tuple[BraidExecutor, AuthorityManager, object]:
    manager = AuthorityManager()
    token = manager.issue_token(
        role="EXECUTOR",
        scope=["execute", "store", "verify"],
        token_id=token_id,
    )
    return BraidExecutor(manager), manager, token


# ---------------------------------------------------------------------------
# 1. Auth → Verify → Promote → Store → Load pipeline
# ---------------------------------------------------------------------------

class TestAuthVerifyPromoteStorePipeline:
    def test_full_pipeline_reaches_certified(self) -> None:
        executor, manager, token = _executor("pipe1")
        strands = [
            StrandState(value={"counter": 1}, authority_token=token),
            StrandState(value={"mirror": True}, authority_token=token),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
            operands={"predicate": lambda v: v["counter"] == 1},
        ))
        braid.add_crossing(ExecutableCrossing(
            "promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "payload"},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].trust_level == TrustLevel.CERTIFIED
        assert len(result.evidence_log) == 4
        assert len(result.checkpoints) >= 2  # verify + promote each create checkpoints

    def test_full_pipeline_verify_reverse_confirms(self) -> None:
        executor, manager, token = _executor("pipe1b")
        initial = [
            StrandState(value={"data": "abc"}, authority_token=token),
            StrandState(value={"flag": False}, authority_token=token),
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
        result = braid.execute(executor)
        verified, terminal = verify_reverse(list(result.evidence_log.records), initial)
        assert verified
        assert stable_hash([s.to_dict() for s in terminal]) == \
               stable_hash([s.to_dict() for s in result.final_strands])


# ---------------------------------------------------------------------------
# 2. Auth → Verify → Role.Transfer → Auth.Check on new holder
# ---------------------------------------------------------------------------

class TestAuthorityTransferPipeline:
    def test_role_transfer_and_re_auth(self) -> None:
        executor, manager, token = _executor("pipe2")
        child_token = manager.issue_token(
            role="CHILD", scope=["execute"], token_id="child-pipe2"
        )
        strands = [
            StrandState(value={"holder": "source"}, authority_token=token),
            StrandState(value={"holder": "target"}, authority_token=child_token),
        ]
        braid = ExecutableBraid(strands=strands)
        # Auth + verify source
        braid.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
            operands={"predicate": lambda v: True},
        ))
        # Transfer authority from strand 0 to strand 1
        braid.add_crossing(ExecutableCrossing(
            "transfer", InstructionFamily.ROLE, RoleOpcode.TRANSFER.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].authority_token is None
        assert result.final_strands[1].authority_token is not None
        assert result.final_strands[1].authority_token.id == token.id


# ---------------------------------------------------------------------------
# 3. Detect → Quarantine → Restore recovery pipeline
# ---------------------------------------------------------------------------

class TestRecoveryPipeline:
    def test_quarantine_and_restore_preserves_evidence(self) -> None:
        executor, manager, token = _executor("pipe3")
        strands = [
            StrandState(value={"status": "ok"}, authority_token=token),
            StrandState(value={"monitor": True}, authority_token=token),
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
        braid.add_crossing(ExecutableCrossing(
            "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
            operands={"detector": lambda v: v.get("status") != "ok"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "restore", InstructionFamily.RECOV, RecoveryOpcode.RESTORE.value, 0, 1,
            operands={"checkpoint_tag": "verify"},
        ))
        result = braid.execute(executor)
        # 5 crossings → 5 evidence records
        assert len(result.evidence_log) == 5
        # Evidence preserved throughout
        assert all(r.tag in ["auth", "verify", "detect", "q", "restore"]
                   for r in result.evidence_log)

    def test_heal_after_quarantine_resets_to_active(self) -> None:
        executor, manager, token = _executor("pipe3b")
        strands = [
            StrandState(value={"broken": True}, authority_token=token),
            StrandState(value={"ok": True}, authority_token=token),
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
        braid.add_crossing(ExecutableCrossing(
            "q", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "heal", InstructionFamily.RECOV, RecoveryOpcode.HEAL.value, 0, 1,
            operands={"replacement": {"broken": False, "healed": True}},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].trust_level == TrustLevel.ACTIVE
        assert result.final_strands[0].value["healed"] is True


# ---------------------------------------------------------------------------
# 4. Fork → process → Join merge pipeline
# ---------------------------------------------------------------------------

class TestForkJoinPipeline:
    def test_fork_then_join_merges_strands(self) -> None:
        executor, manager, token = _executor("pipe4")
        strands = [
            StrandState(value={"stream": "A"}, authority_token=token),
            StrandState(value={"stream": "B"}, authority_token=token),
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
        braid.add_crossing(ExecutableCrossing(
            "fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "join", InstructionFamily.ROUTE, RoutingOpcode.JOIN.value, 0, 1,
            operands={"merge_fn": lambda a, b: {"merged": True, "streams": [a.get("stream"), b.get("stream")]}},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value["merged"] is True
        assert len(result.evidence_log) == 4


# ---------------------------------------------------------------------------
# 5. SQLite persistence integration
# ---------------------------------------------------------------------------

class TestPersistencePipeline:
    def test_braid_session_persists_and_verifies(self) -> None:
        executor, manager, token = _executor("pipe5")
        store = PersistentEvidenceStore(":memory:")
        strands = [
            StrandState(value={"data": "persist_test"}, authority_token=token),
            StrandState(value={"shadow": True}, authority_token=token),
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

        with BraidSession("session-001", braid, executor, store) as session:
            result = session.execute()
            assert len(result.evidence_log) == 2
            verified, terminal = session.replay_from_store()

        assert verified
        assert store.record_count("session-001") == 2

    def test_braid_session_detects_corrupted_initial_state(self) -> None:
        executor, manager, token = _executor("pipe5b")
        store = PersistentEvidenceStore(":memory:")
        strands = [
            StrandState(value={"secret": 42}, authority_token=token),
            StrandState(value=None, authority_token=token),
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

        session = BraidSession("session-002", braid, executor, store)
        session.execute()

        # Corrupt the stored initial state and verify_reverse must catch it.
        stored_log = store.load_evidence_log("session-002")
        corrupted_initial = [
            StrandState(value={"secret": 999}, authority_token=token),
            StrandState(value=None, authority_token=token),
        ]
        ok, _ = verify_reverse(list(stored_log.records), corrupted_initial)
        assert not ok

    def test_persistence_store_lists_sessions(self) -> None:
        store = PersistentEvidenceStore(":memory:")
        executor, manager, token = _executor("pipe5c")
        for i in range(3):
            strands = [
                StrandState(value={"i": i}, authority_token=token),
                StrandState(value=None, authority_token=token),
            ]
            braid = ExecutableBraid(strands=strands)
            braid.add_crossing(ExecutableCrossing(
                "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
                operands={"required_scope": "execute"},
            ))
            with BraidSession(f"s-{i}", braid, executor, store) as session:
                session.execute()
        sessions = store.list_sessions()
        assert len(sessions) == 3
        assert {s["braid_id"] for s in sessions} == {"s-0", "s-1", "s-2"}

    def test_duplicate_session_id_raises(self) -> None:
        store = PersistentEvidenceStore(":memory:")
        executor, manager, token = _executor("pipe5d")
        strands = [StrandState(value=None, authority_token=token)]
        store.create_session("dup", strands)
        with pytest.raises(ValueError, match="already exists"):
            store.create_session("dup", strands)

    def test_load_nonexistent_session_raises(self) -> None:
        store = PersistentEvidenceStore(":memory:")
        with pytest.raises(KeyError):
            store.load_initial_strands("no-such-session")


# ---------------------------------------------------------------------------
# 6. INTEG.ATTEST and INTEG.COMPARE
# ---------------------------------------------------------------------------

class TestAttestCompare:
    def test_attest_attaches_attestation(self) -> None:
        executor, manager, token = _executor("pipe6")
        strands = [
            StrandState(value={"claim": "valid"}, authority_token=token),
            StrandState(value={"ref": True}, authority_token=token),
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
        braid.add_crossing(ExecutableCrossing(
            "attest", InstructionFamily.INTEG, IntegrityOpcode.ATTEST.value, 0, 1,
            operands={"attestation": "external-auditor-v1"},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value.get("attestation") == "external-auditor-v1"

    def test_compare_equal_strands_passes(self) -> None:
        executor, manager, token = _executor("pipe6b")
        val = {"same": 42}
        strands = [
            StrandState(value=val.copy(), authority_token=token),
            StrandState(value=val.copy(), authority_token=token),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "cmp", InstructionFamily.INTEG, IntegrityOpcode.COMPARE.value, 0, 1,
        ))
        result = braid.execute(executor)
        cmp_record = next(r for r in result.evidence_log if r.tag == "cmp")
        assert cmp_record.result == "PASS"

    def test_compare_different_strands_fails(self) -> None:
        executor, manager, token = _executor("pipe6c")
        strands = [
            StrandState(value={"a": 1}, authority_token=token),
            StrandState(value={"a": 2}, authority_token=token),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "cmp", InstructionFamily.INTEG, IntegrityOpcode.COMPARE.value, 0, 1,
        ))
        result = braid.execute(executor)
        cmp_record = next(r for r in result.evidence_log if r.tag == "cmp")
        assert cmp_record.result == "FAIL"


# ---------------------------------------------------------------------------
# 7. AUTH.INHERIT and AUTH.SCOPE
# ---------------------------------------------------------------------------

class TestAuthInheritScope:
    def test_auth_inherit_delegates_token_to_strand_j(self) -> None:
        executor, manager, token = _executor("pipe7")
        strands = [
            StrandState(value={"parent": True}, authority_token=token),
            StrandState(value={"child": True}),  # no token initially
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "inherit", InstructionFamily.AUTH, AuthOpcode.INHERIT.value, 0, 1,
            operands={"scope": ["execute"]},
        ))
        result = braid.execute(executor)
        assert result.final_strands[1].authority_token is not None
        assert "execute" in result.final_strands[1].authority_token.scope

    def test_auth_scope_restricts_token(self) -> None:
        executor, manager, token = _executor("pipe7b")
        strands = [
            StrandState(value=None, authority_token=token),
            StrandState(value=None),
        ]
        braid = ExecutableBraid(strands=strands)
        braid.add_crossing(ExecutableCrossing(
            "scope", InstructionFamily.AUTH, AuthOpcode.SCOPE.value, 0, 1,
            operands={"scope": ["execute"]},
        ))
        result = braid.execute(executor)
        # Original token had ["execute", "store", "verify"]; scoped to just ["execute"]
        new_token = result.final_strands[0].authority_token
        assert new_token is not None
        assert set(new_token.scope) == {"execute"}
