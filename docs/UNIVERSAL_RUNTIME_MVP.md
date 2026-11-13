# JGA BCT Universal Runtime (prototype)

A non-destructive sidecar combining BCT's verification-first model with SB688/SB712-style integrity, recovery, quarantine, and content-addressed storage.

## Implemented in this prototype
- Adaptive zlib compression only when the compressed representation is smaller.
- SHA-256 content-addressed blocks and deduplication.
- Chunked file manifests and verified restore.
- Hash-chained JSONL audit records.
- Fail-closed scanning: absent ClamAV means UNKNOWN, and UNKNOWN is quarantined.
- Quarantine outside active data paths; no automatic deletion. Purge requires an explicit operator and confirmation.
- Large-mail chunk creation/reassembly with per-part hashes.
- PQC provider interface and NIST algorithm identifiers. A vetted ML-KEM/ML-DSA implementation must be supplied; this prototype does not pretend a placeholder is cryptography.

## Gmail reality
Personal Gmail attachment limit is 25 MB total. This tool can create 18 MiB chunks, but multiple chunks in one message still count toward the total limit. For larger transfers, upload the encrypted/verified package to an approved storage provider and send a permission-controlled link. BCT cannot override provider limits.

## Install and test
Python 3.10+; standard library only for core functions.

```bash
python -m unittest discover -s tests -v
```

Install ClamAV separately and ensure `clamscan` is on PATH for malware scanning. Without it, inbound files remain UNKNOWN and are quarantined.

## Example
```python
from pathlib import Path
from jga_universal import BCTRuntime

runtime = BCTRuntime(Path("./bct-data"))
print(runtime.health())
print(runtime.ingest(Path("./incoming/report.bin")))
```

## Explicit limitations
This is an integration prototype, not a production endpoint-security product, not a network acceleration appliance, and not a validated quantum computer interface. Compression benefits depend on file type; already-compressed/encrypted media may not shrink. Transfer throughput depends on the network, endpoints, provider caps, and workload. Do not deploy as the sole security control.
