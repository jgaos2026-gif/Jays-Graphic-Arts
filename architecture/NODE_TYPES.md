# Node Types

> All content is **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Overview

**[HYPOTHESIS]** A BCT braid is composed of nodes connected by strand segments. Nodes occur at crossings and at special structural points. This document defines the node taxonomy.

---

## Crossing Nodes

Crossing nodes are the primary computational nodes. Every crossing node is an executable crossing.

| Node Type | Family | Description |
|---|---|---|
| Integrity Node | INTEG | Performs verification; promotes or routes to recovery |
| Routing Node | ROUTE | Selects execution path; forks or joins strands |
| Recovery Node | RECOV | Detects and handles failures |
| Role Exchange Node | ROLE | Transfers authority tokens |
| Authority Node | AUTH | Checks permissions |
| Memory Node | MEM | Coordinates memory tier transitions |

---

## Structural Nodes

Structural nodes define the shape of the braid but carry no instruction.

**Input Node:** The top boundary of a strand. Every strand begins at an Input Node. Input Nodes initialize the strand state and evidence record.

**Output Node:** The bottom boundary of a strand. Every strand terminates at an Output Node. Output Nodes record the final strand state in the evidence log.

**Fork Node:** A special structural node where a strand splits into two parallel strands. Fork Nodes are created by ROUTE.FORK crossings.

**Join Node:** A structural node where two strands merge into one. Join Nodes are created by ROUTE.JOIN crossings.

**Pocket Entry Node:** Marks the entry boundary of a memory pocket. Created by MEM.OPEN_POCKET crossings.

**Pocket Exit Node:** Marks the exit boundary of a memory pocket. Created by MEM.CLOSE_POCKET crossings.

**Stitch Node:** A special node connecting two non-adjacent strands. Created by MEM.STITCH crossings.

---

## Layer Boundary Nodes

Layer Boundary Nodes mark transitions between the eight computational layers.

```
Input Layer Boundary
  ↓
Authority Layer Boundary
  ↓
Verification Layer Boundary
  ↓
Execution Layer Boundary
  ↓
Recovery Layer Boundary
  ↓
Certification Layer Boundary
  ↓
Persistence Layer Boundary
  ↓
Evidence Layer Boundary
```

Layer Boundary Nodes are mandatory checkpoints. No strand may cross a layer boundary without the appropriate crossing type for that boundary.

---

## Special Nodes

**Root Authority Node:** The unique node representing the root authority token. There is exactly one per braid. It cannot be reached by user-level instructions.

**Evidence Log Node:** The append-only evidence accumulator. All evidence records from all crossings converge here. It has no output strand — evidence is terminal.

**Recovery Entry Node:** The entry point for the recovery path at each layer. All failure routing from that layer connects to this node.

**Closure Node:** In closed braids (computation cycles), the Closure Node connects the bottom Output Nodes back to the top Input Nodes, completing the cycle.

---

## Node Connectivity Rules

**[HYPOTHESIS]** The following rules govern valid node connectivity:

1. Every strand begins at exactly one Input Node and ends at exactly one Output Node or Join Node
2. A Fork Node produces exactly two output strands
3. A Join Node receives exactly two input strands
4. An Authority Node must precede any Certification Node on every path
5. A Verification Node must precede any Execution Node on every path
6. Evidence Log Nodes are the only terminal nodes (no outgoing strands)
7. The Root Authority Node has no incoming strands

---

## Open Problems

1. Formal graph grammar for valid BCT braid node connectivity
2. Decidability of validity checking for braid node graphs
3. Efficient data structure for braid node representation in simulation
4. Visualization: standard notation for BCT braid node diagrams

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
