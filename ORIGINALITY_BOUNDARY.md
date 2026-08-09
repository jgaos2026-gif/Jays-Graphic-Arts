# Originality Boundary

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois  
**Version:** 1.0  

> This document precisely separates what BCT builds upon from what it contributes.  
> This distinction protects the work: it cannot be accused of claiming prior art as original,  
> and it clearly identifies what is defensibly new.

---

## Established Foundations

The following are prior mathematical and computational results. BCT builds upon them but claims no credit for them. Full citations are in `docs/REFERENCES.md` and `foundations/`.

### Mathematics
- **Artin braid groups** — Emil Artin, 1925, 1947
- **Knot theory and braid closures** — Alexander (1923), Markov (1936), Jones (1985)
- **Algebraic topology** — Standard graduate mathematics; Hatcher (2002)
- **Category theory and braided monoidal categories** — Mac Lane (1998), Joyal & Street (1993)
- **Directed algebraic topology** — Grandis (2009)
- **Persistent homology** — Edelsbrunner, Letscher & Zomorodian (2002)
- **Lattice theory and partial orders** — Davey & Priestley (2002)
- **Tensor networks** — Orús (2014)
- **Petri nets** — Petri (1962)
- **Information theory** — Shannon (1948)

### Computer Science
- **Topological quantum computing** — Kitaev (2003), Freedman et al. (2003)
- **Event sourcing and append-only logs** — Fowler (2005); widely deployed
- **Append-only ledgers / blockchain** — Nakamoto (2008); widely deployed
- **Capability-based security** — Dennis & Van Horn (1966); widely studied
- **Write-ahead logging and crash recovery** — Gray & Reuter (1992)
- **Provenance models** — W3C PROV (Moreau & Missier, 2013)
- **Noncommutative operations** — Standard abstract algebra; widely applied in quantum computing
- **Role-based access control** — Sandhu et al. (1996)
- **Distributed consensus** — Lamport (1978, 1998); Raft (Ongaro & Ousterhout, 2014)
- **Mixture-of-experts routing** — Shazeer et al. (2017); widely deployed in AI

---

## Original Contributions Under Investigation

The following are introduced by this research project. They are **research hypotheses and prototype implementations**, not validated results. Each is documented with a corresponding claim in `CLAIMS_REGISTER.md`.

### Conceptual Contributions
- **Computational braid taxonomy** — the systematic classification of braid families by computational purpose
- **Executable braid families** — braids whose crossings perform defined computational work
- **The design rule: one purpose → one braid family** — formalized in `manifesto/WHY_MANY_BRAIDS.md`
- **Bidirectional proof flow** — forward execution and reverse verification as coupled braid paths
- **Contradiction knots** — the structural representation of mutually inconsistent trusted states

### Architectural Contributions
- **Braid ISA** — the instruction set architecture for executable braids (`isa/BRAID_ISA.md`)
- **Role-exchange crossing semantics** — atomic authority token transfer between strands
- **Integrity braid semantics** — append-only verification with evidence-attached state
- **Recovery braid semantics** — evidence-preserving in-place repair vs. rollback
- **Authority braid semantics** — structural (not policy) authority enforcement
- **Eight-layer computational architecture** — Input → Authority → Verification → Execution → Recovery → Certification → Persistence → Evidence
- **History-preserving trusted state** — state that carries its complete verification chain
- **Atomic state-and-proof commits** — committing trusted state and its evidence record as one atomic unit
- **Triad resurrection** — recovery procedure restoring a three-part (state, authority, evidence) trusted unit

### AI Architecture Contributions
- **Braided AI governance framework** — applying BCT braid families to AI reasoning systems
- **Multi-braid cooperation runtime** — multiple braid families operating as one coordinated runtime
- **Evidence braid for AI provenance** — structural provenance tracking through AI reasoning steps
- **Consensus braid for multi-agent reconciliation** — disagreement-preserving distributed agreement

### Research Program Contributions
- **BCT claims register format** — structured separation of established/implemented/hypothetical/speculative claims
- **Public/private research boundary** — explicit documentation of what is published vs. retained

---

## What Is Explicitly Not Claimed

| Not Claimed | Reason |
|---|---|
| Invention of braid groups | Artin, 1925 |
| Invention of topological quantum computing | Kitaev, 2003 |
| Invention of append-only logs | Prior art; widely deployed |
| Invention of capability security | Dennis & Van Horn, 1966 |
| Production-readiness of BCT | Research prototype only |
| Superiority to all existing architectures | Unproven; benchmark-dependent |
| Proof of Turing completeness | Open conjecture |
| Proof of any hypothesis H1–H6 | Untested |
| Independence from prior work | All foundations cited |

---

## Border Cases

Some BCT concepts have partial analogies in prior work. These are noted to prevent overclaiming:

| BCT Concept | Prior analogy | BCT distinction |
|---|---|---|
| Executable crossings | Quantum gate as braid operation (Kitaev 2003) | Classical, not quantum; different instruction model |
| Append-only evidence | Write-ahead logs, blockchain | BCT integrates evidence as structural part of execution, not separate layer |
| Authority tokens | Capability tokens (Dennis & Van Horn) | BCT embeds authority in braid topology; capability systems are software-layer |
| Recovery paths | Checkpoint/restart | BCT preserves evidence during recovery; restart discards it |
| Bidirectional flow | Forward/backward chaining (logic programming) | BCT applies to execution verification, not logic inference |

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
