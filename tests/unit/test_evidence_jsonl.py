"""Tests for EvidenceLog durable JSONL persistence (hash-chained, fail-closed)."""

import json

import pytest

from braid_simulator.evidence import (
    GENESIS_CHAIN_HASH,
    CorruptEvidenceLogError,
    EvidenceLog,
    EvidenceRecord,
)


def make_record(tag: str) -> EvidenceRecord:
    return EvidenceRecord(tag, "INTEG", "VERIFY", 0, 0, 1, "in", "out", "PASS")


def test_jsonl_round_trip_preserves_records_and_chain(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    for tag in ("one", "two", "three"):
        log.append(make_record(tag))
    head_before = log.chain_head
    log.save_jsonl(path)

    loaded = EvidenceLog.load_jsonl(path)
    assert [r.tag for r in loaded.records] == ["one", "two", "three"]
    assert loaded.chain_head == head_before
    assert loaded.path == path


def test_jsonl_append_after_load_continues_chain(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    log.append(make_record("one"))
    log.save_jsonl(path)

    loaded = EvidenceLog.load_jsonl(path)
    loaded.append(make_record("two"))

    reloaded = EvidenceLog.load_jsonl(path)
    assert [r.tag for r in reloaded.records] == ["one", "two"]
    assert reloaded.chain_head == loaded.chain_head


def test_jsonl_constructor_with_path_loads_and_appends(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    first = EvidenceLog(path=path)
    assert first.chain_head == GENESIS_CHAIN_HASH
    first.append(make_record("one"))

    second = EvidenceLog(path=path)
    assert [r.tag for r in second.records] == ["one"]
    second.append(make_record("two"))
    assert [r.tag for r in EvidenceLog.load_jsonl(path).records] == ["one", "two"]


def test_jsonl_memory_only_log_touches_no_disk(tmp_path) -> None:
    log = EvidenceLog()
    log.append(make_record("one"))
    assert log.path is None
    assert log.chain_head != GENESIS_CHAIN_HASH
    assert list(tmp_path.iterdir()) == []


def test_jsonl_tampered_record_is_refused(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    log.append(make_record("one"))
    log.append(make_record("two"))
    log.save_jsonl(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[1])
    tampered["record"]["tag"] = "forged"
    lines[1] = json.dumps(tampered)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(CorruptEvidenceLogError):
        EvidenceLog.load_jsonl(path)


def test_jsonl_tampered_chain_hash_is_refused(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    log.append(make_record("one"))
    log.save_jsonl(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[0])
    tampered["chain"] = "0" * 64
    lines[0] = json.dumps(tampered)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(CorruptEvidenceLogError):
        EvidenceLog.load_jsonl(path)


def test_jsonl_corrupt_line_is_refused(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    log.append(make_record("one"))
    log.save_jsonl(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("this is not json\n")

    with pytest.raises(CorruptEvidenceLogError):
        EvidenceLog.load_jsonl(path)


def test_jsonl_deleted_line_is_refused(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    for tag in ("one", "two", "three"):
        log.append(make_record(tag))
    log.save_jsonl(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="utf-8")

    with pytest.raises(CorruptEvidenceLogError):
        EvidenceLog.load_jsonl(path)


def test_jsonl_swapped_lines_are_refused(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    log.append(make_record("one"))
    log.append(make_record("two"))
    log.save_jsonl(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([lines[1], lines[0]]) + "\n", encoding="utf-8")

    with pytest.raises(CorruptEvidenceLogError):
        EvidenceLog.load_jsonl(path)


def test_jsonl_missing_file_is_refused(tmp_path) -> None:
    with pytest.raises(CorruptEvidenceLogError):
        EvidenceLog.load_jsonl(tmp_path / "does-not-exist.jsonl")


def test_jsonl_empty_log_round_trips(tmp_path) -> None:
    path = tmp_path / "evidence.jsonl"
    log = EvidenceLog()
    log.save_jsonl(path)
    loaded = EvidenceLog.load_jsonl(path)
    assert len(loaded) == 0
    assert loaded.chain_head == GENESIS_CHAIN_HASH
