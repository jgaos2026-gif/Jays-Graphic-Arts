# Decision Log

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  

> Key architectural decisions and the reasoning behind them.

---

## DL-001: Separate braid families rather than one universal braid

**Decision:** Define distinct instruction families (INTEG, ROUTE, RECOV, ROLE, AUTH, MEM) rather than one universal braid with all instruction types mixed.

**Reasoning:** Mixing verification semantics with routing semantics produces conflicts. An integrity crossing must be strict; a routing crossing must be flexible. Separating them into families with defined interaction points avoids semantic interference.

**Alternative considered:** Universal braid with opcode dispatch. Rejected because it would require the tamper detector to distinguish integrity violations from routing choices within the same crossing type — an unnecessary complication.

---

## DL-002: Append-only evidence log (never modified, never deleted)

**Decision:** Evidence records are strictly append-only. No opcode may modify or remove a prior record.

**Reasoning:** The moment evidence can be modified, the provenance chain breaks. An auditor cannot trust a record that could have been altered. The structural guarantee — that the architecture prevents modification — is stronger than a policy that prohibits it.

**Cost accepted:** Storage grows monotonically. This is a deliberate trade-off: correctness over storage efficiency.

---

## DL-003: Recovery preserves evidence, does not erase failure

**Decision:** RECOV.* opcodes append to evidence; they do not replace prior records.

**Reasoning:** Failure is knowledge. A recovery event that erases the failure evidence loses the most valuable information: what went wrong and where. The failure record enables post-mortem analysis, pattern detection, and future recovery improvement.

---

## DL-004: Three-tier memory (hot/warm/cold) rather than flat memory

**Decision:** Memory is organized as three tiers with defined transition crossings.

**Reasoning:** Execution state has natural lifecycle stages. Active state is accessed frequently; archived state rarely. A flat memory model requires either keeping everything hot (expensive) or adding a separate caching layer (additional complexity). The three-tier braid model encodes the lifecycle structurally.

---

## DL-005: Separate physics inspiration into its own directory

**Decision:** All physics-inspired content lives in `physics_inspiration/` with explicit labels. It does not appear in the primary proof chain.

**Reasoning:** Physics inspiration is genuinely motivating. But mixing it with architectural claims gives reviewers an easy reason to dismiss the work. Keeping it separated with explicit labels — and explicitly stating what is not claimed — makes the research more defensible, not less interesting.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
