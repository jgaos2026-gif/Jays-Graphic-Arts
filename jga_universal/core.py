"""JGA BCT Universal Runtime: safe, content-addressed transfer and integrity MVP.

This is an additive sidecar. It never modifies source files in place.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import zlib
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Iterable, Protocol


class Verdict(str, Enum):
    CLEAN = "clean"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ScanResult:
    verdict: Verdict
    engine: str
    detail: str = ""


class Scanner(Protocol):
    def scan(self, path: Path) -> ScanResult: ...


class ClamAVScanner:
    """Optional ClamAV adapter. Missing scanner returns UNKNOWN, never CLEAN."""
    def __init__(self, executable: str = "clamscan"):
        self.executable = executable

    def scan(self, path: Path) -> ScanResult:
        try:
            p = subprocess.run(
                [self.executable, "--no-summary", str(path)],
                capture_output=True, text=True, timeout=120, check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return ScanResult(Verdict.UNKNOWN, "clamav", str(exc))
        if p.returncode == 0:
            return ScanResult(Verdict.CLEAN, "clamav", p.stdout.strip())
        if p.returncode == 1:
            return ScanResult(Verdict.MALICIOUS, "clamav", p.stdout.strip())
        return ScanResult(Verdict.UNKNOWN, "clamav", p.stderr.strip())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AuditLog:
    """Append-only JSONL hash chain. Tamper-evident, not tamper-proof."""
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict) -> str:
        previous = "0" * 64
        if self.path.exists():
            lines = self.path.read_text("utf-8").splitlines()
            if lines:
                previous = json.loads(lines[-1])["record_hash"]
        body = {"time_ns": time.time_ns(), "previous": previous, **event}
        record_hash = sha256(json.dumps(body, sort_keys=True).encode())
        record = {**body, "record_hash": record_hash}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return record_hash


class BCTVault:
    """Content-addressed, deduplicating store with adaptive zlib compression."""
    def __init__(self, root: Path):
        self.root = root
        self.blocks = root / "blocks"
        self.blocks.mkdir(parents=True, exist_ok=True)
        self.audit = AuditLog(root / "audit.jsonl")

    def put(self, data: bytes) -> dict:
        digest = sha256(data)
        target = self.blocks / digest
        if target.exists():
            return {"sha256": digest, "deduplicated": True, "stored_bytes": target.stat().st_size}
        compressed = zlib.compress(data, level=6)
        use_compression = len(compressed) < len(data)
        payload = b"Z" + compressed if use_compression else b"N" + data
        fd, tmp_name = tempfile.mkstemp(dir=self.blocks, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, target)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        self.audit.append({"action": "vault.put", "sha256": digest, "raw_bytes": len(data),
                           "stored_bytes": len(payload), "compressed": use_compression})
        return {"sha256": digest, "deduplicated": False, "stored_bytes": len(payload)}

    def get(self, digest: str) -> bytes:
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid SHA-256 content identifier")
        payload = (self.blocks / digest).read_bytes()
        if not payload:
            raise ValueError("Empty vault block")
        data = zlib.decompress(payload[1:]) if payload[:1] == b"Z" else payload[1:]
        if sha256(data) != digest:
            raise IOError("Vault integrity verification failed")
        return data

    def put_file(self, source: Path, block_size: int = 4 * 1024 * 1024) -> dict:
        if block_size < 1024:
            raise ValueError("block_size must be at least 1024 bytes")
        entries = []
        with source.open("rb") as f:
            while chunk := f.read(block_size):
                entries.append(self.put(chunk)["sha256"])
        manifest = {"name": source.name, "size": source.stat().st_size,
                    "block_size": block_size, "blocks": entries}
        manifest["manifest_sha256"] = sha256(json.dumps(manifest, sort_keys=True).encode())
        return manifest

    def restore_file(self, manifest: dict, destination: Path) -> None:
        expected = manifest["manifest_sha256"]
        body = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
        if sha256(json.dumps(body, sort_keys=True).encode()) != expected:
            raise IOError("Manifest integrity verification failed")
        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = destination.with_name(destination.name + ".bct-tmp")
        try:
            with tmp.open("wb") as out:
                for digest in manifest["blocks"]:
                    out.write(self.get(digest))
                out.flush()
                os.fsync(out.fileno())
            if tmp.stat().st_size != manifest["size"]:
                raise IOError("Restored file size mismatch")
            os.replace(tmp, destination)
        finally:
            if tmp.exists():
                tmp.unlink()


class Quarantine:
    """Isolates suspicious inputs outside active data paths; never auto-purges."""
    def __init__(self, root: Path, audit: AuditLog):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.audit = audit

    def isolate(self, source: Path, result: ScanResult) -> Path:
        digest = sha256(source.read_bytes())
        target = self.root / f"{digest}.{source.name}.quarantined"
        if not target.exists():
            shutil.copy2(source, target)
        self.audit.append({"action": "security.quarantine", "sha256": digest,
                           "source_name": source.name, "verdict": result.verdict.value,
                           "engine": result.engine, "detail": result.detail})
        return target

    def purge(self, quarantined: Path, *, operator: str, confirmed: bool) -> None:
        if not operator.strip() or confirmed is not True:
            raise PermissionError("Purge requires named operator and explicit confirmation")
        digest = sha256(quarantined.read_bytes())
        self.audit.append({"action": "security.purge", "sha256": digest,
                           "operator": operator, "path_name": quarantined.name})
        quarantined.unlink()


class PQCProvider(Protocol):
    """Adapter contract for a vetted NIST PQC implementation; no home-grown crypto."""
    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]: ...
    def decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes: ...
    def sign(self, private_key: bytes, message: bytes) -> bytes: ...
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool: ...


PQC_ALGORITHMS = {
    "kem": "ML-KEM (NIST FIPS 203)",
    "signature": "ML-DSA (NIST FIPS 204)",
    "backup_signature": "SLH-DSA (NIST FIPS 205)",
}


def split_for_mail(source: Path, output_dir: Path, part_bytes: int = 18 * 1024 * 1024) -> dict:
    """Creates independently hashed chunks. Does NOT bypass Gmail's total 25 MB limit."""
    if part_bytes <= 0 or part_bytes > 18 * 1024 * 1024:
        raise ValueError("part_bytes must be between 1 byte and 18 MiB")
    output_dir.mkdir(parents=True, exist_ok=True)
    parts, index = [], 0
    with source.open("rb") as f:
        while chunk := f.read(part_bytes):
            name = f"{source.name}.bctpart{index:05d}"
            path = output_dir / name
            path.write_bytes(chunk)
            parts.append({"file": name, "size": len(chunk), "sha256": sha256(chunk)})
            index += 1
    manifest = {"format": "JGA-BCT-MAIL-1", "source_name": source.name,
                "source_size": source.stat().st_size, "parts": parts,
                "note": "Attach only within provider total-size limits; otherwise transfer via approved storage link."}
    manifest["manifest_sha256"] = sha256(json.dumps(manifest, sort_keys=True).encode())
    (output_dir / (source.name + ".bct-manifest.json")).write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def join_mail_parts(manifest_path: Path, parts_dir: Path, destination: Path) -> None:
    manifest = json.loads(manifest_path.read_text("utf-8"))
    expected = manifest["manifest_sha256"]
    body = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    if sha256(json.dumps(body, sort_keys=True).encode()) != expected:
        raise IOError("Mail manifest has been modified")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + ".bct-tmp")
    try:
        with tmp.open("wb") as out:
            for part in manifest["parts"]:
                data = (parts_dir / part["file"]).read_bytes()
                if len(data) != part["size"] or sha256(data) != part["sha256"]:
                    raise IOError(f"Part failed integrity check: {part['file']}")
                out.write(data)
            out.flush()
            os.fsync(out.fileno())
        if tmp.stat().st_size != manifest["source_size"]:
            raise IOError("Reassembled size mismatch")
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()


