# Braid Instruction Set Architecture

> All content is **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Overview

The Braid ISA defines the complete set of executable crossing types, operand structures, and execution semantics for the BCT architecture. It is an original research definition. It has not been independently validated.

---

## Design Principles

1. Every crossing is an instruction — there are no passive crossings
2. Every instruction has a defined evidence output
3. No instruction discards existing evidence
4. Instructions are grouped into families with defined interaction rules
5. Authority is required for every state promotion
6. Recovery paths are defined for every instruction family

---

## Crossing Format

Each executable crossing is encoded as:

```
CROSSING ::= <family> <opcode> <strand_i> <strand_j> <direction> <operands>

<family>    ::= INTEG | ROUTE | RECOV | ROLE | AUTH | MEM
<opcode>    ::= family-specific opcode (see below)
<strand_i>  ::= strand index (0-based)
<strand_j>  ::= strand index; |strand_i - strand_j| = 1 for standard braids
<direction> ::= OVER | UNDER
<operands>  ::= instruction-specific operand list
```

---

## Integrity Family (INTEG)

Opcodes:

| Opcode | Operation | Input | Output | Evidence |
|---|---|---|---|---|
| `VERIFY` | Hash and verify state | (state, hash_fn) | (trusted_state \| recovery_trigger) | verification_record |
| `PROMOTE` | Promote verified state | (trusted_state) | (certified_state) | promotion_record |
| `ATTEST` | Attach external attestation | (state, attestation) | (attested_state) | attestation_record |
| `SEAL` | Seal state as immutable | (certified_state) | (sealed_state) | seal_record |
| `COMPARE` | Compare two states for equivalence | (state_a, state_b) | (equivalence_result) | comparison_record |

---

## Routing Family (ROUTE)

| Opcode | Operation | Input | Output | Evidence |
|---|---|---|---|---|
| `SELECT` | Evaluate predicate; select path | (state, predicate) | (path_token) | routing_decision |
| `FORK` | Duplicate state to multiple paths | (state) | (state, state) | fork_record |
| `JOIN` | Merge multiple paths | (state_a, state_b) | (merged_state) | join_record |
| `REDIRECT` | Reroute to alternate path | (state, condition) | (rerouted_state) | redirect_record |
| `REPLAY` | Replay state from evidence log | (evidence_ref) | (replayed_state) | replay_record |

---

## Recovery Family (RECOV)

| Opcode | Operation | Input | Output | Evidence |
|---|---|---|---|---|
| `DETECT` | Detect anomaly in state | (state) | (anomaly_flag, state) | anomaly_record |
| `QUARANTINE` | Isolate suspect state | (state) | (quarantined_state) | quarantine_record |
| `RESTORE` | Restore from checkpoint | (checkpoint_ref) | (restored_state) | restore_record |
| `HEAL` | Apply structural repair | (damaged_state, repair_fn) | (healed_state) | heal_record |
| `ARCHIVE` | Move failed state to cold evidence | (state) | () | archive_record |

---

## Role Exchange Family (ROLE)

| Opcode | Operation | Input | Output | Evidence |
|---|---|---|---|---|
| `TRANSFER` | Move authority token | (token, source_strand, target_strand) | () | transfer_record |
| `DELEGATE` | Create scoped sub-authority | (token, scope) | (delegated_token) | delegation_record |
| `REVOKE` | Remove authority token | (token) | () | revocation_record |
| `VERIFY_ROLE` | Confirm role ownership | (token, expected_role) | (confirmation) | role_check_record |

---

## Authority Family (AUTH)

| Opcode | Operation | Input | Output | Evidence |
|---|---|---|---|---|
| `CHECK` | Verify strand has required authority | (strand, required_authority) | (permit \| deny) | auth_check_record |
| `GATE` | Block execution without authority | (state, authority_req) | (state \| recovery_trigger) | gate_record |
| `INHERIT` | Inherit authority from parent strand | (parent_token, child_strand) | (child_token) | inheritance_record |
| `SCOPE` | Restrict authority to defined scope | (token, scope) | (scoped_token) | scope_record |

---

## Memory Family (MEM)

| Opcode | Operation | Input | Output | Evidence |
|---|---|---|---|---|
| `STORE_HOT` | Write to hot memory | (key, state) | () | store_hot_record |
| `LOAD_HOT` | Read from hot memory | (key) | (state) | load_hot_record |
| `DEMOTE_WARM` | Move hot state to warm | (key) | () | demote_record |
| `PROMOTE_HOT` | Move warm state to hot | (key) | () | promote_record |
| `ARCHIVE_COLD` | Move warm state to cold | (key) | () | archive_cold_record |
| `RETRIEVE_COLD` | Fetch from cold to warm | (key) | () | retrieve_cold_record |
| `OPEN_POCKET` | Create a memory pocket | (scope) | (pocket_id) | pocket_open_record |
| `CLOSE_POCKET` | Close a memory pocket | (pocket_id) | () | pocket_close_record |
| `STITCH` | Link non-adjacent memory regions | (region_a, region_b) | (stitch_id) | stitch_record |

---

## Evidence Records

Every instruction produces an evidence record appended to the log. A minimum evidence record contains:

```
EvidenceRecord ::= {
  tag:         unique crossing identifier
  family:      instruction family
  opcode:      instruction opcode
  timestamp:   logical timestamp (crossing index)
  strand_i:    first strand index
  strand_j:    second strand index
  direction:   OVER | UNDER
  input_hash:  hash of input strand states
  output_hash: hash of output strand states
  authority:   authority token present at crossing (if any)
  result:      PASS | FAIL | RECOVERY_TRIGGERED
}
```

Evidence records are append-only. No instruction may modify or delete a prior evidence record.

---

## Execution Cycle

```
1. Fetch next crossing from braid sequence
2. Decode family, opcode, strands, direction, operands
3. CHECK authority (AUTH.CHECK) — if fails, trigger recovery
4. Execute instruction
5. Append evidence record to log
6. Advance to next crossing
```

Step 3 is mandatory for all instructions. No instruction executes without an authority check.

---

## Open Problems

- Formal semantics: define BCT ISA in a standard semantic framework (operational, denotational, or axiomatic)
- Completeness: is the current instruction set complete for the defined architectural goals?
- Overhead: what is the minimum instruction overhead on conventional hardware?
- Simulation: what is the correct mapping from BCT ISA to x86/ARM instruction sequences?

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
