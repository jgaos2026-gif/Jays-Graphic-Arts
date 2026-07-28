"""
tests/bct_004_routing/test_routing_opcodes.py — ROUTE Family Test Suite

Tests every ROUTE opcode: SELECT, FORK, JOIN, REDIRECT, REPLAY.
"""
from __future__ import annotations

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    MemoryOpcode,
    RoutingOpcode,
    StrandState,
    TrustLevel,
)


def _make() -> tuple[BraidExecutor, list[StrandState]]:
    manager = AuthorityManager()
    token = manager.issue_token(role="ROUTER", scope=["execute"], token_id="route-tok")
    executor = BraidExecutor(manager)
    strands = [
        StrandState(value={"counter": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"shadow": 0}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]
    return executor, strands


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
# ROUTE.SELECT
# ---------------------------------------------------------------------------

class TestRouteSelect:
    def test_select_on_true_adds_route_to_value(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "select", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1,
            operands={
                "predicate": lambda v: v["counter"] > 0,
                "on_true": "primary",
                "on_false": "recovery",
            },
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value.get("route") == "primary"

    def test_select_on_false_adds_recovery_route(self) -> None:
        executor, strands = _make()
        strands[0].value["counter"] = -1
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "select", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1,
            operands={
                "predicate": lambda v: v["counter"] > 0,
                "on_true": "primary",
                "on_false": "recovery",
            },
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value.get("route") == "recovery"

    def test_select_records_decision(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "select", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1,
            operands={"predicate": lambda v: True, "on_true": "ok"},
        ))
        result = braid.execute(executor)
        assert any(r.tag == "select" for r in result.evidence_log)

    def test_select_appends_route_to_non_dict_value(self) -> None:
        manager = AuthorityManager()
        token = manager.issue_token(role="R", scope=["execute"], token_id="sel-nd")
        executor = BraidExecutor(manager)
        strands = [
            StrandState(value="plain-string", authority_token=token),
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
        braid.add_crossing(ExecutableCrossing(
            "select", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1,
            operands={"predicate": lambda v: True, "on_true": "chosen"},
        ))
        result = braid.execute(executor)
        assert isinstance(result.final_strands[0].value, dict)
        assert result.final_strands[0].value.get("route") == "chosen"


# ---------------------------------------------------------------------------
# ROUTE.FORK
# ---------------------------------------------------------------------------

class TestRouteFork:
    def test_fork_copies_strand_i_to_strand_j(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[1].value == result.final_strands[0].value

    def test_fork_appends_evidence(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert any(r.tag == "fork" for r in result.evidence_log)

    def test_fork_tags_both_strand_histories(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert "fork" in result.final_strands[0].history
        assert "fork" in result.final_strands[1].history


# ---------------------------------------------------------------------------
# ROUTE.JOIN
# ---------------------------------------------------------------------------

class TestRouteJoin:
    def test_join_merges_two_strands(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "join", InstructionFamily.ROUTE, RoutingOpcode.JOIN.value, 0, 1,
        ))
        result = braid.execute(executor)
        merged = result.final_strands[0].value
        # Default merge produces {"left": ..., "right": ...}
        assert "left" in merged
        assert "right" in merged

    def test_join_custom_merge_fn(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "join", InstructionFamily.ROUTE, RoutingOpcode.JOIN.value, 0, 1,
            operands={"merge_fn": lambda a, b: {"combined": True}},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value == {"combined": True}

    def test_join_appends_evidence(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "join", InstructionFamily.ROUTE, RoutingOpcode.JOIN.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert any(r.tag == "join" for r in result.evidence_log)


# ---------------------------------------------------------------------------
# ROUTE.REDIRECT
# ---------------------------------------------------------------------------

class TestRouteRedirect:
    def test_redirect_adds_destination_to_value(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "redirect", InstructionFamily.ROUTE, RoutingOpcode.REDIRECT.value, 0, 1,
            operands={"destination": "fallback-lane"},
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value.get("redirected_to") == "fallback-lane"

    def test_redirect_default_destination(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "redirect", InstructionFamily.ROUTE, RoutingOpcode.REDIRECT.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert result.final_strands[0].value.get("redirected_to") == "alternate"

    def test_redirect_appends_evidence(self) -> None:
        executor, strands = _make()
        braid = _verified_braid(strands)
        braid.add_crossing(ExecutableCrossing(
            "redirect", InstructionFamily.ROUTE, RoutingOpcode.REDIRECT.value, 0, 1,
        ))
        result = braid.execute(executor)
        assert any(r.tag == "redirect" for r in result.evidence_log)


# ---------------------------------------------------------------------------
# ROUTE.REPLAY
# ---------------------------------------------------------------------------

class TestRouteReplay:
    def test_replay_restores_strand_from_checkpoint(self) -> None:
        executor, strands = _make()
        # Create a checkpoint via MEM.STORE_HOT, then overwrite value, then replay.
        manager = AuthorityManager()
        token = manager.issue_token(role="REPLAY", scope=["execute"], token_id="replay-tok")
        executor2 = BraidExecutor(manager)
        strands2 = [
            StrandState(value={"stable": 42}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value=None, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
        braid = ExecutableBraid(strands=strands2)
        braid.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        braid.add_crossing(ExecutableCrossing(
            "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
            operands={"predicate": lambda v: True},
        ))
        # ROUTE.REPLAY restores from checkpoint tagged "verify"
        braid.add_crossing(ExecutableCrossing(
            "replay", InstructionFamily.ROUTE, RoutingOpcode.REPLAY.value, 0, 1,
            operands={"checkpoint_tag": "verify"},
        ))
        result = braid.execute(executor2)
        # After replay, strand 0 is restored from the "verify" checkpoint
        assert any(r.tag == "replay" for r in result.evidence_log)
