# Related Work

> **[ESTABLISHED]** — existing computer science work relevant to BCT.  
> **Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois (compilation)

---

## Event Sourcing and Append-Only Logs

**[ESTABLISHED]** Event sourcing (Fowler, 2005) preserves the history of state changes as an append-only event log. The current state is derived by replaying the event log from the beginning or from a snapshot.

**BCT relationship:** BCT's evidence log is structurally similar. The difference: in event sourcing, the log is a separate layer added to an application. In BCT, the evidence log is a structural property of the braid execution — every crossing produces a log entry by architectural construction, not by programmer choice.

## Capability-Based Security

**[ESTABLISHED]** Capability-based security (Dennis & Van Horn, 1966; Miller, 2006) represents access rights as unforgeable tokens that must be presented to access a resource.

**BCT relationship:** BCT authority tokens are capability tokens. The architectural difference is that BCT embeds authority checking in the braid crossing structure — a crossing without the required token cannot execute, not because a policy check denies it, but because the execution engine requires a token as a structural operand.

## Petri Nets

**[ESTABLISHED]** Petri nets (Petri, 1962) model concurrent computation as a bipartite graph of places and transitions. Firing rules govern when transitions can fire. Petri nets have well-studied reachability, liveness, and boundedness properties.

**BCT relationship:** Petri nets and executable braids both model concurrent processes with explicit interaction. Key difference: Petri nets do not inherently order concurrent events that happen in different places. Braids impose a total linear order on crossings that determines their topological class.

## W3C PROV Provenance Model

**[ESTABLISHED]** The W3C PROV data model (Moreau & Missier, 2013) defines a standard vocabulary for provenance: entities, activities, agents, and their relationships.

**BCT relationship:** BCT's provenance braid implements a structural version of PROV concepts. The architectural difference: PROV is a data model applied to existing systems. BCT embeds provenance in the execution topology.

## Distributed Consensus

**[ESTABLISHED]** Raft (Ongaro & Ousterhout, 2014) and Paxos (Lamport, 1998) achieve distributed consensus by agreeing on a log of commands. Safety and liveness are proved for defined failure models.

**BCT relationship:** BCT's consensus braid is inspired by these protocols but adds disagreement history preservation. In Raft/Paxos, the history of disagreement is discarded after consensus. In BCT, it is preserved as evidence. Whether this offers practical advantages is an open empirical question.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
