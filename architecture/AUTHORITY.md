# Authority Architecture

> All content is **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Design Philosophy

**[HYPOTHESIS]** In the BCT architecture, authority is not a policy applied on top of computation. It is a structural property of the braid topology. An execution cannot proceed past an authority crossing without the required authority token — not by policy enforcement, but by architectural construction.

This is a hypothesis. Formal proof that the architecture enforces this structurally is an open problem.

---

## Governing Laws

| Law | Statement | Authority implication |
|---|---|---|
| 4 | Authority cannot be bypassed | No path through the braid exists that avoids authority crossings |
| 8 | Verification precedes promotion | Authority must be verified before state can be promoted to trusted |
| 9 | Every module has explicit authority | Every braid strand carries an explicit authority token |

---

## Authority Tokens

**[HYPOTHESIS]** Authority in BCT is carried by **authority tokens** attached to strands.

Properties:
- Each strand carries at most one authority token at any time
- Tokens are not duplicated: transfer moves the token; the source strand loses it
- Tokens have a defined scope: the set of operations they permit
- Tokens have a defined lifetime: they expire or are revoked through defined crossings
- Token possession is necessary (but not sufficient) for state promotion

**Token structure:**

```
AuthorityToken ::= {
  id:        unique token identifier
  role:      defined role (e.g., EXECUTOR, VERIFIER, AUDITOR)
  scope:     permitted operations
  issued_by: issuing authority (parent token id or root)
  issued_at: logical timestamp
  expires:   logical timestamp or NEVER
  revoked:   boolean (set by ROLE.REVOKE)
}
```

---

## Authority Hierarchy

**[HYPOTHESIS]** Authority tokens form a directed acyclic graph (DAG) of delegation:

```
ROOT_AUTHORITY
    ├── SYSTEM_AUTHORITY
    │       ├── EXECUTOR_AUTHORITY
    │       └── VERIFIER_AUTHORITY
    └── AUDIT_AUTHORITY
            └── READ_ONLY_AUTHORITY
```

**[ESTABLISHED]** Lattice theory (Davey & Priestley, 2002) provides the formal framework for partial orders of this kind. The authority hierarchy is a lattice under the ≤ relation (A ≤ B means A's permissions are a subset of B's).

---

## Authority Crossings

**[HYPOTHESIS]** Three types of authority crossing are defined:

**CHECK crossing:** Verifies that a strand possesses a required authority token before execution proceeds. If the check fails, execution is routed to the recovery path. Evidence is recorded regardless of outcome.

**GATE crossing:** Blocks state promotion if the authority requirement is not met. A gate is stricter than a check: it prevents execution from continuing, not just promotion.

**INHERIT crossing:** A child strand inherits a scoped authority token from a parent strand. The parent retains its token; the child receives a new token with reduced scope (defined by the delegation parameters).

---

## Authority and Recovery

**[HYPOTHESIS]** Authority violations must not destroy evidence. When an authority crossing fails:

1. The failure is recorded in the evidence log (append-only)
2. The strand is quarantined (not terminated)
3. The execution is routed to the recovery path
4. The recovery path is itself subject to authority checking

This means authority failures produce auditable records, not silent termination.

---

## Root Authority

**[HYPOTHESIS]** The BCT architecture defines a root authority that is:
- Not derived from any other token
- Immutable and permanent
- The ultimate issuer of all other tokens
- Not accessible by user-level braid instructions

The root authority is a structural constant of the braid architecture, not a runtime value.

---

## Open Problems

1. Formal proof that authority crossings cannot be topologically bypassed
2. Efficient representation of authority tokens in simulation
3. Definition of authority token revocation in distributed braids
4. Relationship between BCT authority lattice and capability-based security models

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
