from braid_simulator import AuthorityManager


def test_authority_token_issue_delegate_and_revoke() -> None:
    manager = AuthorityManager()
    root = manager.issue_token(role="ROOT", scope=["execute", "verify", "store"], token_id="root")
    child = manager.delegate_token(root, scope=["execute"], role="EXECUTOR", token_id="child")

    assert manager.check_scope(root, "verify")
    assert manager.check_scope(child, "execute")
    assert not manager.check_scope(child, "store")

    revoked = manager.revoke_token(child)
    assert revoked.revoked is True
    assert not manager.check_scope(revoked, "execute")
