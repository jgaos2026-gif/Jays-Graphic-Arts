# Research History

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Origin

Braided Computational Topology originated from a sustained investigation into the structural limitations of conventional computational architectures, particularly as they relate to:

- History preservation in long-running systems
- Authority tracking across distributed execution
- Recovery with evidence preservation
- Provenance in AI reasoning systems

The observation that motivated the research was simple: modern architectures are optimized to answer *where information ends up*, but many of the most difficult problems in systems engineering require knowing *how information got there*.

This gap between what architectures discard and what engineers need to reconstruct drove the investigation of whether an alternative structural model could preserve that history natively.

---

## Key Intellectual Steps

### Step 1 — Identifying the Structural Gap

The first step was recognizing that history preservation, authority tracking, and verification completeness are consistently treated as software-layer additions in conventional architectures — not architectural properties.

This is not a flaw. It is a correct design choice for general-purpose computation.

The research question became: *for computation classes where these properties are mandatory, is there a structural substrate that carries them natively?*

### Step 2 — Braid Groups as a Candidate Structure

Braid groups preserve exactly what conventional architectures discard: ordered interaction, crossing history, and structural consequence. Two braids with identical closures (final states) can have completely different strand histories.

This made braid groups a natural candidate structure for investigation.

### Step 3 — Executable Crossings

Classical braid groups are passive mathematical objects. The crossings record relationships but perform no work.

The key original idea was: *what if crossings are executable?* What if each crossing carries an instruction that performs computational work?

This transformation — from passive mathematical structure to active computational substrate — is the core original contribution of BCT.

### Step 4 — Instruction Families

Rather than one universal executable braid, the research identified that different computational purposes require different crossing behaviors. This led to the definition of six instruction families: Integrity, Routing, Recovery, Role Exchange, Authority, and Memory.

### Step 5 — Architectural Specification

With the instruction families defined, the layered computational architecture was specified: eight layers from Input through Evidence, each implemented as a braid topology.

### Step 6 — Repository and Documentation

The research is documented in this repository as a research prototype. The goal is to provide sufficient precision for independent review, reproduction, and falsification.

---

## What Has Not Changed

The core observation has remained constant: braids preserve interaction history structurally. Everything else — the instruction families, the architecture, the laws, the ISA — has been refined through iteration.

The governing philosophy has not changed: *novelty is insufficient. The research must be testable, measurable, and reproducible.*

---

## What Remains Open

The history of this research is incomplete. The following are open:

- Independent mathematical validation of the formal definitions
- Empirical benchmark results
- Peer review
- Determination of which hypotheses are validated, which require revision, and which are falsified

The history of this research will be updated as these milestones are reached.

---

*John E. Arenz — JGA Enterprises, Mendota, Illinois*  
*Braided Computational Topology, Version 1.0, 2026*
