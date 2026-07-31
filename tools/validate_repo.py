#!/usr/bin/env python3
"""Validate BCT repository structure and cross-references."""
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

required = [
    "README.md", "LICENSE", "CITATION.cff", "CLAIMS_REGISTER.md",
    "ORIGINALITY_BOUNDARY.md", "PROJECT_STATUS.md",
    "manifesto/WHY_MANY_BRAIDS.md", "manifesto/BRAIDED_TOPOLOGY_MANIFESTO.md",
    "braid_catalog/README.md", "isa/OPCODES.md",
    "theory/PROOF_OBLIGATIONS.md", "theory/AXIOMS.md",
    "braid_simulator/__init__.py", "pyproject.toml",
]

missing = [f for f in required if not os.path.exists(os.path.join(BASE, f))]
if missing:
    print("MISSING FILES:")
    for f in missing:
        print(f"  ✗ {f}")
    sys.exit(1)
else:
    print(f"✓ All {len(required)} required files present.")
    sys.exit(0)
