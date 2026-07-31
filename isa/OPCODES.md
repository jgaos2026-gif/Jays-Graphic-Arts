# Opcode Reference

> **[ORIGINAL]** Complete opcode list for BCT ISA Alpha 0.1  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## INTEG Family

| Opcode | Inputs | Outputs | Evidence | Effect |
|---|---|---|---|---|
| `INTEG.VERIFY` | (state, hash_fn) | (trusted_state \| recovery_trigger) | verification_record | Verifies state; promotes or routes to recovery |
| `INTEG.PROMOTE` | (trusted_state) | (certified_state) | promotion_record | Elevates verified state to certified |
| `INTEG.ATTEST` | (state, attestation) | (attested_state) | attestation_record | Attaches external attestation |
| `INTEG.SEAL` | (certified_state) | (sealed_state) | seal_record | Marks state as immutable certified output |
| `INTEG.COMPARE` | (state_a, state_b) | (equivalence_result) | comparison_record | Compares two states |

## ROUTE Family

| Opcode | Inputs | Outputs | Evidence |
|---|---|---|---|
| `ROUTE.SELECT` | (state, predicate) | (path_token) | routing_decision |
| `ROUTE.FORK` | (state) | (state, state) | fork_record |
| `ROUTE.JOIN` | (state_a, state_b) | (merged_state) | join_record |
| `ROUTE.REDIRECT` | (state, condition) | (rerouted_state) | redirect_record |
| `ROUTE.REPLAY` | (evidence_ref) | (replayed_state) | replay_record |

## RECOV Family

| Opcode | Inputs | Outputs | Evidence |
|---|---|---|---|
| `RECOV.DETECT` | (state) | (anomaly_flag, state) | anomaly_record |
| `RECOV.QUARANTINE` | (state) | (quarantined_state) | quarantine_record |
| `RECOV.RESTORE` | (checkpoint_ref) | (restored_state) | restore_record |
| `RECOV.HEAL` | (damaged_state, repair_fn) | (healed_state) | heal_record |
| `RECOV.ARCHIVE` | (state) | () | archive_record |

## ROLE Family

| Opcode | Inputs | Outputs | Evidence |
|---|---|---|---|
| `ROLE.TRANSFER` | (token, source, target) | () | transfer_record |
| `ROLE.DELEGATE` | (token, scope) | (delegated_token) | delegation_record |
| `ROLE.REVOKE` | (token) | () | revocation_record |
| `ROLE.VERIFY_ROLE` | (token, expected_role) | (confirmation) | role_check_record |

## AUTH Family

| Opcode | Inputs | Outputs | Evidence |
|---|---|---|---|
| `AUTH.CHECK` | (strand, required_authority) | (permit \| deny) | auth_check_record |
| `AUTH.GATE` | (state, authority_req) | (state \| recovery_trigger) | gate_record |
| `AUTH.INHERIT` | (parent_token, child_strand) | (child_token) | inheritance_record |
| `AUTH.SCOPE` | (token, scope) | (scoped_token) | scope_record |

## MEM Family

| Opcode | Inputs | Outputs | Evidence |
|---|---|---|---|
| `MEM.STORE_HOT` | (key, state) | () | store_hot_record |
| `MEM.LOAD_HOT` | (key) | (state) | load_hot_record |
| `MEM.DEMOTE_WARM` | (key) | () | demote_record |
| `MEM.PROMOTE_HOT` | (key) | () | promote_record |
| `MEM.ARCHIVE_COLD` | (key) | () | archive_cold_record |
| `MEM.RETRIEVE_COLD` | (key) | () | retrieve_cold_record |
| `MEM.OPEN_POCKET` | (scope) | (pocket_id) | pocket_open_record |
| `MEM.CLOSE_POCKET` | (pocket_id) | () | pocket_close_record |
| `MEM.STITCH` | (region_a, region_b) | (stitch_id) | stitch_record |

**Total opcodes: 28**  
**Implementation status:** See `PROJECT_STATUS.md` and `CLAIMS_REGISTER.md`.
