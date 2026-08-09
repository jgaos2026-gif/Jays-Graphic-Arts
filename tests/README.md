# Tests

This directory contains tests for the BCT simulator.

**Status:** 47 tests passing across all suites.

## Test Suites

- `unit/` — unit tests for crossing execution, authority, evidence, and braid composition
- `adversarial/` — tests that attempt to violate governing laws (tamper, proof obligations)
- `bct_001_integrity/` — non-commutativity and crossing-order correctness
- `bct_002_authority/` — delegation, revocation, HMAC capability tokens
- `bct_008_evidence/` — evidence manifest schema and denied-action logging
- `property/` — property-based invariant tests (evidence monotonicity, trust ordering)
- `replay/` — deterministic replay and tamper-detected replay

## Running Tests

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Testing Philosophy

Tests verify formal properties, not just functional behavior. Every governing law has at least one test suite that attempts to violate it and confirms the violation is detected and rejected.

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
