from braid_simulator.evidence import EvidenceLog, EvidenceRecord


def test_evidence_log_length_monotonically_increases() -> None:
    log = EvidenceLog()
    lengths = []
    for index in range(8):
        log.append(EvidenceRecord(f"tag-{index}", "MEM", "STORE_HOT", index, 0, 1, str(index), str(index + 1), "PASS"))
        lengths.append(len(log))

    assert lengths == sorted(lengths)
    assert all(left < right for left, right in zip(lengths, lengths[1:]))
