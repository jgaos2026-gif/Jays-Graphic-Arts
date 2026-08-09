"""
BCT-001 Integrity — Non-Commutative Crossing Adversarial Suite

Verifies that the Integrity braid correctly enforces its non-commutative
crossing semantics:

  • INTEG.PROMOTE must be preceded by AUTH.CHECK + INTEG.VERIFY — no shortcuts.
  • Trust levels are strictly monotone: ACTIVE → TRUSTED → CERTIFIED.
    QUARANTINED is a terminal absorbing state exitable only via HEAL + re-verify.
  • An adversary who attempts to bypass AUTH.CHECK, skip INTEG.VERIFY, or directly
    promote from ACTIVE must receive a LawViolation with a message referencing the
    violated law number.
  • A braid-relation reordering of INTEGRITY crossings (legal Reidemeister move)
    produces the same normal form and must NOT raise TopologicalMismatchFault —
    the non-commutativity detector must not produce false positives on this case.
  • An illegal adjacent transposition of integrity crossings must produce a
    different normal form AND trigger TopologicalMismatchFault.
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
    StrandState,
    TopologicalMismatchFault,
    TrustLevel,
    check_topological_equivalence,
    reduce_to_normal_form,
    sigma,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_executor() -> tuple[BraidExecutor, object]:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="integ_tok")
    return BraidExecutor(manager), token


def _strands(token, *, n: int = 2) -> list[StrandState]:
    return [
        StrandState(value={"x": i}, trust_level=TrustLevel.ACTIVE, authority_token=token)
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_promote_without_verify_raises_law_violation() -> None:
    """
    Law 1: No active state becomes trusted or certified without verification.

    Attempting INTEG.PROMOTE directly after AUTH.CHECK (skipping INTEG.VERIFY)
    must raise LawViolation referencing Law 1.
    """
    executor, token = _make_executor()
    braid = ExecutableBraid(strands=_strands(token))
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "promote_bypass", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
    ))

    with pytest.raises(LawViolation, match="Law 1"):
        braid.execute(executor)


def test_promote_without_auth_check_raises_law_violation() -> None:
    """
    Law 4: AUTH.CHECK must precede any state promotion.

    Attempting INTEG.VERIFY + INTEG.PROMOTE with no AUTH.CHECK must raise
    LawViolation referencing Law 4 on the VERIFY step (auth check required first).
    """
    executor, token = _make_executor()
    braid = ExecutableBraid(strands=_strands(token))
    braid.add_crossing(ExecutableCrossing(
        "verify_no_auth", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))

    with pytest.raises(LawViolation, match="Law 4"):
        braid.execute(executor)


def test_revoked_token_blocks_verify() -> None:
    """
    Law 9: Promoted strands require an explicit non-revoked authority token.

    Revoking a token before execution causes INTEG.VERIFY to raise LawViolation
    referencing Law 9.
    """
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="revoke_integ")
    executor = BraidExecutor(manager)

    braid = ExecutableBraid(strands=[
        StrandState(value={"x": 0}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"x": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ])
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: True},
    ))

    # Revoke the token BEFORE execution — the executor must see a revoked token.
    manager.revoke_token(token)

    with pytest.raises(LawViolation, match="Law 9"):
        braid.execute(executor)


def test_trust_level_monotone_active_trusted_certified() -> None:
    """
    PO-6: Trust levels are strictly monotone ACTIVE → TRUSTED → CERTIFIED.

    A full AUTH.CHECK → INTEG.VERIFY → INTEG.PROMOTE chain must advance the
    trust level through exactly these states, never skipping or reversing.
    """
    executor, token = _make_executor()
    braid = ExecutableBraid(strands=_strands(token))
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

    assert result.final_strands[0].trust_level == TrustLevel.CERTIFIED, (
        f"Expected CERTIFIED after full verification chain, "
        f"got {result.final_strands[0].trust_level!r}."
    )
    assert result.final_strands[1].trust_level == TrustLevel.ACTIVE, (
        "Strand 1 was not part of the promotion chain and must remain ACTIVE."
    )


def test_failed_verify_does_not_promote() -> None:
    """
    A failing INTEG.VERIFY must leave trust_level at ACTIVE and block PROMOTE.

    If the predicate returns False, the strand must not be promoted to TRUSTED.
    A subsequent PROMOTE must then raise LawViolation (Law 1).
    """
    executor, token = _make_executor()
    braid = ExecutableBraid(strands=_strands(token))
    braid.add_crossing(ExecutableCrossing(
        "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
        operands={"required_scope": "execute"},
    ))
    braid.add_crossing(ExecutableCrossing(
        "bad_verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
        operands={"predicate": lambda v: False},   # always fails
    ))
    braid.add_crossing(ExecutableCrossing(
        "promote_after_fail", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
    ))

    with pytest.raises(LawViolation, match="Law 1"):
        braid.execute(executor)


def test_noncommutative_crossing_braid_relation_not_a_mismatch() -> None:
    """
    PO-1 Regime B applied to integrity crossings: the three-crossing braid
    relation σ_1 σ_2 σ_1 = σ_2 σ_1 σ_2 must NOT raise TopologicalMismatchFault.

    This mirrors test_regime_b_braid_relation_is_legitimate but is explicit
    about the Integrity braid context to close the OP-9 gap at the BCT-001 level.
    """
    W  = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
    Wp = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)

    assert reduce_to_normal_form(W) == reduce_to_normal_form(Wp), (
        "σ_1 σ_2 σ_1 and σ_2 σ_1 σ_2 have different normal forms — "
        "the braid relation is not recognised as a legal Reidemeister move."
    )

    try:
        check_topological_equivalence(W, Wp)
    except TopologicalMismatchFault as exc:
        pytest.fail(
            f"TopologicalMismatchFault raised for a valid braid-relation reordering "
            f"of Integrity crossings (false positive / OP-9 gap): {exc}"
        )


def test_noncommutative_crossing_illegal_swap_is_mismatch() -> None:
    """
    PO-1 Regime B tamper case: σ_1 σ_2 → σ_2 σ_1 in B_3 is an illegal
    adjacent transposition of Integrity crossings.

    The normal forms must differ AND TopologicalMismatchFault must be raised.
    """
    W  = sigma(1, 3) * sigma(2, 3)
    Wp = sigma(2, 3) * sigma(1, 3)

    nf_W  = reduce_to_normal_form(W)
    nf_Wp = reduce_to_normal_form(Wp)

    assert nf_W != nf_Wp, (
        f"CRITICAL: σ_1 σ_2 and σ_2 σ_1 have the SAME normal form — "
        f"the tamper detector cannot distinguish illegal transpositions from the "
        f"braid relation (OP-9 gap).\n"
        f"  NF(σ_1 σ_2) = {nf_W.canonical}\n"
        f"  NF(σ_2 σ_1) = {nf_Wp.canonical}"
    )

    with pytest.raises(TopologicalMismatchFault):
        check_topological_equivalence(W, Wp)


def test_evidence_log_records_every_integrity_crossing() -> None:
    """
    PO-2: Every crossing appends exactly one evidence record.

    A three-crossing braid (AUTH, VERIFY, PROMOTE) must produce exactly 3
    records in the evidence log — no crossing may be silent.
    """
    executor, token = _make_executor()
    braid = ExecutableBraid(strands=_strands(token))
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

    assert len(result.evidence_log) == 3, (
        f"Expected 3 evidence records for a 3-crossing braid, "
        f"got {len(result.evidence_log)}: "
        f"{[r.tag for r in result.evidence_log.records]}"
    )
    assert [r.tag for r in result.evidence_log.records] == ["auth", "verify", "promote"], (
        "Evidence record tags do not match crossing order."
    )
