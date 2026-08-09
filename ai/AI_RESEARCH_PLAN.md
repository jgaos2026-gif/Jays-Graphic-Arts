# AI Research Plan

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Phase 5 Plan (Post-H1-H5 validation)

### Step 1: Define the explainability benchmark
Select: TruthfulQA, HotpotQA, FactScore, custom contradiction detection set.
Define metrics: citation precision, faithfulness, contradiction detection rate, correction accuracy.

### Step 2: Implement evidence braid provenance layer
Build a braid provenance wrapper for an existing open-source language model.
The wrapper adds Evidence Braid crossings at each reasoning step without retraining the model.

### Step 3: Run BENCH-H6
Compare: baseline LLM (no braid provenance) vs. LLM + evidence braid.
Measure improvement on defined metrics.

### Step 4: Publish results
Whether H6 is confirmed or falsified, publish the methodology and results.

---

## Open Questions

1. Can braid provenance be added to an existing LLM without retraining?
2. Does the provenance overhead outweigh the explainability benefit?
3. Can the authority braid replace or augment RLHF?
4. Does contradiction detection improve factual accuracy on defined benchmarks?

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*
