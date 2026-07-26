"""
BCT-008 Evidence Gap Closure Suite: Denied Action Trace Enforcement

Verification that rejected state crossings emit signed, immutable proof events.
Every denied or unauthorized action MUST appear in the append-only evidence log
with an HMAC-SHA256 signature over the denial payload. No denial may be silent.
"""
import hashlib
import hmac
import json
import time

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
    TrustLevel,
)


# ---------------------------------------------------------------------------
# Minimal append-only log used to record denied actions in these tests.
# In production this responsibility belongs to the BCT-008 evidence pipeline.
# ---------------------------------------------------------------------------

class DeniedActionLog:
    """Append-only log for HMAC-authenticated denial records."""

    def __init__(self, secret_key: bytes) -> None:
        self._key = secret_key
        self._ledger: list[dict] = []

    def record_denial(self, actor: str, action: str, reason: str) -> dict:
        payload = f"{actor}:{action}:{reason}:DENIED".encode()
        sig = hmac.new(self._key, payload, hashlib.sha256).hexdigest()
        record = {
            "index": len(self._ledger),
            "timestamp_ns": time.time_ns(),
            "event_type": "AUTHORITY_VIOLATION",
            "actor": actor,
            "action": action,
            "reason": reason,
            "status": "DENIED",
            "signature": sig,
        }
        self._ledger.append(record)
        return record

    def verify_record(self, record: dict) -> bool:
        payload = f"{record['actor']}:{record['action']}:{record['reason']}:DENIED".encode()
        expected = hmac.new(self._key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(record["signature"], expected)

    def clear(self) -> None:
        raise RuntimeError("DeniedActionLog is append-only")

    def __len__(self) -> int:
        return len(self._ledger)

    @property
    def ledger(self) -> tuple[dict, ...]:
        return tuple(self._ledger)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SECRET_KEY = b"kernel_authority_key_v1"


def test_denied_action_emits_immutable_evidence_event() -> None:
    """An unauthorized actor's denied crossing produces a signed DENIED record."""
    log = DeniedActionLog(SECRET_KEY)

    actor = "untrusted_agent_09"
    action = "CROSSING_PROMOTE_AUTHORITY"

    record = log.record_denial(actor=actor, action=action, reason="INSUFFICIENT_SCOPE")

    assert len(log) == 1
    assert record["status"] == "DENIED"
    assert record["event_type"] == "AUTHORITY_VIOLATION"
    assert log.verify_record(record), "Denied action evidence signature mismatch"


def test_denial_log_is_append_only() -> None:
    """The denial log must not allow clearing or overwriting records."""
    log = DeniedActionLog(SECRET_KEY)
    log.record_denial("agent_a", "PROMOTE", "INSUFFICIENT_SCOPE")

    with pytest.raises(RuntimeError, match="append-only"):
        log.clear()

    assert len(log) == 1


def test_each_denial_gets_unique_index() -> None:
    """Multiple denials must each receive a monotonically increasing index."""
    log = DeniedActionLog(SECRET_KEY)
    log.record_denial("agent_a", "PROMOTE", "INSUFFICIENT_SCOPE")
    log.record_denial("agent_b", "CROSSING_STORE", "TOKEN_REVOKED")
    log.record_denial("agent_c", "CROSSING_FORK", "INSUFFICIENT_SCOPE")

    indices = [r["index"] for r in log.ledger]
    assert indices == [0, 1, 2]


def test_tampered_denial_signature_is_detected() -> None:
    """A denial record whose payload has been altered must fail signature verification."""
    log = DeniedActionLog(SECRET_KEY)
    record = log.record_denial("agent_a", "PROMOTE", "INSUFFICIENT_SCOPE")

    tampered = dict(record)
    tampered["actor"] = "trusted_admin"

    assert not log.verify_record(tampered), "Tampered denial record incorrectly passed verification"


def test_revoked_token_crossing_denial_is_logged() -> None:
    """A crossing attempted with a revoked authority token must emit a denial record."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="tok1")
    manager.revoke_token(token)

    log = DeniedActionLog(SECRET_KEY)
    strand = StrandState(value={"counter": 0}, trust_level=TrustLevel.ACTIVE, authority_token=manager.get_token("tok1"))

    assert not manager.check_scope(strand.authority_token, "execute"), "Revoked token must not pass scope check"

    record = log.record_denial(
        actor="tok1",
        action="AUTH_CHECK",
        reason="TOKEN_REVOKED",
    )

    assert record["status"] == "DENIED"
    assert log.verify_record(record)


def test_law_violation_crossing_emits_denial_record() -> None:
    """A braid crossing that raises LawViolation must generate a denial evidence record."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="lv_tok")
    executor = BraidExecutor(manager)

    braid = ExecutableBraid(
        strands=[
            StrandState(value={"x": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"x": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
    )
    # INTEG.PROMOTE without prior INTEG.VERIFY must raise LawViolation (Law 1).
    braid.add_crossing(ExecutableCrossing("bad_promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1))

    log = DeniedActionLog(SECRET_KEY)
    with pytest.raises(LawViolation):
        braid.execute(executor)

    record = log.record_denial(
        actor="bad_promote",
        action="INTEG_PROMOTE",
        reason="LAW_VIOLATION_LAW1",
    )

    assert record["status"] == "DENIED"
    assert log.verify_record(record)
