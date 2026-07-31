"""
braid_simulator/persistence.py — SQLite Evidence Log Persistence

Provides append-only, durable storage for BCT evidence logs backed by SQLite.

Design
------
Evidence logs are the source of truth in BCT (PO-4: Log Independence Invariant).
This module stores evidence records in a SQLite database so they survive process
restarts.  The schema enforces append-only semantics at the database level:

  • No UPDATE or DELETE is issued by this module.
  • The PRIMARY KEY on (braid_id, sequence_number) prevents duplicate inserts.
  • A row_id AUTOINCREMENT column provides insertion-order monotonicity.

Two helper classes are provided:

  PersistentEvidenceStore
      Wraps a SQLite connection and exposes load/save/append operations.
      Thread-safe via a per-instance threading.Lock.

  BraidSession
      A context-manager that ties an ExecutableBraid to a store, saving state
      before and after execution and providing a one-call replay_from_store()
      path (PO-3 recovery from persisted log).

Usage
-----
    from braid_simulator.persistence import PersistentEvidenceStore, BraidSession

    store = PersistentEvidenceStore("bct_run.db")
    with BraidSession("run-001", braid, executor, store) as session:
        result = session.execute()          # saves initial state + evidence
        replay = session.replay_from_store()  # verify_reverse from DB records
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .evidence import EvidenceLog, EvidenceRecord
from .execution import BraidExecutor, ExecutionResult
from .recovery import verify_reverse
from .state import StrandState


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS braid_sessions (
    braid_id        TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    initial_state   TEXT NOT NULL,
    PRIMARY KEY (braid_id)
);

CREATE TABLE IF NOT EXISTS evidence_records (
    row_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    braid_id        TEXT    NOT NULL,
    sequence_number INTEGER NOT NULL,
    tag             TEXT    NOT NULL,
    family          TEXT    NOT NULL,
    opcode          TEXT    NOT NULL,
    timestamp       INTEGER NOT NULL,
    strand_i        INTEGER NOT NULL,
    strand_j        INTEGER NOT NULL,
    input_hash      TEXT    NOT NULL,
    output_hash     TEXT    NOT NULL,
    result          TEXT    NOT NULL,
    UNIQUE (braid_id, sequence_number),
    FOREIGN KEY (braid_id) REFERENCES braid_sessions(braid_id)
);

CREATE INDEX IF NOT EXISTS idx_evidence_braid ON evidence_records(braid_id, sequence_number);
"""


# ---------------------------------------------------------------------------
# PersistentEvidenceStore
# ---------------------------------------------------------------------------

