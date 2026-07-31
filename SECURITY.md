# Security Policy

## Scope

This is a research prototype. It is not designed for production deployment. The security considerations below apply to the research software itself and to the security claims made in the research.

## Research Security Claims

BCT makes specific security-relevant claims, all classified in `CLAIMS_REGISTER.md`:

- **BCT-007** (Locally Verified): Active state cannot become trusted without INTEG.VERIFY
- **BCT-008** (Locally Verified): Authority cannot be bypassed in the simulator
- **BCT-009** (Locally Verified): Tampered execution is detected on replay

These claims are verified in the simulator. They are **not** verified in production hardware or production software environments.

## Reporting Vulnerabilities

If you discover:
- A way to bypass authority checking in the simulator
- A way to modify or delete evidence records
- A way to promote active state without verification crossing
- Any violation of the ten governing laws

Please open an issue labeled `security` with a detailed description of the bypass.

**This is actively desired.** Finding bypasses in the simulator validates or falsifies the architectural claims. A discovered bypass is a research result.

## Threat Model

The simulator is designed to resist:
- In-memory state modification (detected by HMAC)
- Crossing sequence reordering (detected by evidence hash)
- Evidence record deletion (structurally prevented by append-only log)
- Authority token duplication (prevented by transfer semantics)

The simulator is **not** designed to resist:
- Modification of the simulator code itself
- Modification of the evidence log storage layer
- Network-level attacks (no network layer exists)
- Side-channel attacks

## Disclosure Policy

Security findings will be addressed in the next version and credited in `CHANGELOG.md`.
