"""Regression tests for red-team findings 10 and 11 (SQLite persistence).

Finding 10 — the append-only claim must hold at the DATABASE level, not just
in the Python wrapper: direct UPDATE/DELETE attempts against the tables must
fail, and the rows must be unchanged afterwards.

Finding 11 — save_evidence_log must distinguish a genuine duplicate
(byte-identical content at the same sequence, safe to skip) from a
conflicting record (different content at the same sequence, an error) and
from any other integrity failure (which must propagate, not be swallowed).
"""

from __future__ import annotations

import sqlite3

import pytest

from braid_simulator.evidence import EvidenceLog, EvidenceRecord
from braid_simulator.persistence import PersistentEvidenceStore
from braid_simulator.state import StrandState


def make_record(tag: str) -> EvidenceRecord:
    return EvidenceRecord(tag, "INTEG", "VERIFY", 0, 0, 1, "in", "out", "PASS")


def _seed_store(store: PersistentEvidenceStore, braid_id: str = "s1") -> None:
    store.create_session(braid_id, [StrandState(value={"x": 1})])
    store.append_record(braid_id, 0, make_record("one"))


def _stored_tag(store: PersistentEvidenceStore, braid_id: str, seq: int) -> str | None:
    row = store._conn.execute(  # noqa: SLF001 - regression test reads the raw row
        "SELECT tag FROM evidence_records WHERE braid_id = ? AND sequence_number = ?",
        (braid_id, seq),
    ).fetchone()
    return row["tag"] if row is not None else None


# ---------------------------------------------------------------------------
# Finding 10 — database-level append-only triggers
# ---------------------------------------------------------------------------


def test_direct_update_on_evidence_records_is_refused() -> None:
    store = PersistentEvidenceStore(":memory:")
    _seed_store(store)
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        store._conn.execute(  # noqa: SLF001 - the test IS the bypass attempt
            "UPDATE evidence_records SET tag = 'tampered' "
            "WHERE braid_id = 's1' AND sequence_number = 0"
        )
    store._conn.rollback()
    assert _stored_tag(store, "s1", 0) == "one"
    assert store.record_count("s1") == 1
    store.close()


def test_direct_delete_on_evidence_records_is_refused() -> None:
    store = PersistentEvidenceStore(":memory:")
    _seed_store(store)
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        store._conn.execute(  # noqa: SLF001 - the test IS the bypass attempt
            "DELETE FROM evidence_records WHERE braid_id = 's1' AND sequence_number = 0"
        )
    store._conn.rollback()
    assert _stored_tag(store, "s1", 0) == "one"
    assert store.record_count("s1") == 1
    store.close()


def test_direct_update_and_delete_on_braid_sessions_are_refused() -> None:
    store = PersistentEvidenceStore(":memory:")
    _seed_store(store)
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        store._conn.execute(  # noqa: SLF001 - the test IS the bypass attempt
            "UPDATE braid_sessions SET initial_state = '[]' WHERE braid_id = 's1'"
        )
    store._conn.rollback()
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        store._conn.execute(  # noqa: SLF001 - the test IS the bypass attempt
            "DELETE FROM braid_sessions WHERE braid_id = 's1'"
        )
    store._conn.rollback()
    assert store.session_exists("s1")
    store.close()


def test_bypass_connection_cannot_rewrite_history(tmp_path) -> None:
    """A completely independent connection to the same file is also refused.

    This is the real bypass: a caller that never touches PersistentEvidenceStore
    at all, opening the database file directly.
    """
    db_path = tmp_path / "bct_run.db"
    store = PersistentEvidenceStore(db_path)
    _seed_store(store)

    rogue = sqlite3.connect(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            rogue.execute(
                "UPDATE evidence_records SET tag = 'tampered' "
                "WHERE braid_id = 's1' AND sequence_number = 0"
            )
        rogue.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            rogue.execute("DELETE FROM evidence_records WHERE braid_id = 's1'")
        rogue.rollback()
    finally:
        rogue.close()
    assert _stored_tag(store, "s1", 0) == "one"
    store.close()

    # Triggers survive a reopen: an existing database gains them on open.
    reopened = PersistentEvidenceStore(db_path)
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        reopened._conn.execute(  # noqa: SLF001 - the test IS the bypass attempt
            "DELETE FROM evidence_records WHERE braid_id = 's1'"
        )
    reopened._conn.rollback()
    assert reopened.record_count("s1") == 1
    reopened.close()


# ---------------------------------------------------------------------------
# Finding 11 — save_evidence_log distinguishes duplicates from conflicts
# ---------------------------------------------------------------------------


def test_save_genuine_duplicate_is_still_skipped() -> None:
    store = PersistentEvidenceStore(":memory:")
    store.create_session("s1", [StrandState(value={"x": 1})])
    log = EvidenceLog([make_record("one"), make_record("two")])
    store.save_evidence_log("s1", log)
    assert store.record_count("s1") == 2
    # Saving the byte-identical log again is a no-op, not an error.
    store.save_evidence_log("s1", log)
    assert store.record_count("s1") == 2
    assert _stored_tag(store, "s1", 0) == "one"
    assert _stored_tag(store, "s1", 1) == "two"
    store.close()


def test_save_conflicting_record_raises_and_keeps_stored_row() -> None:
    store = PersistentEvidenceStore(":memory:")
    store.create_session("s1", [StrandState(value={"x": 1})])
    store.save_evidence_log("s1", EvidenceLog([make_record("alpha")]))
    assert store.record_count("s1") == 1

    conflicting = EvidenceLog([make_record("BETA-DIFFERENT")])
    with pytest.raises(ValueError, match="conflicting evidence record"):
        store.save_evidence_log("s1", conflicting)
    # The stored row is untouched; the conflict was never silently skipped.
    assert _stored_tag(store, "s1", 0) == "alpha"
    assert store.record_count("s1") == 1
    store.close()


def test_save_non_duplicate_integrity_error_propagates() -> None:
    """An integrity failure with NO row at that sequence must propagate.

    Here a NOT NULL violation fires on a fresh sequence, so there is no
    duplicate to skip — the raw IntegrityError must reach the caller.
    """
    store = PersistentEvidenceStore(":memory:")
    store.create_session("s1", [StrandState(value={"x": 1})])
    bad = EvidenceRecord("bad", "INTEG", "VERIFY", 0, 0, 1, "in", "out", None)  # type: ignore[arg-type]
    with pytest.raises(sqlite3.IntegrityError):
        store.save_evidence_log("s1", EvidenceLog([bad]))
    assert store.record_count("s1") == 0
    store.close()
