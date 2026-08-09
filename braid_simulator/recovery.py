"""
braid_simulator/recovery.py — Reverse Verification Engine

Implements the forward-replay verification path for proof obligation PO-3
(Reconstructability via Decoupled Provenance).

verify_reverse():
    Independently replay an evidence log against a known initial state and
    verify that the reconstructed terminal state matches the forward execution.

    The function treats the evidence log — not the terminal state — as the
    source of truth.  It applies the minimal deterministic state transitions
    implied by each evidence record (trust-level changes and history updates)
    and verifies the per-crossing hash chain matches at every step.

    If the initial state is corrupted (hashes diverge at step 0), or if any
    intermediate crossing hash mismatches, the function returns (False, ...).
    A caller can therefore detect silent state corruption by comparing the
    hash of verify_reverse's recovered terminal state against a known-good
    checkpoint hash.

SCOPE NOTE: This module implements the hash-chain verification component of
PO-3.  Full algebraic inverse composition (f^{-1} per opcode) is a Phase 2
deliverable (see theory/PROOF_OBLIGATIONS.md §3).
"""
from __future__ import annotations

from .evidence import EvidenceRecord, stable_hash
from .instructions import IntegrityOpcode, RecoveryOpcode, RoleOpcode, RoutingOpcode, AuthOpcode
from .state import StrandState, TrustLevel


def _apply_fork_semantics(
    strands: list[StrandState],
    i: int,
    j: int,
) -> None:
    """
    Replicate ROUTE.FORK's clone-before-touch semantics during hash-chain replay.

    The forward executor (crossing.py) clones strand_i into strand_j BEFORE
    calling _touch on either strand.  This helper must therefore be called
    before the standard history-append step in _apply_verified_transition.
    Mirrors crossing.py lines 196-198:
        strands[j] = state_i.clone()
        _touch(state_i, tag)   ← happens outside this helper
        _touch(strands[j], tag) ← happens in the strand_j block
    """
    strands[j] = strands[i].clone()


def _apply_transfer_semantics(
    strands: list[StrandState],
    i: int,
    j: int,
) -> None:
    """
    Replicate ROLE.TRANSFER's atomic token-move during hash-chain replay.

    Mirrors crossing.py lines 274-275:
        state_j.authority_token = state_i.authority_token
        state_i.authority_token = None
    Both the forward executor and this replay helper must stay in sync.
    """
    strands[j].authority_token = strands[i].authority_token
    strands[i].authority_token = None