class BCTRuntime:
    """Safe sidecar runtime. Observe/optimize only BCT-managed copies by default."""
    def __init__(self, root: Path, scanner: Scanner | None = None):
        self.root = root
        self.vault = BCTVault(root / "vault")
        self.audit = self.vault.audit
        self.quarantine = Quarantine(root / "quarantine", self.audit)
        self.scanner = scanner or ClamAVScanner()

    def ingest(self, source: Path) -> dict:
        result = self.scanner.scan(source)
        if result.verdict is not Verdict.CLEAN:
            held = self.quarantine.isolate(source, result)
            return {"status": "quarantined", "path": str(held),
                    "verdict": result.verdict.value, "engine": result.engine}
        manifest = self.vault.put_file(source)
        self.audit.append({"action": "ingest.accepted", "name": source.name,
                           "manifest_sha256": manifest["manifest_sha256"]})
        return {"status": "accepted", "manifest": manifest}

    def health(self) -> dict:
        return {"mode": "sidecar", "source_mutation": False,
                "pqc_adapter": "interface-only; configure vetted provider",
                "pqc_algorithms": PQC_ALGORITHMS,
                "scanner": type(self.scanner).__name__,
                "vault_blocks": sum(1 for p in self.vault.blocks.iterdir() if p.is_file())}
