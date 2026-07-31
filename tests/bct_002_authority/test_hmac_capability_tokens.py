"""
BCT-002 Authority — HMAC Capability Token Lifecycle Suite

Verifies that AuthorityToken objects behave as unforgeable, HMAC-authenticated
capability tokens:
  • Tokens are issued with a deterministic scope tuple.
  • A token's HMAC signature over its canonical serialisation is stable and
    verifiable with the correct key; the wrong key produces a different digest.
  • Revoked tokens fail every scope check immediately — there is no window
    between revocation and enforcement.
  • A token cannot silently broaden its own scope (no privilege escalation).
"""
from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from braid_simulator import AuthorityManager, AuthorityToken


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HMAC_KEY = b"bct_002_capability_key_v1"


def _token_hmac(token: AuthorityToken, key: bytes = _HMAC_KEY) -> str:
    """Compute an HMAC-SHA256 over the token's canonical JSON payload."""
    payload = json.dumps(token.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def _verify_token_hmac(token: AuthorityToken, signature: str, key: bytes = _HMAC_KEY) -> bool:
    expected = _token_hmac(token, key)
    return hmac.compare_digest(signature, expected)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_issued_token_has_deterministic_sorted_scope() -> None:
    """Token scope is always stored as a sorted tuple — no ordering ambiguity."""
    manager = AuthorityManager()
    token = manager.issue_token(
        role="EXECUTOR",
        scope=["store", "execute", "verify"],
        token_id="scope_order_test",
    )

    assert token.scope == ("execute", "store", "verify"), (
        f"Token scope is not sorted: {token.scope!r}. "
        "Scope must be a sorted tuple to enable deterministic HMAC computation."
    )


def test_token_hmac_is_stable_and_verifiable() -> None:
    """The HMAC over a token's canonical JSON payload is reproducible and verifiable."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="hmac_test")

    sig1 = _token_hmac(token)
    sig2 = _token_hmac(token)

    assert sig1 == sig2, "HMAC is not deterministic for the same token."
    assert _verify_token_hmac(token, sig1), "HMAC verification failed with correct key."


def test_wrong_key_fails_hmac_verification() -> None:
    """HMAC computed with the wrong key must not verify under the correct key."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="wrong_key_test")

    bad_sig = _token_hmac(token, key=b"attacker_key")
    assert not _verify_token_hmac(token, bad_sig, key=_HMAC_KEY), (
        "HMAC computed with wrong key incorrectly verified under the correct key — "
        "capability token forgery is possible."
    )


def test_tampered_token_payload_fails_hmac_verification() -> None:
    """Altering any field of the token payload invalidates its HMAC signature."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="tamper_test")
    sig = _token_hmac(token)

    # Simulate an adversary promoting their own role.
    elevated = AuthorityToken(
        id=token.id,
        role="ROOT",            # escalated role
        scope=token.scope,
        issued_at=token.issued_at,
        revoked=False,
    )

    assert not _verify_token_hmac(elevated, sig), (
        "A token whose role was changed still passes HMAC verification — "
        "role escalation attack is undetected."
    )


def test_tampered_scope_fails_hmac_verification() -> None:
    """Expanding the scope of an existing token invalidates its HMAC signature."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="scope_tamper")
    sig = _token_hmac(token)

    expanded = AuthorityToken(
        id=token.id,
        role=token.role,
        scope=("execute", "store", "verify"),   # illegally expanded
        issued_at=token.issued_at,
        revoked=False,
    )

    assert not _verify_token_hmac(expanded, sig), (
        "A token with an expanded scope still passes HMAC verification — "
        "scope escalation attack is undetected."
    )


def test_revoked_token_immediately_fails_all_scope_checks() -> None:
    """Revocation is immediate: a revoked token passes no scope check."""
    manager = AuthorityManager()
    token = manager.issue_token(
        role="EXECUTOR",
        scope=["execute", "store", "verify"],
        token_id="revoke_test",
    )

    assert manager.check_scope(token, "execute"), "Token should pass before revocation."

    revoked = manager.revoke_token(token)

    for scope in ("execute", "store", "verify", "root", "anything"):
        assert not manager.check_scope(revoked, scope), (
            f"Revoked token still passes scope check for {scope!r}. "
            "Revocation must be immediate and total."
        )


def test_revoked_token_hmac_detects_un_revocation_attempt() -> None:
    """
    An attacker who takes a revoked token, flips revoked=False, and presents it
    must be detected: the HMAC over the mutated payload will not match.
    """
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="unrevoke_test")
    revoked = manager.revoke_token(token)
    sig_revoked = _token_hmac(revoked)

    # Attacker flips the revoked flag back to False.
    un_revoked = AuthorityToken(
        id=revoked.id,
        role=revoked.role,
        scope=revoked.scope,
        issued_at=revoked.issued_at,
        revoked=False,           # attacker's mutation
    )

    assert not _verify_token_hmac(un_revoked, sig_revoked), (
        "An un-revocation attempt (flipping revoked=False) passed HMAC verification — "
        "the revoked status is not integrity-protected."
    )


def test_token_scope_cannot_exceed_parent_at_delegation() -> None:
    """Delegated scope must be a subset of the parent's scope — no privilege widening."""
    manager = AuthorityManager()
    parent = manager.issue_token(
        role="ROOT",
        scope=["execute", "verify"],
        token_id="parent_scope_test",
    )

    with pytest.raises(ValueError, match="delegated scope must be contained"):
        manager.delegate_token(parent, scope=["execute", "store"])  # 'store' not in parent


def test_check_scope_requires_all_listed_scopes() -> None:
    """check_scope must require ALL listed scopes — not just any one of them."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="multi_scope")

    assert manager.check_scope(token, "execute"), "Single-scope check must pass."
    assert not manager.check_scope(token, ["execute", "store"]), (
        "check_scope returned True for ['execute', 'store'] but token only has 'execute'. "
        "Partial-scope match must not be accepted."
    )
