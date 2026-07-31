from braid_simulator.evidence import EvidenceLog, EvidenceRecord


def make_record(tag: str) -> EvidenceRecord:
    return EvidenceRecord(tag, "INTEG", "VERIFY", 0, 0, 1, "in", "out", "PASS")


def test_evidence_log_is_append_only() -> None:
    log = EvidenceLog()
    log.append(make_record("one"))
    log.append(make_record("two"))

    assert len(log) == 2
    assert tuple(record.tag for record in log.records) == ("one", "two")

    try:
        log.clear()
    except RuntimeError as exc:
        assert "append-only" in str(exc)
    else:
        raise AssertionError("clear() should fail on append-only evidence")
