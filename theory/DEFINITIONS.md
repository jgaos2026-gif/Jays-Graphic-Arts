# Definitions

> All definitions are **[ORIGINAL]** unless labeled **[ESTABLISHED]**  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

**Definition 1 (Executable Crossing):** An executable crossing E is a 5-tuple (i, j, direction, instruction, tag) where i and j are strand indices with |i−j|=1 for standard crossings, direction ∈ {OVER, UNDER}, instruction ∈ I for defined instruction set I, and tag is a unique crossing identifier.

**Definition 2 (Executable Braid):** An executable braid B = (n, I, [E_1, …, E_k]) where n ≥ 2 is the strand count, I is an instruction set, and [E_1, …, E_k] is a sequence of executable crossings forming a valid braid word in B_n. **[ESTABLISHED: braid word validity via Artin relations]**

**Definition 3 (Evidence Log):** An evidence log L is a finite sequence of EvidenceRecord structures. L is strictly append-only: no element of L may be modified or removed after insertion.

**Definition 4 (Trusted State):** A strand state s is trusted if s.trust = TRUSTED and s.certificate is a valid VerificationCertificate attached by an INTEG.VERIFY crossing.

**Definition 5 (Certified State):** A strand state s is certified if s.trust = CERTIFIED and s was promoted from TRUSTED by an INTEG.PROMOTE crossing with valid authority.

**Definition 6 (Quarantined State):** A strand state s is quarantined if s.trust = QUARANTINED. Quarantined state is preserved in the evidence log but cannot be promoted without RECOV.HEAL followed by fresh INTEG.VERIFY.

**Definition 7 (Authority Token):** An authority token T = (id, role, scope, issued_by, issued_at, revoked) where role defines the set of permitted operations and scope restricts the domain of authority. A token is valid if revoked = False and the issuing authority chain traces to the root.

**Definition 8 (Braid Word Equivalence):** **[ESTABLISHED]** Two braid words w₁, w₂ are equivalent if one can be derived from the other by applying far-commutativity relations (σ_i σ_j = σ_j σ_i for |i−j|≥2) and braid relations (σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}). See `theory/PROOF_OBLIGATIONS.md` PO-1 for the computational tamper-detection implications.

**Definition 9 (Recovery Checkpoint):** A recovery checkpoint is a (state_hash, evidence_log_position, authority_snapshot) triple recorded at a defined point in execution. A checkpoint is valid if the state hash matches a certified strand state.

**Definition 10 (Contradiction Knot):** A contradiction knot arises when two trusted states s₁ and s₂ in the same braid execution are mutually inconsistent according to a defined consistency predicate. Both states are quarantined; the knot is recorded as a compound evidence record.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
