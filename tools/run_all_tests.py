#!/usr/bin/env python3
"""Run full test suite with clear output."""
import subprocess, sys
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.exit(result.returncode)
