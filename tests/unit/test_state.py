"""
tests/unit/test_state.py — StrandState Unit Tests

Covers StrandState serialization, deserialization, cloning, and
trust-level enum behavior.
"""
from __future__ import annotations

import pytest

from braid_simulator import AuthorityManager, StrandState, TrustLevel


class TestTrustLevel:
    def test_all_values_defined(self) -> None:
        assert {TrustLevel.ACTIVE, TrustLevel.TRUSTED, TrustLevel.CERTIFIED, TrustLevel.QUARANTINED}

    def test_values_are_strings(self) -> None:
        for level in TrustLevel:
            assert isinstance(level.value, str)

    def test_enum_from_string(self) -> None:
        assert TrustLevel("ACTIVE") == TrustLevel.ACTIVE
        assert TrustLevel("QUARANTINED") == TrustLevel.QUARANTINED

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            TrustLevel("UNKNOWN")


class TestStrandState:
    def _make_token(self):
        m = AuthorityManager()
        return m.issue_token(role="TEST", scope=["execute"], token_id="tok-state-test")

    def test_default_trust_level_is_active(self) -> None:
        s = StrandState(value=42)
        assert s.trust_level == TrustLevel.ACTIVE

    def test_default_history_is_empty(self) -> None:
        s = StrandState(value={"x": 1})
        assert s.history == []

    def test_clone_is_deep_copy(self) -> None:
        original = StrandState(value={"counter": 1}, history=["step-a"])
        cloned = original.clone()
        cloned.value["counter"] = 99
        cloned.history.append("step-b")
        assert original.value["counter"] == 1
        assert "step-b" not in original.history

    def test_clone_preserves_trust_level(self) -> None:
        s = StrandState(value=None, trust_level=TrustLevel.TRUSTED)
        assert s.clone().trust_level == TrustLevel.TRUSTED

    def test_clone_preserves_authority_token(self) -> None:
        token = self._make_token()
        s = StrandState(value=None, authority_token=token)
        assert s.clone().authority_token == token

    def test_to_dict_round_trips(self) -> None:
        token = self._make_token()
        s = StrandState(
            value={"payload": "data"},
            trust_level=TrustLevel.CERTIFIED,
            authority_token=token,
            history=["a", "b"],
        )
        d = s.to_dict()
        restored = StrandState.from_dict(d)
        assert restored.value == s.value
        assert restored.trust_level == s.trust_level
        assert restored.history == s.history
        assert restored.authority_token is not None
        assert restored.authority_token.id == token.id

    def test_to_dict_without_token(self) -> None:
        s = StrandState(value=None)
        d = s.to_dict()
        assert d["authority_token"] is None

    def test_from_dict_without_token(self) -> None:
        d = {"value": 42, "trust_level": "ACTIVE", "authority_token": None, "history": []}
        s = StrandState.from_dict(d)
        assert s.value == 42
        assert s.authority_token is None

    def test_quarantined_trust_level_survives_roundtrip(self) -> None:
        s = StrandState(value=None, trust_level=TrustLevel.QUARANTINED)
        d = s.to_dict()
        s2 = StrandState.from_dict(d)
        assert s2.trust_level == TrustLevel.QUARANTINED

    def test_value_can_be_none(self) -> None:
        s = StrandState(value=None)
        assert s.to_dict()["value"] is None

    def test_value_can_be_list(self) -> None:
        s = StrandState(value=[1, 2, 3])
        d = s.to_dict()
        assert d["value"] == [1, 2, 3]

    def test_clone_does_not_share_list_value(self) -> None:
        s = StrandState(value=[1, 2, 3])
        c = s.clone()
        c.value.append(4)
        assert s.value == [1, 2, 3]
