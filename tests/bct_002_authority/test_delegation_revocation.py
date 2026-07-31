"""
BCT-002 Authority — Token Delegation and Revocation Suite

Verifies the full delegation and revocation lifecycle:
  • Delegated tokens inherit at most the parent scope.
  • Multi-level delegation chains enforce scope narrowing at every step.
  • Revoking a parent does NOT automatically revoke children (each token's
    revoked flag is independent); the caller must track the chain.
  • A delegated token's HMAC signature is distinct from its parent's.
  • An already-revoked token cannot be re-delegated.
"""
from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from braid_simulator import AuthorityManager, AuthorityToken


_HMAC_KEY = b"bct_002_delegation_key_v1"


def _token_hmac(token: AuthorityToken) -> str:
    payload = json.dumps(token.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(_HMAC_KEY, payload, hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_delegated_token_scope_is_subset_of_parent() -> None:
    """A delegated token holds at most the scope the parent carries."""
    manager = AuthorityManager()
    root = manager.issue_token(role="ROOT", scope=["execute", "store", "verify"], token_id="root")
    child = manager.delegate_token(root, scope=["execute"], role="WORKER", token_id="child")

    assert manager.check_scope(child, "execute"), "Delegated 'execute' must pass."
    assert not manager.check_scope(child, "store"), (
        "Child has 'store' scope but parent did not delegate it."
    )
    assert not manager.check_scope(child, "verify"), (
        "Child has 'verify' scope but parent did not delegate it."
    )


def test_three_level_delegation_chain_narrows_scope() -> None:
    """Each delegation step can only narrow scope — never widen it."""
    manager = AuthorityManager()
    root   = manager.issue_token(role="ROOT",      scope=["execute", "store", "verify"])
    mid    = manager.delegate_token(root,   scope=["execute", "store"], role="MID")
    leaf   = manager.delegate_token(mid,    scope=["execute"],          role="LEAF")

    assert manager.check_scope(root, ["execute", "store", "verify"])
    assert manager.check_scope(mid,  ["execute", "store"])
    assert not manager.check_scope(mid,  "verify")
    assert manager.check_scope(leaf, "execute")
    assert not manager.check_scope(leaf, "store")
    assert not manager.check_scope(leaf, "verify")


def test_cannot_delegate_from_revoked_parent() -> None:
    """Delegating from a revoked token must raise ValueError."""
    manager = AuthorityManager()
    token = manager.issue_token(role="ROOT", scope=["execute"])
    revoked = manager.revoke_token(token)

    with pytest.raises(ValueError):
        manager.delegate_token(revoked, scope=["execute"])


def test_revoking_parent_does_not_auto_revoke_child() -> None:
    """
    Parent and child tokens are independent objects.  Revoking the parent does
    not automatically flip the child's revoked flag — the system enforces this
    via the manager's token registry, not via reference mutation.
    """
    manager = AuthorityManager()
    parent = manager.issue_token(role="ROOT", scope=["execute"], token_id="par")
    child  = manager.delegate_token(parent, scope=["execute"], role="CHILD", token_id="chi")

    manager.revoke_token(parent)

    # The child's revoked flag in the registry is still False.
    child_in_registry = manager.get_token("chi")
    assert child_in_registry is not None
    assert child_in_registry.revoked is False, (
        "Revoking the parent automatically revoked the child. "
        "Tokens are independent objects; the caller owns chain-revocation logic."
    )

    # The manager still lets the child pass scope checks (by design).
    assert manager.check_scope(child_in_registry, "execute"), (
        "Child token fails scope check after parent was revoked. "
        "Independent tokens must be revoked independently."
    )


def test_delegated_token_hmac_differs_from_parent() -> None:
    """A delegated token must have a different HMAC from its parent."""
    manager = AuthorityManager()
    parent = manager.issue_token(role="ROOT", scope=["execute", "verify"], token_id="par_hmac")
    child  = manager.delegate_token(parent, scope=["execute"], role="CHILD", token_id="chi_hmac")

    assert _token_hmac(parent) != _token_hmac(child), (
        "Parent and child tokens have the same HMAC — their canonical payloads "
        "are identical, which means scope restriction had no effect on the payload."
    )


def test_revoke_removes_token_from_active_scope() -> None:
    """After revocation the manager's registry returns the revoked flag as True."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="revoke_registry")
    manager.revoke_token(token)

    stored = manager.get_token("revoke_registry")
    assert stored is not None
    assert stored.revoked is True, (
        f"Token in registry has revoked=False after revoke_token() was called: {stored!r}"
    )
    assert not manager.check_scope(stored, "execute"), (
        "Revoked token in registry still passes scope check."
    )


def test_delegation_with_empty_scope_raises() -> None:
    """Attempting to delegate an empty scope must raise (no zero-scope tokens)."""
    manager = AuthorityManager()
    token = manager.issue_token(role="ROOT", scope=["execute"])

    with pytest.raises((ValueError, Exception)):
        manager.delegate_token(token, scope=[])
