from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

from .authority import AuthorityToken
from .state import StrandState


#: Chain head for an empty JSONL log. The first record chains from GENESIS.
GENESIS_CHAIN_HASH = "GENESIS"


class CorruptEvidenceLogError(ValueError):
    """Raised when a persisted evidence log fails chain verification.

    A log that raises this error is refused entirely (fail closed): it is
    never loaded partially, and no record from it is trusted.
    """


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


def _chain_hash(prev_hash: str, record: dict[str, Any]) -> str:
    """Hash chaining one record onto the previous chain hash.

    The chain hash binds the record payload to the entire history before it:
    changing any earlier record changes every later chain hash.
    """
    return stable_hash({"prev": prev_hash, "record": record})


def _encode_line(seq: int, record: EvidenceRecord, prev_hash: str) -> tuple[str, str]:
    """Encode one record as a single JSONL line carrying its chain hash.

    Returns (line, chain_hash).
    """
    payload = record.to_dict()
    chain = _chain_hash(prev_hash, payload)
    line = stable_json(
        {
            "seq": seq,
            "record": payload,
            "prev": prev_hash,
            "chain": chain,
        }
    )
    return line, chain


def _decode_line(line: str, expected_seq: int, expected_prev: str) -> tuple[EvidenceRecord, str]:
    """Decode and verify one JSONL line.

    Raises CorruptEvidenceLogError on any problem: unparsable JSON, wrong
    shape, out-of-order sequence, broken prev linkage, or a chain hash that
    does not match the record payload. Fail closed — never return a record
    from a line that does not verify.
    """
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as exc:
        raise CorruptEvidenceLogError(f"line {expected_seq}: not valid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise CorruptEvidenceLogError(f"line {expected_seq}: line is not a JSON object")
    try:
        seq = obj["seq"]
        payload = obj["record"]
        prev = obj["prev"]
        chain = obj["chain"]
    except KeyError as exc:
        raise CorruptEvidenceLogError(f"line {expected_seq}: missing field {exc}") from exc
    if seq != expected_seq:
        raise CorruptEvidenceLogError(
            f"line {expected_seq}: sequence {seq!r} out of order (expected {expected_seq})"
        )
    if prev != expected_prev:
        raise CorruptEvidenceLogError(
            f"line {expected_seq}: prev hash does not match the chain head — log truncated or reordered"
        )
    if not isinstance(payload, dict) or not isinstance(chain, str):
        raise CorruptEvidenceLogError(f"line {expected_seq}: malformed record or chain hash")
    if chain != _chain_hash(prev, payload):
        raise CorruptEvidenceLogError(
            f"line {expected_seq}: chain hash mismatch — record tampered with"
        )
    try:
        return EvidenceRecord.from_dict(payload), chain
    except (TypeError, KeyError) as exc:
        raise CorruptEvidenceLogError(f"line {expected_seq}: invalid record fields ({exc})") from exc


class EvidenceLog:
    """Append-only evidence log.

    In memory the log is a plain list (unchanged API). For durability it can
    be attached to a JSONL file: every appended record is written to the file
    immediately, chained to the previous record by hash, and loading a file
    verifies the whole chain — a tampered or corrupt file is refused entirely
    (fail closed) instead of loading partially.
    """

    def __init__(
        self,
        records: Iterable[EvidenceRecord] | None = None,
        *,
        path: str | Path | None = None,
    ) -> None:
        self._records: list[EvidenceRecord] = []
        self._path: Path | None = None
        self._chain_head: str = GENESIS_CHAIN_HASH
        if path is not None:
            self._path = Path(path)
            if self._path.exists():
                loaded = EvidenceLog.load_jsonl(self._path)
                self._records = loaded._records
                self._chain_head = loaded._chain_head
        if records is not None:
            self.extend(records)

    @property
    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._records)

    @property
    def path(self) -> Path | None:
        """JSONL file this log is durably attached to, or None (memory only)."""
        return self._path

    @property
    def chain_head(self) -> str:
        """Hash chaining the full log history; GENESIS for an empty log."""
        return self._chain_head

    def append(self, record: EvidenceRecord) -> None:
        if not isinstance(record, EvidenceRecord):
            raise TypeError("evidence log accepts EvidenceRecord entries only")
        seq = len(self._records)
        line, chain = _encode_line(seq, record, self._chain_head)
        self._records.append(record)
        self._chain_head = chain
        if self._path is not None:
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

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

    # ------------------------------------------------------------------
    # Durable JSONL persistence (hash-chained, verified on load)
    # ------------------------------------------------------------------

    def save_jsonl(self, path: str | Path) -> None:
        """Write the whole log to a JSONL file (overwriting it) and attach.

        Each line carries the record, its sequence number, the previous chain
        hash, and the chain hash binding them. After saving, later appends
        are also written to this file.
        """
        target = Path(path)
        head = GENESIS_CHAIN_HASH
        lines = []
        for seq, record in enumerate(self._records):
            line, head = _encode_line(seq, record, head)
            lines.append(line)
        with target.open("w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        self._path = target
        self._chain_head = head

    @classmethod
    def load_jsonl(cls, path: str | Path) -> "EvidenceLog":
        """Load a JSONL evidence log, verifying the full hash chain.

        Raises CorruptEvidenceLogError (a ValueError) if any line is
        unparsable, out of order, unlinked, or tampered with. The log is
        refused entirely — never loaded partially. Returns a log attached
        to the file, so further appends persist to it.
        """
        target = Path(path)
        log = cls()
        head = GENESIS_CHAIN_HASH
        try:
            text = target.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise CorruptEvidenceLogError(f"evidence log file not found: {target}") from exc
        for expected_seq, line in enumerate(text.splitlines()):
            if not line.strip():
                raise CorruptEvidenceLogError(f"line {expected_seq}: blank line in log")
            record, head = _decode_line(line, expected_seq, head)
            log._records.append(record)
        log._chain_head = head
        log._path = target
        return log


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
