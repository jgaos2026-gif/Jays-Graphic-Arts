# Braid ISA

> **[ORIGINAL — HYPOTHESIS]**  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
> **Version:** Alpha 0.1

The Braid Instruction Set Architecture defines all executable crossing types, operand structures, and execution rules for the BCT architecture.

This is a research definition. It is implemented in `braid_simulator/`. See `isa/OPCODES.md` for the complete opcode list.

## Quick Reference

| Family | Prefix | Purpose |
|---|---|---|
| Integrity | `INTEG` | Verify state; build trust |
| Routing | `ROUTE` | Select and direct execution paths |
| Recovery | `RECOV` | Detect failures; restore evidence-intact |
| Role Exchange | `ROLE` | Transfer authority tokens |
| Authority | `AUTH` | Enforce permissions |
| Memory | `MEM` | Coordinate hot/warm/cold state |

## Execution Contract

Every crossing E in the Braid ISA satisfies:
1. Authority is checked before execution (AUTH.CHECK precedes any state promotion)
2. Evidence is appended after execution (never before, never omitted)
3. No crossing modifies a prior evidence record
4. No crossing produces TRUSTED state without INTEG.VERIFY

See `isa/EXECUTION_RULES.md` for the complete contract.
