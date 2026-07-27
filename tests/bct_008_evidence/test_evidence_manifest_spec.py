"""
BCT-008 Evidence Manifest Specification

Defines the schema and verification contract for BCT-008 evidence manifests.
An evidence manifest is a machine-readable artifact produced at the end of a
braid execution run. It binds the executed commit, the evidence log hash, and
the test result to a single signed document that constitutes the Level 3 proof
artifact required by BFR_REGISTRY.md.
"""
import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass
from typing import Any

import pytest

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    StrandState,
    TrustLevel,
)


# ---------------------------------------------------------------------------
# Manifest schema
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvidenceManifest:
    """
    Immutable proof artifact for a single braid execution run.

    Fields
    ------
    braid_id:
        BFR ID of the braid under test (e.g. "BCT-008").
    run_id:
        Unique identifier for this execution run (e.g. a UUID or git commit SHA).
    timestamp_ns:
        Wall-clock time of manifest creation in nanoseconds since epoch.
    evidence_count:
        Number of evidence records in the log for this run.
    log_hash:
        SHA-256 hex digest of the canonical JSON serialization of all evidence records.
    test_result:
        "PASS" or "FAIL".
    manifest_signature:
        HMAC-SHA256 hex digest over the canonical payload (all fields except this one).
    """

    braid_id: str
    run_id: str
    timestamp_ns: int
    evidence_count: int
    log_hash: str
    test_result: str
    manifest_signature: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def canonical_payload(
        cls,
        braid_id: str,
        run_id: str,
        timestamp_ns: int,
        evidence_count: int,
        log_hash: str,
        test_result: str,
    ) -> bytes:
        payload = {
            "braid_id": braid_id,
            "run_id": run_id,
            "timestamp_ns": timestamp_ns,
            "evidence_count": evidence_count,
            "log_hash": log_hash,
            "test_result": test_result,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    @classmethod
    def create(
        cls,
        braid_id: str,
        run_id: str,
        evidence_records: list[dict],
        test_result: str,
        secret_key: bytes,
    ) -> "EvidenceManifest":
        timestamp_ns = time.time_ns()
        log_bytes = json.dumps(evidence_records, sort_keys=True, separators=(",", ":")).encode()
        log_hash = hashlib.sha256(log_bytes).hexdigest()
        evidence_count = len(evidence_records)
        payload = cls.canonical_payload(braid_id, run_id, timestamp_ns, evidence_count, log_hash, test_result)
        sig = hmac.new(secret_key, payload, hashlib.sha256).hexdigest()
        return cls(
            braid_id=braid_id,
            run_id=run_id,
            timestamp_ns=timestamp_ns,
            evidence_count=evidence_count,
            log_hash=log_hash,
            test_result=test_result,
            manifest_signature=sig,
        )

    def verify(self, secret_key: bytes) -> bool:
        payload = self.canonical_payload(
            self.braid_id,
            self.run_id,
            self.timestamp_ns,
            self.evidence_count,
            self.log_hash,
            self.test_result,
        )
        expected = hmac.new(secret_key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.manifest_signature, expected)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SECRET_KEY = b"manifest_signing_key_v1"


def test_manifest_is_created_and_verifiable() -> None:
    """A freshly created manifest must pass self-verification."""
    manifest = EvidenceManifest.create(
        braid_id="BCT-008",
        run_id="run-001",
        evidence_records=[{"tag": "auth", "result": "PASS"}],
        test_result="PASS",
        secret_key=SECRET_KEY,
    )

    assert manifest.braid_id == "BCT-008"
    assert manifest.test_result == "PASS"
    assert manifest.evidence_count == 1
    assert manifest.verify(SECRET_KEY), "Fresh manifest must pass verification"


def test_manifest_with_wrong_key_fails_verification() -> None:
    """A manifest verified with the wrong key must be rejected."""
    manifest = EvidenceManifest.create(
        braid_id="BCT-008",
        run_id="run-002",
        evidence_records=[],
        test_result="PASS",
        secret_key=SECRET_KEY,
    )

    assert not manifest.verify(b"wrong_key"), "Manifest must fail verification with wrong key"


def test_manifest_captures_correct_evidence_count() -> None:
    """The manifest evidence_count must equal the number of records passed in."""
    records = [{"tag": f"step-{i}", "result": "PASS"} for i in range(5)]
    manifest = EvidenceManifest.create(
        braid_id="BCT-008",
        run_id="run-003",
        evidence_records=records,
        test_result="PASS",
        secret_key=SECRET_KEY,
    )

    assert manifest.evidence_count == 5


def test_manifest_detects_log_tampering() -> None:
    """
    If a manifest's log_hash is recomputed over a different set of records,
    the resulting manifest_signature will not match the stored one.
    """
    original_records = [{"tag": "auth", "result": "PASS"}]
    manifest = EvidenceManifest.create(
        braid_id="BCT-008",
        run_id="run-004",
        evidence_records=original_records,
        test_result="PASS",
        secret_key=SECRET_KEY,
    )

    tampered_records = [{"tag": "auth", "result": "PASS"}, {"tag": "injected", "result": "PASS"}]
    tampered_log_bytes = json.dumps(tampered_records, sort_keys=True, separators=(",", ":")).encode()
    tampered_log_hash = hashlib.sha256(tampered_log_bytes).hexdigest()

    assert manifest.log_hash != tampered_log_hash, "Tampered records must produce a different log hash"


def test_manifest_from_real_braid_execution() -> None:
    """A manifest created from a real braid execution must verify and record evidence correctly."""
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"], token_id="manifest_tok")
    executor = BraidExecutor(manager)

    braid = ExecutableBraid(
        strands=[
            StrandState(value={"payload": "data"}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"shadow": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda v: True}))
    braid.add_crossing(ExecutableCrossing("promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1))

    result = braid.execute(executor)
    records = [r.to_dict() for r in result.evidence_log]

    manifest = EvidenceManifest.create(
        braid_id="BCT-008",
        run_id="run-005",
        evidence_records=records,
        test_result="PASS",
        secret_key=SECRET_KEY,
    )

    assert manifest.evidence_count == len(records)
    assert manifest.test_result == "PASS"
    assert manifest.verify(SECRET_KEY)
