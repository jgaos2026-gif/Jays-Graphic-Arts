# Memory Architecture

> All content is **[ORIGINAL — HYPOTHESIS]** unless labeled **[ESTABLISHED]**

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Overview

**[HYPOTHESIS]** The BCT memory architecture uses braid topology to coordinate three memory tiers through executable crossing instructions. Memory state is not stored as a flat address space but as a structured braid whose topology encodes the relationships between stored states, their history, and their retrieval paths.

---

## Three-Tier Model

### Hot Memory

**Purpose:** Active execution state.

**Properties:**
- Maximum bandwidth and minimum latency
- Limited capacity (determined by braid width)
- All currently executing strand states reside here
- State transitions are direct crossing operations

**Braid structure:** A tight braid with high crossing density. Strands representing active state interact frequently through integrity, authority, and routing crossings.

### Warm Memory

**Purpose:** Recent but inactive state.

**Properties:**
- Moderate latency and bandwidth
- Larger capacity than hot memory
- State in warm memory is not actively executing but remains readily available
- State may be promoted back to hot memory without full retrieval

**Braid structure:** A looser braid with lower crossing density. Warm strands maintain connectivity to hot strands through defined circulation crossings.

### Cold Memory

**Purpose:** Archived state with complete history.

**Properties:**
- Highest latency; unlimited capacity
- All state that has ever been committed is retrievable
- Retrieval path is deterministic (follows evidence log)
- State is never deleted (Law 7)

**Braid structure:** A persistent, append-only braid record. Cold strands are sealed (immutable) after archival.

---

## State Transitions

```
                    ┌──────────┐
                    │          │
                    ▼          │
HOT ─── demote ──► WARM ─── archive ──► COLD
 ▲                  │
 └─── promote ──────┘
                              ▲
                              │ retrieve
                              │
                            COLD
```

All transitions are recorded in the evidence log.

---

## Circulation Patterns

**[HYPOTHESIS]**

### Figure-8 Circulation

State circulates through a figure-eight path:

```
    Hot Memory
      ╱ ╲
     ╱   ╲
    ╳     ╳  ← crossing point (memory exchange)
     ╲   ╱
      ╲ ╱
    Warm Memory
      ╱ ╲
     ╱   ╲
    ╳     ╳
     ╲   ╱
      ╲ ╱
    (back to Hot)
```

**Characteristic:** State that was recently hot returns to hot more quickly than state that has been in warm for a longer time. This models temporal locality.

### Möbius Circulation

State circulates through a Möbius-topology path:

```
    All memory regions accessible
    from all execution contexts
    with equal path length
```

**Characteristic:** No privileged "inside" or "outside." All contexts have symmetric access to all memory regions. Useful for shared-state coordination across multiple execution strands.

---

## Memory Pockets

**[HYPOTHESIS]** A **memory pocket** is a bounded region of the braid where state is held temporarily during computation.

- Created by `MEM.OPEN_POCKET`
- Closed by `MEM.CLOSE_POCKET`
- State within a pocket is accessible only to strands within the pocket's scope
- When a pocket closes, its state is either committed to warm memory or discarded (with evidence of the discard)
- Unclosed pockets at braid termination trigger recovery

---

## Stitched Storage

**[HYPOTHESIS]** **Stitched storage** connects non-adjacent braid regions through stitch crossings, enabling efficient access to related state without requiring full traversal.

A stitch crossing:
- Connects two strands that are not adjacent in the braid
- Requires authority to create
- Preserves evidence of the connection
- Can be dissolved by an unstitching crossing

Stitched storage is used for: joining related but separated execution contexts; sharing state between parallel braid branches; implementing efficient foreign-key-style state relationships.

---

## History Preservation

**[HYPOTHESIS]** Memory state is never deleted (Law 7). All state transitions — demotions, promotions, archival, pocket operations — are recorded in the evidence log. This means:

- The full history of every memory state is reconstructible from the evidence log
- Recovery can restore any prior memory configuration
- Audits can trace the complete lifecycle of any stored value

The cost of this property is storage overhead proportional to the number of state transitions. Whether this overhead is competitive with conventional logging approaches for the relevant computation classes is the subject of Hypothesis H1.

---

## Open Problems

1. Optimal braid width for hot memory given a defined execution load
2. Circulation pattern selection criteria: when should Figure-8 be preferred over Möbius?
3. Efficient implementation of stitch crossings in simulation
4. Memory pocket garbage collection: detecting and recovering from pocket leaks
5. Cold memory retrieval optimization: minimizing latency while preserving determinism

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