def _apply_verified_transition(record: EvidenceRecord, strands: list[StrandState]) -> None:
    """
    Apply the minimum deterministic state update implied by a single evidence record.

    Every crossing calls _touch(strand_i, tag) — appending the tag to the strand's
    history.  Selected opcodes additionally change trust_level.  This function
    reproduces exactly those side-effects so that verify_reverse can recompute
    the output hash at each step.

    Fully supported (history + trust-level):
        AUTH.CHECK / AUTH.GATE   — history only (strand_i)
        INTEG.VERIFY             — history + ACTIVE → TRUSTED on PASS
        INTEG.PROMOTE            — history + TRUSTED → CERTIFIED on PASS
        INTEG.SEAL               — history + any → CERTIFIED on PASS
        RECOV.QUARANTINE         — history + any → QUARANTINED
        RECOV.HEAL               — history + any → ACTIVE on PASS

    History-only (state.value modifications from these opcodes are opaque to
    the verification replayer; the output hash check will catch any divergence):
        All other opcodes (ROUTE.SELECT, MEM.STORE_HOT, etc.)

    Crossings that also _touch strand_j (history on j):
        AUTH.INHERIT, INTEG.COMPARE, ROUTE.FORK, ROUTE.JOIN, ROLE.TRANSFER,
        ROLE.DELEGATE
    """
    i = record.strand_i
    j = record.strand_j
    family = record.family
    opcode = record.opcode
    result = record.result

    if i >= len(strands):
        return

    # ROUTE.FORK: clone strand_i into strand_j BEFORE touching either strand.
    # See _apply_fork_semantics() for the ordering rationale.
    if (family == "ROUTE" and opcode == RoutingOpcode.FORK.value
            and j != i and 0 <= j < len(strands)):
        _apply_fork_semantics(strands, i, j)

    # Every crossing calls _touch(state_i, tag) — append tag to strand_i history.
    strands[i].history.append(record.tag)

    # Trust-level transitions for supported opcodes.
    if family == "INTEG":
        if opcode == IntegrityOpcode.VERIFY.value and result == "PASS":
            if strands[i].trust_level == TrustLevel.ACTIVE:
                strands[i].trust_level = TrustLevel.TRUSTED
        elif opcode == IntegrityOpcode.PROMOTE.value and result == "PASS":
            if strands[i].trust_level == TrustLevel.TRUSTED:
                strands[i].trust_level = TrustLevel.CERTIFIED
        elif opcode == IntegrityOpcode.SEAL.value and result == "PASS":
            strands[i].trust_level = TrustLevel.CERTIFIED
    elif family == "RECOV":
        if opcode == RecoveryOpcode.QUARANTINE.value:
            strands[i].trust_level = TrustLevel.QUARANTINED
        elif opcode == RecoveryOpcode.HEAL.value and result == "PASS":
            strands[i].trust_level = TrustLevel.ACTIVE

    # Crossings that also call _touch on strand_j.
    _ALSO_TOUCH_J = {
        ("AUTH", AuthOpcode.INHERIT.value),
        ("INTEG", IntegrityOpcode.COMPARE.value),
        ("ROUTE", RoutingOpcode.FORK.value),
        ("ROUTE", RoutingOpcode.JOIN.value),
        ("ROLE", RoleOpcode.TRANSFER.value),
        ("ROLE", RoleOpcode.DELEGATE.value),
    }
    if (family, opcode) in _ALSO_TOUCH_J and j != i and 0 <= j < len(strands):
        # ROLE.TRANSFER: authority_token moves atomically from strand_i to strand_j.
        # See _apply_transfer_semantics() which mirrors crossing.py lines 274-275.
        if family == "ROLE" and opcode == RoleOpcode.TRANSFER.value:
            _apply_transfer_semantics(strands, i, j)
        strands[j].history.append(record.tag)


def verify_reverse(
    log_records: list[EvidenceRecord],
    initial_strands: list[StrandState],
) -> tuple[bool, list[StrandState]]:
    """
    Independently verify an evidence log by replaying it against initial_strands.

    For each evidence record the function:
      1. Computes the hash of the relevant strands (strand_i and strand_j) in
         the current reconstructed state.
      2. Asserts it equals record.input_hash.
      3. Applies the deterministic state transition (_apply_verified_transition).
      4. Recomputes the hash of the relevant strands after the transition.
      5. Asserts it equals record.output_hash.

    If all 2 × len(log_records) hash checks pass, the log is internally
    consistent with the initial state and verify_reverse returns (True, terminal).

    If any check fails, verify_reverse returns (False, strands_at_point_of_failure)
    immediately — the log has diverged from the initial state, indicating either
    a corrupted initial state or a tampered log.

    Parameters
    ----------
    log_records:
        The evidence records from an ExecutionResult, in execution order.
    initial_strands:
        The strand state at the moment execution began (before the first crossing
        in log_records).  These are NOT mutated; clones are used internally.

    Returns
    -------
    (verified: bool, terminal_strands: list[StrandState])
        verified        — True iff the full hash chain is consistent.
        terminal_strands — The reconstructed strand state after all records.
                          If verified is True this matches the forward executor's
                          final state exactly.  If False it reflects the state at
                          the point of divergence.
    """
    strands = [s.clone() for s in initial_strands]

    for record in log_records:
        i = record.strand_i
        j = record.strand_j

        # Build relevant-strands list (same logic as BraidExecutor._relevant_states).
        relevant_indices = [i] + ([j] if j != i and 0 <= j < len(strands) else [])
        relevant_before = [strands[k] for k in relevant_indices if k < len(strands)]

        computed_input = stable_hash([s.to_dict() for s in relevant_before])
        if computed_input != record.input_hash:
            return False, strands

        _apply_verified_transition(record, strands)

        relevant_after = [strands[k] for k in relevant_indices if k < len(strands)]
        computed_output = stable_hash([s.to_dict() for s in relevant_after])
        if computed_output != record.output_hash:
            return False, strands

    return True, strands
