# Tests

This directory will contain tests for the BCT simulator and prototype.

**Status:** Empty — tests pending simulator implementation.

**Planned test suites:**
- `unit/` — unit tests for individual crossing instruction implementations
- `integration/` — integration tests for multi-layer execution
- `conformance/` — conformance tests against formal specification
- `property/` — property-based tests for invariant verification

**Testing philosophy:**
Tests must verify formal properties, not just functional behavior. Every governing law should have a corresponding test suite that attempts to violate it.

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
