# ISA Versioning

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

## Current Version

**BCT ISA Alpha 0.1**

This is a research-stage ISA. Breaking changes are expected in 0.x versions.

## Version Policy

| Version | Stability guarantee |
|---|---|
| 0.x | No stability guarantee; breaking changes allowed |
| 1.0 | Stable opcode set; additions only |
| 2.0 | Major revision; backward compatibility documented |

## Versioning Rules for 1.0+

- New opcodes may be added without a version bump
- Opcode semantics may not change without a version bump
- Opcode removal requires a major version bump
- Evidence record format changes require a major version bump

## Change Log

### Alpha 0.1 (2026-07-26)
- Initial ISA definition
- 28 opcodes across 6 families
- Evidence record format v1
- Execution rules R1–R8
