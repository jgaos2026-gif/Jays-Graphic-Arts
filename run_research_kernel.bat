@echo off
REM BCT Research Kernel — One-command setup and verification
REM John E. Arenz — JGA Enterprises, Mendota, Illinois

echo === Braided Computational Topology — Research Kernel ===
echo === Author: John E. Arenz, JGA Enterprises, Mendota IL ===
echo.

echo [1/4] Creating virtual environment...
python -m venv .venv
call .venv\Scripts\Activate.ps1

echo [2/4] Installing BCT simulator...
pip install -e ".[dev]" --quiet

echo [3/4] Running test suite...
pytest tests\ -v

echo [4/4] Running integrity demo...
python -m braid_simulator examples\integrity_demo

echo.
echo === Research Kernel verified. ===
echo Run 'python -m braid_simulator examples\routing_demo' for routing demo.
echo See PROJECT_STATUS.md for current implementation status.
echo See CLAIMS_REGISTER.md for all claim classifications.
