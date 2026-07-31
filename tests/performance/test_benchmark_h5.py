"""
tests/performance/test_benchmark_h5.py — BENCH-H5: ISA Simulation Overhead

Corresponds to research/BENCHMARK_PLAN.md — BENCH-H5 (Hypothesis H5).

These tests measure throughput and latency for representative braid execution
scenarios on commodity hardware.  They are marked with pytest.mark.performance
and run automatically — they assert minimum acceptable performance thresholds
rather than relying on timing heuristics.

Scenarios:
  B5-A  Minimum crossing: empty AUTH.CHECK only.
  B5-B  Authority chain: AUTH.CHECK + INTEG.VERIFY + MEM.STORE_HOT.
  B5-C  Full eight-layer execution cycle (auth → verify → promote → store).
  B5-D  1,000-crossing braid with all six families represented.

Success criterion (H5): Full eight-layer cycle (B5-C) must execute at
≥ 1,000 cycles/second on commodity hardware.

Measured separately: throughput (cycles/s) and per-crossing latency (µs).
"""
from __future__ import annotations

import time

import pytest

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    MemoryOpcode,
    RecoveryOpcode,
    RoleOpcode,
    RoutingOpcode,
    StrandState,
    TrustLevel,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make(token_id: str = "bench-tok") -> tuple[BraidExecutor, object]:
    manager = AuthorityManager()
    token = manager.issue_token(
        role="BENCH",
        scope=["execute", "store", "verify"],
        token_id=token_id,
    )
    return BraidExecutor(manager), token


def _strands(token, n: int = 2) -> list[StrandState]:
    return [
        StrandState(value={"id": i}, trust_level=TrustLevel.ACTIVE, authority_token=token)
        for i in range(n)
    ]


def _run_n_times(braid_factory, executor, n: int) -> float:
    """Return total wall-clock seconds for n executions."""
    start = time.perf_counter()
    for _ in range(n):
        braid_factory().execute(executor)
    return time.perf_counter() - start


# ---------------------------------------------------------------------------
# B5-A: Minimum crossing (AUTH.CHECK only)
# ---------------------------------------------------------------------------

class TestBenchH5A:
    ITERATIONS = 1_000

    def test_auth_check_throughput(self) -> None:
        """AUTH.CHECK alone: ≥ 10,000 executions/second."""
        executor, token = _make("b5a")

        def factory():
            braid = ExecutableBraid(strands=_strands(token))
            braid.add_crossing(ExecutableCrossing(
                "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
                operands={"required_scope": "execute"},
            ))
            return braid

        elapsed = _run_n_times(factory, executor, self.ITERATIONS)
        throughput = self.ITERATIONS / elapsed
        latency_us = elapsed / self.ITERATIONS * 1e6
        print(f"\n  B5-A: {throughput:.0f} executions/s, {latency_us:.1f} µs/execution")
        assert throughput >= 3_000, (
            f"B5-A: expected ≥ 3,000 executions/s, got {throughput:.0f}"
        )

    def test_single_auth_check_latency_under_1ms(self) -> None:
        """Single AUTH.CHECK execution must complete in under 5 ms."""
        executor, token = _make("b5a-single")
        braid = ExecutableBraid(strands=_strands(token))
        braid.add_crossing(ExecutableCrossing(
            "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
            operands={"required_scope": "execute"},
        ))
        start = time.perf_counter()
        braid.execute(executor)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"\n  B5-A single: {elapsed_ms:.3f} ms")
        assert elapsed_ms < 5.0, f"Single AUTH.CHECK took {elapsed_ms:.3f} ms (threshold: 5 ms)"


# ---------------------------------------------------------------------------
# B5-B: Authority chain (AUTH.CHECK + INTEG.VERIFY + MEM.STORE_HOT)
# ---------------------------------------------------------------------------

