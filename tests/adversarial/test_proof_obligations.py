"""
tests/adversarial/test_proof_obligations.py

Executable proof-obligation tests for theory/PROOF_OBLIGATIONS.md.

Every test makes a concrete assertion against real implementation code and
fails loudly with a diagnostic message if the condition is false.  No mocks,
no stubs, no hand-computed expected values — only the algebra engine and the
execution kernel.

Test Group 1 — Two-Regime Ordering (PO-1, §1)
  1a. Far commutativity: σ_i σ_j = σ_j σ_i for |i−j| ≥ 2
  1b. Braid relation is legitimate: σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}
      must NOT be flagged as a topological mismatch fault (OP-9 edge case).
  1c. Actual tamper detected: an illegal adjacent transposition must produce
      a DIFFERENT normal form from 1b AND must raise TopologicalMismatchFault.

Test Group 2 — Bounded Quarantine (BCT-003, §2)
  2a. Injecting a fault on strands k..k+2 quarantines exactly those strands;
      strands at index-distance ≥ 2 from the faulted range continue executing.

Test Group 3 — Duplex Continuity / Reverse Verification (PO-3, §3)
  3a. Forward execution produces V_{t+1}.  verify_reverse independently replays
      the evidence log against the initial state and confirms the recovered
      terminal state hash matches V_{t+1}.  Corrupting the initial state causes
      verify_reverse to return False.
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
    StrandState,
    TopologicalMismatchFault,
    TrustLevel,
    check_topological_equivalence,
    halted_strands,
    quarantine_neighborhood,
    reduce_to_normal_form,
    sigma,
    verify_reverse,
)
from braid_simulator.evidence import stable_hash


# ============================================================================
# Test Group 1 — Two-Regime Ordering
# ============================================================================

def test_regime_a_far_commutativity() -> None:
    """
    PO-1 Regime A: σ_1 σ_3 = σ_3 σ_1 in B_4 (|1−3| = 2 ≥ 2).

    Both words must reduce to the same normal form via reduce_to_normal_form —
    the real braid word reduction function, not a hand-computed value.
    """
    W  = sigma(1, 4) * sigma(3, 4)   # σ_1 σ_3
    Wp = sigma(3, 4) * sigma(1, 4)   # σ_3 σ_1

    nf_W  = reduce_to_normal_form(W)
    nf_Wp = reduce_to_normal_form(Wp)

    assert nf_W == nf_Wp, (
        f"Far-commutativity FAILED: σ_1 σ_3 and σ_3 σ_1 have DIFFERENT normal forms in B_4.\n"
        f"  NF(σ_1 σ_3) = {nf_W.canonical}\n"
        f"  NF(σ_3 σ_1) = {nf_Wp.canonical}\n"
        "These words must be equivalent because |1−3| = 2 ≥ 2 (far commutativity)."
    )


def test_regime_b_braid_relation_is_legitimate() -> None:
    """
    PO-1 Regime B (OP-9 edge case): σ_1 σ_2 σ_1 = σ_2 σ_1 σ_2 in B_3.

    Both words must:
      1. Reduce to the SAME normal form (they equal the Garside element Δ_3).
      2. NOT cause check_topological_equivalence to raise TopologicalMismatchFault.

    An adversary who reorders crossings in the exact pattern of the braid relation
    is performing a legitimate Reidemeister move — the detector must not produce
    a false positive here.  Failure to handle this case is the OP-9 gap.
    """
    W  = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)   # σ_1 σ_2 σ_1
    Wp = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)   # σ_2 σ_1 σ_2

    nf_W  = reduce_to_normal_form(W)
    nf_Wp = reduce_to_normal_form(Wp)

    assert nf_W == nf_Wp, (
        f"Braid relation FAILED: σ_1 σ_2 σ_1 and σ_2 σ_1 σ_2 have DIFFERENT normal forms.\n"
        f"  NF(σ_1 σ_2 σ_1) = {nf_W.canonical}\n"
        f"  NF(σ_2 σ_1 σ_2) = {nf_Wp.canonical}\n"
        "Both words must equal Δ_3 in B_3."
    )

    # The verification engine must NOT flag this as a mismatch.
    try:
        check_topological_equivalence(W, Wp)
    except TopologicalMismatchFault as exc:
        pytest.fail(
            f"check_topological_equivalence raised TopologicalMismatchFault for a VALID "
            f"braid-relation reordering (OP-9 false positive):\n{exc}"
        )


def test_regime_b_actual_tamper_detected() -> None:
    """
    PO-1 Regime B tamper case: σ_1 σ_2 ≠ σ_2 σ_1 in B_3.

    An illegal adjacent transposition (not far-commutativity, not the braid relation)
    must satisfy ALL of the following:

      1. reduce_to_normal_form gives DIFFERENT results for the two words.
      2. check_topological_equivalence raises TopologicalMismatchFault.
      3. The normal form of the tampered word is DIFFERENT from both words in
         the legitimate braid-relation case (test 1b) — proving the detector
         distinguishes illegal from legitimate adjacent reorderings.

    Point 3 is the critical claim: two-crossing adjacent swap ≠ three-crossing
    braid relation, even though both involve reordering adjacent generators.
    """
    W  = sigma(1, 3) * sigma(2, 3)   # σ_1 σ_2  (valid braid)
    Wp = sigma(2, 3) * sigma(1, 3)   # σ_2 σ_1  (illegal transposition of W)

    nf_W  = reduce_to_normal_form(W)
    nf_Wp = reduce_to_normal_form(Wp)

    # 1 — Normal forms must differ.
    assert nf_W != nf_Wp, (
        f"CRITICAL — tamper NOT detected: σ_1 σ_2 and σ_2 σ_1 have the SAME normal form.\n"
        f"  NF(σ_1 σ_2) = {nf_W.canonical}\n"
        f"  NF(σ_2 σ_1) = {nf_Wp.canonical}\n"
        "If both reduce to the same form the tamper detector cannot distinguish an illegal "
        "adjacent transposition from a legitimate braid-relation reordering (OP-9 gap)."
    )

    # 2 — The verification engine must raise TopologicalMismatchFault.
    with pytest.raises(TopologicalMismatchFault):
        check_topological_equivalence(W, Wp)

    # 3 — Neither tampered word shares a normal form with the legitimate braid-relation words.
    braid_rel_W  = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)   # = Δ_3
    nf_braid_rel = reduce_to_normal_form(braid_rel_W)

    assert nf_W != nf_braid_rel, (
        f"σ_1 σ_2 has the same normal form as σ_1 σ_2 σ_1 (Δ_3).\n"
        f"  NF(σ_1 σ_2)      = {nf_W.canonical}\n"
        f"  NF(σ_1 σ_2 σ_1)  = {nf_braid_rel.canonical}\n"
        "The two-crossing word must be strictly shorter/different from the three-crossing Δ_3."
    )

    assert nf_Wp != nf_braid_rel, (
        f"σ_2 σ_1 has the same normal form as σ_2 σ_1 σ_2 (Δ_3).\n"
        f"  NF(σ_2 σ_1)      = {nf_Wp.canonical}\n"
        f"  NF(σ_2 σ_1 σ_2)  = {nf_braid_rel.canonical}\n"
        "The illegal transposition must be strictly different from the legitimate braid relation."
    )


# ============================================================================
# Test Group 2 — Bounded Quarantine
# ============================================================================

def test_quarantine_blast_radius() -> None:
    """
    BCT-003 bounded neighborhood quarantine.

    A 10-strand braid has a fault injected on strands k=4 through k+2=6.
    The test asserts:
      • Exactly 3 strands are quarantined (the faulted range — not the full strand count).
      • Strands at index-distance ≥ 2 from [4, 6] remain ACTIVE.
      • halted_strands() agrees with quarantine_neighborhood()'s return value.
    """
    n_strands = 10
    k = 4                              # fault starts here
    fault_range = list(range(k, k + 3))  # [4, 5, 6]
    faulted_min, faulted_max = fault_range[0], fault_range[-1]

    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"])
    strands = [
        StrandState(value={"id": i}, trust_level=TrustLevel.ACTIVE, authority_token=token)
        for i in range(n_strands)
    ]

    quarantined_indices = quarantine_neighborhood(fault_range, strands)
    halted = halted_strands(strands)

    actual_quarantined = set(quarantined_indices)
    actual_halted      = set(halted)
    expected           = set(fault_range)

    # quarantine_neighborhood() must return exactly the faulted indices.
    assert actual_quarantined == expected, (
        f"quarantine_neighborhood() quarantined {sorted(actual_quarantined)} "
        f"but expected exactly {sorted(expected)}."
    )

    # halted_strands() must agree with quarantine_neighborhood().
    assert actual_halted == expected, (
        f"halted_strands() reports {sorted(actual_halted)} quarantined, "
        f"but the fault was on {sorted(expected)}. "
        f"Actual halted count: {len(halted)}/{n_strands}."
    )

    # Count must equal the fault range, NOT the full strand count.
    assert len(halted) == len(fault_range), (
        f"Expected {len(fault_range)} halted strands, "
        f"got {len(halted)}/{n_strands} total. "
        f"Halted: {sorted(halted)}."
    )

    # Strands at index-distance ≥ 2 from [faulted_min, faulted_max] must be ACTIVE.
    safe_strands = [
        i for i in range(n_strands)
        if i <= faulted_min - 2 or i >= faulted_max + 2
    ]
    assert safe_strands, "No safe strands found — increase n_strands or reduce fault range."

    for idx in safe_strands:
        assert strands[idx].trust_level == TrustLevel.ACTIVE, (
            f"Strand {idx} is at distance ≥ 2 from faulted range "
            f"[{faulted_min}, {faulted_max}] but was halted "
            f"(trust_level={strands[idx].trust_level!r}). "
            f"Total halted: {len(halted)}/{n_strands} strands: {sorted(halted)}."
        )


# ============================================================================
# Test Group 3 — Duplex Reverse Verification (PO-3)
# ============================================================================

def test_duplex_agreement_promotes() -> None:
    """
    PO-3 Reconstructability: the evidence log is the source of truth.

    Forward execution: AUTH.CHECK → INTEG.VERIFY → INTEG.PROMOTE
    Final strand state: CERTIFIED.

    verify_reverse independently replays the evidence log against the original
    initial strands and must recover a terminal state whose hash matches the
    forward executor's final state exactly.

    Corruption detection: replacing the initial strand value causes verify_reverse
    to return False at the very first hash check — proving the log alone is
    sufficient to detect silent state corruption.
    """
    manager = AuthorityManager()
    token   = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="duplex_tok")
    executor = BraidExecutor(manager)

    # Record initial state BEFORE execution (deep-cloned by ExecutableBraid.__init__).
    initial_strands = [
        StrandState(value={"payload": "data"}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        StrandState(value={"shadow": True},    trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]

    braid = ExecutableBraid(strands=initial_strands)
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
        "Forward execution did not promote strand 0 to CERTIFIED — "
        "precondition for verify_reverse test is not met."
    )

    # ── Verify-reverse: replay evidence log against the original initial state ──
    verified, terminal_strands = verify_reverse(
        list(result.evidence_log.records),
        initial_strands,          # original state before any crossing
    )

    assert verified, (
        "verify_reverse returned False for an uncorrupted forward execution.\n"
        "The evidence log is not consistent with the initial state — "
        "the hash chain has a gap."
    )

    # Recovered terminal state must have the same hash as the forward result.
    expected_hash  = stable_hash([s.to_dict() for s in result.final_strands])
    recovered_hash = stable_hash([s.to_dict() for s in terminal_strands])

    assert recovered_hash == expected_hash, (
        f"verify_reverse produced a different terminal state than forward execution.\n"
        f"  Expected hash (forward):   {expected_hash[:24]}...\n"
        f"  Recovered hash (reverse):  {recovered_hash[:24]}...\n"
        "The reverse-verification engine and the forward executor disagree on the "
        "terminal state — the evidence log does not faithfully encode the execution."
    )

    # ── Corruption detection ────────────────────────────────────────────────
    # Modify the initial strand value — the first record's input_hash must diverge.
    corrupted_strands = [
        StrandState(
            value={"payload": "CORRUPTED_BY_ADVERSARY"},
            trust_level=TrustLevel.ACTIVE,
            authority_token=token,
        ),
        StrandState(value={"shadow": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
    ]

    verified_corrupted, _ = verify_reverse(
        list(result.evidence_log.records),
        corrupted_strands,
    )

    assert not verified_corrupted, (
        "verify_reverse returned True for a CORRUPTED initial state.\n"
        "The evidence log must detect that the provided initial state does not match "
        "the hash recorded at the start of the logged execution."
    )
