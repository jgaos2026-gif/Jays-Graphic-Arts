from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Iterable

from .authority import AuthorityToken
from .state import StrandState


@dataclass(frozen=True)
class EvidenceRecord:
    tag: str
    family: str
    opcode: str
    timestamp: int
    strand_i: int
    strand_j: int
    input_hash: str
    output_hash: str
    result: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceRecord":
        return cls(**payload)


class EvidenceLog:
    def __init__(self, records: Iterable[EvidenceRecord] | None = None) -> None:
        self._records: list[EvidenceRecord] = list(records or [])

    @property
    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._records)

    def append(self, record: EvidenceRecord) -> None:
        if not isinstance(record, EvidenceRecord):
            raise TypeError("evidence log accepts EvidenceRecord entries only")
        self._records.append(record)

    def extend(self, records: Iterable[EvidenceRecord]) -> None:
        for record in records:
            self.append(record)

    def clear(self) -> None:
        raise RuntimeError("EvidenceLog is append-only")

    def pop(self, index: int = -1) -> EvidenceRecord:
        raise RuntimeError("EvidenceLog is append-only")

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self):
        return iter(self._records)

    def __getitem__(self, index: int) -> EvidenceRecord:
        return self._records[index]

    def to_dicts(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records]

    @classmethod
    def from_dicts(cls, records: Iterable[dict[str, Any]]) -> "EvidenceLog":
        return cls(EvidenceRecord.from_dict(record) for record in records)


def canonicalize(value: Any) -> Any:
    if isinstance(value, StrandState):
        return value.to_dict()
    if isinstance(value, AuthorityToken):
        return value.to_dict()
    if isinstance(value, tuple):
        return [canonicalize(item) for item in value]
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonicalize(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    return value


def stable_json(value: Any) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return sha256(stable_json(value).encode("utf-8")).hexdigest()
