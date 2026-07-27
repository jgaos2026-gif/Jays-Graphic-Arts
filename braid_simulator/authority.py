from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4


@dataclass(frozen=True)
class AuthorityToken:
    id: str
    role: str
    scope: tuple[str, ...]
    issued_at: str
    revoked: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "role": self.role,
            "scope": list(self.scope),
            "issued_at": self.issued_at,
            "revoked": self.revoked,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AuthorityToken":
        return cls(
            id=str(payload["id"]),
            role=str(payload["role"]),
            scope=tuple(payload.get("scope", [])),
            issued_at=str(payload["issued_at"]),
            revoked=bool(payload.get("revoked", False)),
        )


class AuthorityManager:
    def __init__(self) -> None:
        self._tokens: dict[str, AuthorityToken] = {}

    def issue_token(
        self,
        role: str,
        scope: Iterable[str],
        issued_at: str | None = None,
        token_id: str | None = None,
    ) -> AuthorityToken:
        token = AuthorityToken(
            id=token_id or str(uuid4()),
            role=role,
            scope=tuple(sorted(set(scope))),
            issued_at=issued_at or datetime.now(timezone.utc).isoformat(),
            revoked=False,
        )
        self._tokens[token.id] = token
        return token

    def register(self, token: AuthorityToken) -> AuthorityToken:
        self._tokens[token.id] = token
        return token

    def get_token(self, token_id: str) -> AuthorityToken | None:
        return self._tokens.get(token_id)

    def revoke_token(self, token_or_id: AuthorityToken | str) -> AuthorityToken:
        token_id = token_or_id.id if isinstance(token_or_id, AuthorityToken) else token_or_id
        token = self._tokens[token_id]
        revoked = AuthorityToken(
            id=token.id,
            role=token.role,
            scope=token.scope,
            issued_at=token.issued_at,
            revoked=True,
        )
        self._tokens[token_id] = revoked
        return revoked

    def check_scope(self, token: AuthorityToken | None, required_scope: str | Iterable[str]) -> bool:
        if token is None:
            return False
        # Look up the live registry entry so that post-issuance revocations are
        # visible even when callers hold a stale AuthorityToken snapshot.
        live = self._tokens.get(token.id)
        effective = live if live is not None else token
        if effective.revoked:
            return False
        required = {required_scope} if isinstance(required_scope, str) else set(required_scope)
        return required.issubset(set(effective.scope))

    def delegate_token(
        self,
        parent: AuthorityToken,
        scope: Iterable[str],
        role: str | None = None,
        issued_at: str | None = None,
        token_id: str | None = None,
    ) -> AuthorityToken:
        requested_scope = tuple(sorted(set(scope)))
        if not requested_scope:
            raise ValueError("delegated scope must not be empty")
        if not self.check_scope(parent, requested_scope):
            raise ValueError("delegated scope must be contained within parent scope")
        return self.issue_token(
            role=role or parent.role,
            scope=requested_scope,
            issued_at=issued_at,
            token_id=token_id,
        )
