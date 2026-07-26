# AI Applications

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

> All content is **[HYPOTHESIS]** or **[OPEN]** unless labeled **[CS-TRAJECTORY]** or **[ESTABLISHED]**.

---

## Motivation

**[CS-TRAJECTORY]** AI systems — particularly large language models and reasoning systems — face growing requirements for:

- Explainability: why did the system produce this output?
- Provenance: what sources and reasoning steps influenced this output?
- Authority tracking: which instructions or data sources took precedence?
- Auditability: can the reasoning be independently reviewed?
- Recovery: when the system produces an incorrect result, how is it corrected?

**[CS-TRAJECTORY]** These requirements are being addressed through separate systems: retrieval-augmented generation, chain-of-thought prompting, citation systems, RLHF feedback. Each is a separate overlay on a system not architecturally designed for them.

**[HYPOTHESIS]** BCT proposes that a braided AI architecture could carry these requirements natively through defined braid instruction families.

---

## Braided AI Architecture

**[HYPOTHESIS]** A braided AI reasoning system would separate reasoning functions into distinct braid families:

### Evidence Braid
Carries sources, citations, and provenance throughout the reasoning process. Each piece of evidence is a strand. Evidence crossings record when and how evidence was used.

Evidence strands are never terminated — they persist through the full reasoning cycle. Every output can be traced to its evidence strands.

### Hypothesis Braid
Generates candidate conclusions. Hypothesis strands are **active** (not trusted) by default. They must pass the Verification Braid before being used in certified outputs.

Multiple hypotheses are active simultaneously — parallel candidate strands that are not collapsed until verification.

### Verification Braid
Challenges and tests candidate hypotheses. Verification crossings apply:
- Consistency checks against evidence strands
- Cross-reference checks against multiple independent sources
- Logical coherence checks
- Contradiction detection against prior certified outputs

Only hypotheses that pass verification become trusted conclusions.

### Authority Braid
Tracks which sources, instructions, and reasoning rules outrank others. Authority crossings enforce:
- Source credibility ordering
- Instruction priority (system instructions > user instructions > inferred context)
- Domain expertise routing (some question classes route to specialized reasoning)

**[INSPIRATION]** This is analogous to the noncommutativity principle: `Verify → Promote ≠ Promote → Verify`. In an authority braid, a low-authority source cannot override a high-authority verified conclusion.

### Memory Braid
Manages reasoning state across:
- **Hot memory**: current reasoning context (active strands)
- **Warm memory**: recent prior conclusions still relevant to current reasoning
- **Cold memory**: full reasoning history (all prior sessions)

Memory braids enable the system to reference prior reasoning without re-executing it, while preserving the full provenance chain.

### Recovery Braid
Handles contradictions and errors:
- Detects when a candidate conclusion contradicts prior verified conclusions
- Quarantines the contradiction
- Rewinds the reasoning path to the last verified state
- Routes through an alternate reasoning path

The recovery record is preserved. The system can explain what it tried and why it was rejected.

### Consensus Braid
Reconciles outputs from specialized reasoning agents in a mixture-of-experts architecture. Consensus crossings:
- Compare outputs from multiple agents
- Weight by authority and evidence quality
- Produce a merged trusted conclusion
- Record the consensus process

### Output Braid
Promotes only certified conclusions to external output. No active or untrusted state reaches the output. Every output carries its complete verification certificate and provenance chain.

---

## Bidirectional Reasoning

**[HYPOTHESIS]** The key architectural advance of braided AI is bidirectional information flow:

```
Forward:  evidence → interpretation → candidate → verification → output

Reverse:  output → contradiction check → source validation → correction
```

The reverse path does not merely regenerate a new answer. It inspects the specific path that produced the original answer, identifies where it went wrong, and corrects at that point.

**[CS-TRAJECTORY]** This resembles how scientific reasoning works:

```
observe → propose → test → challenge → revise → verify
```

Current AI systems approximate the forward path well. They do not natively preserve the structures required for rigorous reverse traversal.

---

## Comparison to Current Approaches

| Property | Current LLM | Braided AI (Hypothesis) |
|---|---|---|
| Evidence provenance | Added as RAG overlay | Native braid strand |
| Reasoning steps | Chain-of-thought prompting | Native crossing sequence |
| Contradiction handling | Retry or prompt engineering | Native recovery braid |
| Authority enforcement | System prompt + RLHF | Native authority crossing |
| History preservation | Context window limit | Native cold memory braid |
| Output certification | Not native | Native certification layer |

**All items in the "Braided AI" column are hypotheses.** The comparison assumes BCT implementation succeeds. Whether the implementation achieves the claimed properties is the subject of H6.

---

## Research Questions

1. Can a braid provenance layer be implemented on top of an existing language model without retraining?
2. Does braid evidence tracking improve faithfulness of explanations on established benchmarks?
3. Can the authority braid replace or augment RLHF for instruction following?
4. Does the recovery braid improve factual accuracy on contradiction-detection benchmarks?
5. What is the latency overhead of the complete braided AI architecture?

---

## Benchmark Plan

See `research/BENCHMARK_PLAN.md` — BENCH-H6 for the AI explainability benchmark plan.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
