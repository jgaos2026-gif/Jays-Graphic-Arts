from __future__ import annotations

from .crossing import ExecutableCrossing
from .evidence import EvidenceLog
from .execution import BraidExecutor, ExecutionResult
from .state import StrandState


class ExecutableBraid:
    def __init__(
        self,
        strands: list[StrandState] | None = None,
        crossings: list[ExecutableCrossing] | None = None,
        evidence_log: EvidenceLog | None = None,
    ) -> None:
        self.strands = [strand.clone() for strand in (strands or [])]
        self.crossings = list(crossings or [])
        self.evidence_log = evidence_log or EvidenceLog()

    def add_crossing(self, crossing: ExecutableCrossing) -> "ExecutableBraid":
        self.crossings.append(crossing)
        return self

    def execute(self, executor: BraidExecutor | None = None) -> ExecutionResult:
        runner = executor or BraidExecutor()
        result = runner.run(self)
        self.evidence_log = result.evidence_log
        self.strands = [strand.clone() for strand in result.final_strands]
        return result

    def get_evidence(self) -> EvidenceLog:
        return self.evidence_log
