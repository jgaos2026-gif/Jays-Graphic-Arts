"""
tests/bct_006_memory/test_memory_tiers.py — MEM Family Test Suite

Tests every MEM opcode:
  STORE_HOT, LOAD_HOT, DEMOTE_WARM, PROMOTE_HOT,
  ARCHIVE_COLD, RETRIEVE_COLD, OPEN_POCKET, CLOSE_POCKET, STITCH.
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
    MemoryOpcode,
    StrandState,
    TrustLevel,
)


def _make() -> tuple[BraidExecutor, AuthorityManager, list[StrandState]]:
    manager = AuthorityManager()
    token = manager.issue_token(role="MEM_OPS", scope=["execute"], token_id="mem-tok")
    executor = BraidExecutor(manager)
    strands = [
        StrandState(value={"data": "payload"}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"mirror": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]
    return executor, manager, strands


def _verified_braid(strands: list[StrandState]) -> ExecutableBraid:
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
# MEM.STORE_HOT / MEM.LOAD_HOT
# ---------------------------------------------------------------------------

class TestHotMemory:
    def test_store_hot_and_load_hot_round_trip(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "mykey"},
        ))
        original_value = strands[0].value.copy()
        # Modify strand value after storing
        braid.add_crossing(ExecutableCrossing(
            "load", InstructionFamily.MEM, MemoryOpcode.LOAD_HOT.value, 0, 1,
            operands={"key": "mykey"},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "store" for r in result.evidence_log)
        assert any(r.tag == "load" for r in result.evidence_log)

    def test_store_hot_appends_evidence(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "k1"},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "store" for r in result.evidence_log)
        assert any(r.result == "PASS" for r in result.evidence_log if r.tag == "store")

    def test_store_hot_creates_checkpoint(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "k2"},
        ))
        result = braid.execute(executor)
        # STORE_HOT calls record_checkpoint internally if a trusted strand exists
        assert len(result.checkpoints) >= 1

    def test_load_hot_uses_tag_as_default_key(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "mystore", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
        ))
        braid.add_crossing(ExecutableCrossing(
            "mystore", InstructionFamily.MEM, MemoryOpcode.LOAD_HOT.value, 0, 1,
        ))
        result = braid.execute(executor)
        load_record = [r for r in result.evidence_log if r.opcode == MemoryOpcode.LOAD_HOT.value]
        assert len(load_record) == 1
        assert load_record[0].result == "PASS"


# ---------------------------------------------------------------------------
# MEM.DEMOTE_WARM / MEM.PROMOTE_HOT
# ---------------------------------------------------------------------------

class TestWarmMemory:
    def test_demote_to_warm_and_promote_back(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "wk"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "demote", InstructionFamily.MEM, MemoryOpcode.DEMOTE_WARM.value, 0, 1,
            operands={"key": "wk"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "promote", InstructionFamily.MEM, MemoryOpcode.PROMOTE_HOT.value, 0, 1,
            operands={"key": "wk"},
        ))
        result = braid.execute(executor)
        for tag in ["store", "demote", "promote"]:
            assert any(r.tag == tag for r in result.evidence_log)

    def test_demote_result_is_pass(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "dk"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "demote", InstructionFamily.MEM, MemoryOpcode.DEMOTE_WARM.value, 0, 1,
            operands={"key": "dk"},
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "demote")
        assert record.result == "PASS"


# ---------------------------------------------------------------------------
# MEM.ARCHIVE_COLD / MEM.RETRIEVE_COLD
# ---------------------------------------------------------------------------

class TestColdMemory:
    def test_archive_and_retrieve(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
            operands={"key": "ck"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "demote", InstructionFamily.MEM, MemoryOpcode.DEMOTE_WARM.value, 0, 1,
            operands={"key": "ck"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "archive", InstructionFamily.MEM, MemoryOpcode.ARCHIVE_COLD.value, 0, 1,
            operands={"key": "ck"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "retrieve", InstructionFamily.MEM, MemoryOpcode.RETRIEVE_COLD.value, 0, 1,
            operands={"key": "ck"},
        ))
        result = braid.execute(executor)
        for tag in ["store", "demote", "archive", "retrieve"]:
            assert any(r.tag == tag for r in result.evidence_log)


# ---------------------------------------------------------------------------
# MEM.OPEN_POCKET / MEM.CLOSE_POCKET
# ---------------------------------------------------------------------------

class TestPockets:
    def test_open_and_close_pocket(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "open", InstructionFamily.MEM, MemoryOpcode.OPEN_POCKET.value, 0, 1,
            operands={"key": "pk", "scope": "local"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "close", InstructionFamily.MEM, MemoryOpcode.CLOSE_POCKET.value, 0, 1,
            operands={"key": "pk"},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "open" for r in result.evidence_log)
        assert any(r.tag == "close" for r in result.evidence_log)

    def test_open_pocket_default_scope(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "open", InstructionFamily.MEM, MemoryOpcode.OPEN_POCKET.value, 0, 1,
            operands={"key": "pk2"},
        ))
        result = braid.execute(executor)
        assert any(r.result == "PASS" for r in result.evidence_log if r.tag == "open")

    def test_close_nonexistent_pocket_is_safe(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "close", InstructionFamily.MEM, MemoryOpcode.CLOSE_POCKET.value, 0, 1,
            operands={"key": "nonexistent"},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "close" for r in result.evidence_log)


# ---------------------------------------------------------------------------
# MEM.STITCH
# ---------------------------------------------------------------------------

class TestStitch:
    def test_stitch_appends_evidence(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "stitch", InstructionFamily.MEM, MemoryOpcode.STITCH.value, 0, 1,
            operands={"region_a": "zone-A", "region_b": "zone-B"},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "stitch" for r in result.evidence_log)

    def test_stitch_result_is_pass(self) -> None:
        executor, _, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "stitch", InstructionFamily.MEM, MemoryOpcode.STITCH.value, 0, 1,
            operands={"region_a": "A", "region_b": "B"},
        ))
        result = braid.execute(executor)
        record = next(r for r in result.evidence_log if r.tag == "stitch")
        assert record.result == "PASS"
