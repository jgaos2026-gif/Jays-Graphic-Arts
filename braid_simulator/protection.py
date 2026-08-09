"""
braid_simulator/protection.py — Bounded Neighborhood Quarantine

Implements BCT-003 (Protection): fault isolation that quarantines a bounded
region of the braid rather than halting the entire computation.

quarantine_neighborhood():
    Mark exactly the specified strand indices as QUARANTINED.
    Strands outside the fault region are unaffected and continue executing.
    This enforces the "blast radius" property: a fault on strands k..k+r
    cannot propagate to strands at distance ≥ 2 from the faulted range.

halted_strands():
    Return the indices of all currently quarantined strands.
"""
from __future__ import annotations

from .state import StrandState, TrustLevel


def quarantine_neighborhood(
    fault_indices: list[int] | range,
    strands: list[StrandState],
) -> list[int]:
    """
    Quarantine exactly the strands identified by fault_indices.

    Each strand in fault_indices whose index is within [0, len(strands))
    has its trust_level set to TrustLevel.QUARANTINED.  All other strands
    are untouched.

    Parameters
    ----------
    fault_indices:
        The strand indices to quarantine.  May be a range or an explicit list.
    strands:
        The live strand list (mutated in place).

    Returns
    -------
    list[int]
        The indices that were actually quarantined (may be a subset of
        fault_indices if some indices were out of bounds).
    """
    quarantined: list[int] = []
    for idx in fault_indices:
        if 0 <= idx < len(strands):
            strands[idx].trust_level = TrustLevel.QUARANTINED
            quarantined.append(idx)
    return quarantined


def halted_strands(strands: list[StrandState]) -> list[int]:
    """
    Return the indices of every strand that is currently QUARANTINED.

    A quarantined strand is "halted" — it may not participate in further
    crossings until it is healed (RECOV.HEAL + re-verification).
    """
    return [i for i, strand in enumerate(strands) if strand.trust_level == TrustLevel.QUARANTINED]
