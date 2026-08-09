from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .authority import AuthorityToken


class TrustLevel(str, Enum):
    ACTIVE = "ACTIVE"
    TRUSTED = "TRUSTED"
    CERTIFIED = "CERTIFIED"
    QUARANTINED = "QUARANTINED"


@dataclass
class StrandState:
    value: Any
    trust_level: TrustLevel = TrustLevel.ACTIVE
    authority_token: AuthorityToken | None = None
    history: list[str] = field(default_factory=list)

    def clone(self) -> "StrandState":
        return StrandState(
            value=deepcopy(self.value),
            trust_level=self.trust_level,
            authority_token=self.authority_token,
            history=list(self.history),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": deepcopy(self.value),
            "trust_level": self.trust_level.value,
            "authority_token": self.authority_token.to_dict() if self.authority_token else None,
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StrandState":
        token_payload = payload.get("authority_token")
        return cls(
            value=deepcopy(payload.get("value")),
            trust_level=TrustLevel(payload.get("trust_level", TrustLevel.ACTIVE.value)),
            authority_token=AuthorityToken.from_dict(token_payload) if token_payload else None,
            history=list(payload.get("history", [])),
        )
