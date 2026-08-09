"""
tests/unit/test_protection.py — quarantine_neighborhood / halted_strands

Covers all code paths in braid_simulator.protection:
  • Normal quarantine of a contiguous range.
  • Out-of-bounds indices are silently skipped.
  • Empty fault_indices does nothing.
  • halted_strands returns exactly the quarantined subset.
  • Re-quarantining an already-quarantined strand is idempotent.
  • Range objects work as well as lists.
"""
from __future__ import annotations

from braid_simulator import StrandState, TrustLevel, halted_strands, quarantine_neighborhood


def _strands(n: int) -> list[StrandState]:
    return [StrandState(value={"id": i}, trust_level=TrustLevel.ACTIVE) for i in range(n)]


class TestQuarantineNeighborhood:
    def test_quarantines_exactly_given_indices(self) -> None:
        strands = _strands(5)
        result = quarantine_neighborhood([1, 2, 3], strands)
        assert set(result) == {1, 2, 3}
        for i in [1, 2, 3]:
            assert strands[i].trust_level == TrustLevel.QUARANTINED
        for i in [0, 4]:
            assert strands[i].trust_level == TrustLevel.ACTIVE

    def test_out_of_bounds_indices_are_skipped(self) -> None:
        strands = _strands(3)
        result = quarantine_neighborhood([0, 5, 10], strands)
        assert result == [0]  # only index 0 is in bounds
        assert strands[0].trust_level == TrustLevel.QUARANTINED

    def test_empty_fault_indices_does_nothing(self) -> None:
        strands = _strands(4)
        result = quarantine_neighborhood([], strands)
        assert result == []
        assert all(s.trust_level == TrustLevel.ACTIVE for s in strands)

    def test_negative_index_skipped(self) -> None:
        strands = _strands(3)
        result = quarantine_neighborhood([-1, 0], strands)
        assert -1 not in result
        assert 0 in result

    def test_range_object_works(self) -> None:
        strands = _strands(6)
        result = quarantine_neighborhood(range(2, 5), strands)
        assert set(result) == {2, 3, 4}

    def test_all_strands_quarantined(self) -> None:
        strands = _strands(4)
        result = quarantine_neighborhood(range(4), strands)
        assert set(result) == {0, 1, 2, 3}
        assert all(s.trust_level == TrustLevel.QUARANTINED for s in strands)

    def test_idempotent_on_already_quarantined(self) -> None:
        strands = _strands(3)
        strands[1].trust_level = TrustLevel.QUARANTINED
        result = quarantine_neighborhood([1], strands)
        assert 1 in result
        assert strands[1].trust_level == TrustLevel.QUARANTINED

    def test_single_strand(self) -> None:
        strands = _strands(1)
        result = quarantine_neighborhood([0], strands)
        assert result == [0]
        assert strands[0].trust_level == TrustLevel.QUARANTINED


class TestHaltedStrands:
    def test_no_quarantined_returns_empty(self) -> None:
        strands = _strands(5)
        assert halted_strands(strands) == []

    def test_returns_quarantined_indices(self) -> None:
        strands = _strands(6)
        strands[2].trust_level = TrustLevel.QUARANTINED
        strands[4].trust_level = TrustLevel.QUARANTINED
        assert halted_strands(strands) == [2, 4]

    def test_returns_all_indices_when_all_quarantined(self) -> None:
        strands = _strands(3)
        for s in strands:
            s.trust_level = TrustLevel.QUARANTINED
        assert halted_strands(strands) == [0, 1, 2]

    def test_certified_is_not_halted(self) -> None:
        strands = _strands(2)
        strands[0].trust_level = TrustLevel.CERTIFIED
        assert halted_strands(strands) == []

    def test_trusted_is_not_halted(self) -> None:
        strands = _strands(2)
        strands[0].trust_level = TrustLevel.TRUSTED
        assert halted_strands(strands) == []

    def test_empty_strands_returns_empty(self) -> None:
        assert halted_strands([]) == []

    def test_consistent_with_quarantine_neighborhood(self) -> None:
        strands = _strands(8)
        quarantined = quarantine_neighborhood([3, 4, 5], strands)
        assert set(halted_strands(strands)) == set(quarantined)