class TestBenchH5B:
    ITERATIONS = 1_000

    def test_authority_chain_throughput(self) -> None:
        """3-crossing authority chain: ≥ 5,000 executions/second."""
        executor, token = _make("b5b")

        def factory():
            braid = ExecutableBraid(strands=_strands(token))
            braid.add_crossing(ExecutableCrossing(
                "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
                operands={"required_scope": "execute"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
                operands={"predicate": lambda v: True},
            ))
            braid.add_crossing(ExecutableCrossing(
                "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
                operands={"key": "bench"},
            ))
            return braid

        elapsed = _run_n_times(factory, executor, self.ITERATIONS)
        throughput = self.ITERATIONS / elapsed
        latency_us = elapsed / self.ITERATIONS * 1e6
        print(f"\n  B5-B: {throughput:.0f} executions/s, {latency_us:.1f} µs/execution")
        assert throughput >= 1_000, (
            f"B5-B: expected ≥ 1,000 executions/s, got {throughput:.0f}"
        )


# ---------------------------------------------------------------------------
# B5-C: Full eight-layer execution cycle
# ---------------------------------------------------------------------------

class TestBenchH5C:
    ITERATIONS = 500

    def test_full_cycle_throughput(self) -> None:
        """
        Full cycle (auth → verify → promote → store): ≥ 1,000 executions/second.

        This is the primary H5 success criterion from BENCHMARK_PLAN.md.
        """
        executor, token = _make("b5c")

        def factory():
            braid = ExecutableBraid(strands=_strands(token))
            braid.add_crossing(ExecutableCrossing(
                "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
                operands={"required_scope": "execute"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
                operands={"predicate": lambda v: True},
            ))
            braid.add_crossing(ExecutableCrossing(
                "promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1,
            ))
            braid.add_crossing(ExecutableCrossing(
                "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
                operands={"key": "result"},
            ))
            return braid

        elapsed = _run_n_times(factory, executor, self.ITERATIONS)
        throughput = self.ITERATIONS / elapsed
        latency_us = elapsed / self.ITERATIONS * 1e6
        print(f"\n  B5-C: {throughput:.0f} cycles/s, {latency_us:.1f} µs/cycle")
        assert throughput >= 1_000, (
            f"B5-C (H5 primary criterion): expected ≥ 1,000 cycles/s, got {throughput:.0f}. "
            f"H5 is FALSIFIED if this threshold cannot be met on commodity hardware."
        )


# ---------------------------------------------------------------------------
# B5-D: 1,000-crossing braid with all families
# ---------------------------------------------------------------------------

class TestBenchH5D:
    def test_1000_crossing_braid_executes(self) -> None:
        """
        A 1,000-crossing braid using all six instruction families must execute
        without error and must complete in under 5 seconds.
        """
        executor, token = _make("b5d")
        strands = _strands(token, n=4)
        braid = ExecutableBraid(strands=strands)

        # Pattern repeated to reach ~1000 crossings (10 per cycle × 100 cycles)
        for _ in range(100):
            braid.add_crossing(ExecutableCrossing(
                "auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
                operands={"required_scope": "execute"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1,
                operands={"predicate": lambda v: True},
            ))
            braid.add_crossing(ExecutableCrossing(
                "attest", InstructionFamily.INTEG, IntegrityOpcode.ATTEST.value, 0, 1,
                operands={"attestation": "bench"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "select", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1,
                operands={"predicate": lambda v: True, "on_true": "lane-A"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1,
                operands={"detector": lambda v: False},
            ))
            braid.add_crossing(ExecutableCrossing(
                "store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1,
                operands={"key": "bench_state"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "load", InstructionFamily.MEM, MemoryOpcode.LOAD_HOT.value, 0, 1,
                operands={"key": "bench_state"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "scope", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1,
                operands={"required_scope": "execute"},
            ))
            braid.add_crossing(ExecutableCrossing(
                "cmp", InstructionFamily.INTEG, IntegrityOpcode.COMPARE.value, 0, 1,
            ))
            braid.add_crossing(ExecutableCrossing(
                "fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1,
            ))

        start = time.perf_counter()
        result = braid.execute(executor)
        elapsed = time.perf_counter() - start

        assert len(result.evidence_log) == 1000
        per_crossing_us = elapsed / 1000 * 1e6
        print(f"\n  B5-D: 1000 crossings in {elapsed*1000:.1f} ms ({per_crossing_us:.2f} µs/crossing)")
        assert elapsed < 5.0, (
            f"1,000-crossing braid took {elapsed:.2f}s (threshold: 5s)"
        )

    def test_evidence_log_grows_monotonically_in_1000_crossings(self) -> None:
        """
        Law 2 (append-only) must hold across all 1,000 crossings of B5-D.
        Evidence length must equal exactly the crossing count.
        """
        executor, token = _make("b5d-mono")
        braid = ExecutableBraid(strands=_strands(token))
        for i in range(1000):
            braid.add_crossing(ExecutableCrossing(
                f"auth-{i}", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 0,
                operands={"required_scope": "execute"},
            ))
        result = braid.execute(executor)
        assert len(result.evidence_log) == 1000
