# Terminology

This document defines precise language used throughout the BCT research program. Consistent terminology is essential for rigorous research and clear communication with reviewers.

---

## Layer Labels

All claims in this repository are labeled with one of three designations:

**[ESTABLISHED]**  
Prior mathematical or computational work. A citation is provided. BCT builds on this but does not claim it as original.

**[HYPOTHESIS]** or **[ORIGINAL]**  
An original claim or definition from this research project. Not independently validated unless explicitly stated. Requires testing before it can be treated as a result.

**[INSPIRATION]**  
A conceptual analogy that motivates the research. Does not constitute evidence. Listed for transparency.

**[OPEN]**  
An unresolved research question. Not a claim. A direction for future work.

---

## Precise Usage

### "Established"
Use only for claims backed by peer-reviewed mathematics or computer science literature, with a citation. Do not use loosely.

### "Original"
Use only for definitions and hypotheses introduced by this research project. Do not claim originality for concepts that exist in prior literature, even if you were unaware of them.

### "Verified"
Use only when a claim has been formally proved or empirically demonstrated with documented results. Do not use "verified" to mean "we believe this to be true."

### "Proof" vs. "Argument"
- **Proof** — a complete formal mathematical derivation
- **Argument** — an informal justification or intuitive reasoning

BCT documents distinguish these. Formal proofs are in `proofs/`. Arguments and motivations are in text.

### "Architecture" vs. "System"
- **Architecture** — a formal specification of structure and behavior
- **System** — an implemented, running instance

BCT currently defines architectures. The prototype is an early-stage system.

### "Instruction" vs. "Operation"
- **Instruction** — a member of a defined instruction family; part of the braid ISA
- **Operation** — a general computational action

BCT instructions are formally specified. Do not use "operation" where "instruction" is precise.

### "Crossing" (BCT usage)
In BCT, a crossing is always an executable crossing unless explicitly labeled as a classical braid crossing. Crossings carry instructions and perform work.

### "Strand"
A computational path within a braid topology. Strands carry state, authority tokens, and execution context.

### "Trusted" vs. "Active"
- **Trusted state** — has passed a verification crossing
- **Active state** — currently executing but not yet verified

These are distinct and must not be conflated. An active state is not trusted.

### "Evidence"
The append-only record of computation. Evidence is never overwritten or deleted in the BCT model. Use "evidence" precisely — not as a synonym for "data" or "result."

### "Recovery" vs. "Restart"
- **Recovery** — restoring execution while preserving evidence
- **Restart** — discarding execution state and beginning again

BCT recovery preserves evidence. It is not a restart.

### "Hypothesis" vs. "Conjecture" vs. "Claim"
- **Hypothesis** — a testable proposition that drives experimental design
- **Conjecture** — a mathematical proposition believed true but not yet proved
- **Claim** — a general assertion

BCT uses "hypothesis" for testable empirical propositions and "conjecture" for mathematical propositions. Avoid "claim" without qualification.

---

## Terms to Avoid Without Qualification

These terms are frequently misused. Use them precisely or avoid them:

| Term | Issue | Better alternative |
|---|---|---|
| "Proven" | Often used informally | "Formally proved" (with citation to proof) or "shown empirically" |
| "Better" | Requires comparison baseline and metric | "Achieves lower overhead than X on benchmark Y" |
| "Efficient" | Requires asymptotic or empirical qualification | "O(n log n) in space" or "30% faster on benchmark X" |
| "Secure" | Requires threat model | "Resistant to authority bypass under threat model T" |
| "Novel" | Requires prior art review | "Not present in prior literature as of date X" |
| "Complete" | Has formal meanings in theory | Specify whether Turing-complete, computationally complete, etc. |
| "Solves" | Overstates | "Addresses," "reduces," "improves," "mitigates" |

---

## Abbreviations

| Abbreviation | Full form |
|---|---|
| BCT | Braided Computational Topology |
| ISA | Instruction Set Architecture |
| H1–H6 | Hypotheses 1 through 6 (see `research/HYPOTHESES.md`) |
| Bₙ | Braid group on n strands |
| σᵢ | i-th Artin generator of a braid group |