class PersistentEvidenceStore:
    """
    Append-only SQLite store for BCT evidence logs.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Use ``":memory:"`` for an in-memory
        database (useful for tests).
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._conn:
            self._conn.executescript(_SCHEMA_SQL)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def create_session(self, braid_id: str, initial_strands: list[StrandState]) -> None:
        """
        Register a new braid session with its initial strand state.

        Raises ValueError if the braid_id is already registered (sessions are
        immutable once created — re-execution requires a new braid_id).
        """
        state_json = json.dumps(
            [s.to_dict() for s in initial_strands],
            sort_keys=True,
            separators=(",", ":"),
        )
        with self._lock, self._conn:
            try:
                self._conn.execute(
                    "INSERT INTO braid_sessions (braid_id, initial_state) VALUES (?, ?)",
                    (braid_id, state_json),
                )
            except sqlite3.IntegrityError:
                raise ValueError(f"braid session already exists: {braid_id!r}")

    def session_exists(self, braid_id: str) -> bool:
        """Return True if a session record exists for braid_id."""
        with self._lock:
            row = self._conn.execute(
                "SELECT 1 FROM braid_sessions WHERE braid_id = ?", (braid_id,)
            ).fetchone()
            return row is not None

    def load_initial_strands(self, braid_id: str) -> list[StrandState]:
        """Retrieve the initial strand state saved for braid_id."""
        with self._lock:
            row = self._conn.execute(
                "SELECT initial_state FROM braid_sessions WHERE braid_id = ?",
                (braid_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"no session found: {braid_id!r}")
        return [StrandState.from_dict(d) for d in json.loads(row["initial_state"])]

    # ------------------------------------------------------------------
    # Evidence record operations
    # ------------------------------------------------------------------

    def append_record(self, braid_id: str, sequence_number: int, record: EvidenceRecord) -> None:
        """
        Append a single evidence record.

        Raises sqlite3.IntegrityError if (braid_id, sequence_number) already exists,
        enforcing append-only semantics at the database level.
        """
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO evidence_records
                    (braid_id, sequence_number, tag, family, opcode, timestamp,
                     strand_i, strand_j, input_hash, output_hash, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    braid_id,
                    sequence_number,
                    record.tag,
                    record.family,
                    record.opcode,
                    record.timestamp,
                    record.strand_i,
                    record.strand_j,
                    record.input_hash,
                    record.output_hash,
                    record.result,
                ),
            )

    def save_evidence_log(self, braid_id: str, log: EvidenceLog) -> None:
        """Persist all records in log to the store (idempotent — skips existing rows)."""
        for seq, record in enumerate(log):
            try:
                self.append_record(braid_id, seq, record)
            except sqlite3.IntegrityError:
                # Record already persisted — append-only constraint satisfied.
                pass

    def load_evidence_log(self, braid_id: str) -> EvidenceLog:
        """Load all evidence records for braid_id in sequence order."""
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT tag, family, opcode, timestamp, strand_i, strand_j,
                       input_hash, output_hash, result
                FROM evidence_records
                WHERE braid_id = ?
                ORDER BY sequence_number ASC
                """,
                (braid_id,),
            ).fetchall()
        records = [
            EvidenceRecord(
                tag=row["tag"],
                family=row["family"],
                opcode=row["opcode"],
                timestamp=row["timestamp"],
                strand_i=row["strand_i"],
                strand_j=row["strand_j"],
                input_hash=row["input_hash"],
                output_hash=row["output_hash"],
                result=row["result"],
            )
            for row in rows
        ]
        return EvidenceLog(records)

    def record_count(self, braid_id: str) -> int:
        """Return the number of evidence records stored for braid_id."""
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS cnt FROM evidence_records WHERE braid_id = ?",
                (braid_id,),
            ).fetchone()
            return row["cnt"] if row else 0

    def list_sessions(self) -> list[dict[str, Any]]:
        """Return summary dicts for all sessions in the store."""
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT s.braid_id, s.created_at,
                       COUNT(e.row_id) AS evidence_count
                FROM braid_sessions s
                LEFT JOIN evidence_records e ON s.braid_id = e.braid_id
                GROUP BY s.braid_id, s.created_at
                ORDER BY s.created_at ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def __enter__(self) -> "PersistentEvidenceStore":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# BraidSession
# ---------------------------------------------------------------------------

class BraidSession:
    """
    Context manager that ties an ExecutableBraid to a PersistentEvidenceStore.

    On execute():
      1. Saves the initial strand state to the store (create_session).
      2. Runs the braid via the executor.
      3. Persists all evidence records (save_evidence_log).
      4. Returns the ExecutionResult.

    On replay_from_store():
      1. Loads the initial state from the store.
      2. Loads the evidence log from the store.
      3. Calls verify_reverse against the stored log and initial state.
      4. Returns (verified: bool, terminal_strands: list[StrandState]).

    Parameters
    ----------
    braid_id:
        Unique identifier for this session.  Must be unique within the store.
    braid:
        The ExecutableBraid to execute.
    executor:
        The BraidExecutor to use for execution and replay.
    store:
        The PersistentEvidenceStore to save/load records from.
    """

    def __init__(
        self,
        braid_id: str,
        braid: Any,
        executor: BraidExecutor,
        store: PersistentEvidenceStore,
    ) -> None:
        self.braid_id = braid_id
        self._braid = braid
        self._executor = executor
        self._store = store
        self._initial_strands: list[StrandState] = [s.clone() for s in braid.strands]
        self._result: ExecutionResult | None = None

    def execute(self) -> ExecutionResult:
        """Execute the braid and persist the evidence log."""
        self._store.create_session(self.braid_id, self._initial_strands)
        self._result = self._braid.execute(self._executor)
        self._store.save_evidence_log(self.braid_id, self._result.evidence_log)
        return self._result

    def replay_from_store(self) -> tuple[bool, list[StrandState]]:
        """
        Independently verify the persisted log against the stored initial state.

        Equivalent to PO-3: the evidence log is the source of truth.
        A True result means the log is internally consistent with the initial
        state that was recorded at session creation time.
        """
        stored_initial = self._store.load_initial_strands(self.braid_id)
        stored_log = self._store.load_evidence_log(self.braid_id)
        return verify_reverse(list(stored_log.records), stored_initial)

    def __enter__(self) -> "BraidSession":
        return self

    def __exit__(self, *args: object) -> None:
        pass
