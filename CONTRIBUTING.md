# Contributing to Braided Computational Topology

Thank you for your interest in contributing to the BCT research program.

This is an active research project. Contributions are welcome across multiple dimensions.

---

## Ways to Contribute

### 1. Mathematical Review

The most valuable contributions are independent mathematical reviews of:

- Definitions in `mathematics/`
- Proofs in `proofs/`
- Invariant definitions in `mathematics/INVARIANTS.md`

If you identify errors, ambiguities, or improvements, open an issue with a precise description.

### 2. Architecture Review

Review documents in `architecture/` for:

- Internal consistency
- Completeness of definitions
- Missing edge cases
- Alternative formulations

### 3. Implementation

See `implementation/` for prototype and simulator work. Contributions welcome in:

- Simulator development
- Prototype extensions
- Benchmark implementations
- Example programs

### 4. Research Questions

If you have new research questions, hypotheses, or related work not yet referenced, open an issue or pull request updating:

- `research/OPEN_PROBLEMS.md`
- `research/HYPOTHESES.md`
- `docs/REFERENCES.md`

### 5. Documentation

Corrections, clarifications, and improvements to any documentation file are welcome.

---

## Contribution Standards

### Honesty of Claims

All contributions must clearly distinguish:

- **Established** — prior mathematical or computational work, with citation
- **Original** — new contributions from this project, clearly labeled
- **Hypothetical** — conjectures and open questions, clearly labeled

Do not submit contributions that blur these distinctions.

### Commit Messages

Use clear, descriptive commit messages:

```
Add formal definition of authority crossing in AUTHORITY.md
Fix invariant proof in proofs/AUTHORITY_INVARIANT.md
Add open problem: braid compression lower bounds
```

### Pull Requests

- Reference the specific document(s) modified
- Describe the change and its justification
- For mathematical changes, provide a brief argument for correctness
- For new hypotheses, label them explicitly as unverified

---

## Review Process

All pull requests will be reviewed for:

1. Accuracy of claims
2. Consistency with existing definitions
3. Appropriate distinction between established and original work
4. Formatting and clarity

---

## Setting Up Locally

```bash
git clone https://github.com/jgaos2026-gif/braided-computational-topology.git
cd braided-computational-topology
```

No build system is required for documentation contributions.

For implementation contributions, see `implementation/README.md` (forthcoming).

---

## Questions

Open an issue with the label `question` for any questions about the research or the repository.
