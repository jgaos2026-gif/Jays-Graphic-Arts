from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .authority import AuthorityManager
from .crossing import ExecutableCrossing
from .evidence import EvidenceLog, EvidenceRecord, stable_hash
from .instructions import InstructionFamily, RecoveryOpcode
from .state import StrandState, TrustLevel


class LawViolation(RuntimeError):
    pass


class TopologicalMismatchFault(LawViolation):
    """
    Raised when two braid words that should be equivalent reduce to different
    normal forms — i.e., the reordering is not an instance of far-commutativity
    or the braid relation and is therefore a topological fault.

    This is the exception that the verification engine emits for proof obligation PO-1.
    An adversary who reorders crossings in a way that satisfies the braid relation
    will NOT trigger this fault (that reordering is a legitimate Reidemeister move).
    An adversary who performs an illegal adjacent transposition WILL trigger it.
    """


@dataclass
class Checkpoint:
    tag: str
    timestamp: int
    strands: list[StrandState]
    evidence_length: int

    def clone(self) -> "Checkpoint":
        return Checkpoint(
            tag=self.tag,
            timestamp=self.timestamp,
            strands=[strand.clone() for strand in self.strands],
            evidence_length=self.evidence_length,
        )


@dataclass
class ExecutionResult:
    final_strands: list[StrandState]
    evidence_log: EvidenceLog
    layer_trace: list[str]
    checkpoints: list[Checkpoint] = field(default_factory=list)
    memory: dict[str, Any] = field(default_factory=dict)
    tampered: bool = False
    divergence_index: int | None = None
    divergence_tag: str | None = None
    quarantined_tags: list[str] = field(default_factory=list)
    recovered: bool = False
    proof_report: dict[str, Any] = field(default_factory=dict)


class _ExecutionContext:
    def __init__(self, authority_manager: AuthorityManager, evidence_log: EvidenceLog) -> None:
        self.authority_manager = authority_manager
        self.evidence_log = evidence_log
        self.last_auth_result: dict[int, bool] = {}
        self.last_verify_result: dict[int, bool] = {}
        self.memory: dict[str, Any] = {
            "hot": {},
            "warm": {},
            "cold": {},
            "pockets": {},
            "stitches": [],
        }
        self.checkpoints: list[Checkpoint] = []
        self.quarantined_tags: list[str] = []
        self.archived: list[StrandState] = []
        self.anomalies: list[dict[str, Any]] = []
        self.route_decisions: dict[str, str] = {}
        self.current_timestamp = 0

    def law_violation(self, message: str) -> LawViolation:
        return LawViolation(message)

    def ensure_strand_index(self, index: int) -> None:
        if index < 0:
            raise self.law_violation("strand index must be non-negative")

    def stable_hash(self, value: Any) -> str:
        return stable_hash(value)

    def record_checkpoint(self, tag: str, strands: list[StrandState]) -> None:
        trusted_present = any(strand.trust_level in {TrustLevel.TRUSTED, TrustLevel.CERTIFIED} for strand in strands)
        if not trusted_present:
            return
        self.checkpoints.append(
            Checkpoint(
                tag=tag,
                timestamp=self.current_timestamp,
                strands=[strand.clone() for strand in strands],
                evidence_length=len(self.evidence_log) + 1,
            )
        )

    def replay_value(self, checkpoint_tag: str | None) -> StrandState:
        checkpoint = self._find_checkpoint(checkpoint_tag)
        return checkpoint.strands[0].clone()

    def restore_checkpoint(self, checkpoint_tag: str | None, before_index: int | None = None) -> list[StrandState]:
        if checkpoint_tag is not None:
            checkpoint = self._find_checkpoint(checkpoint_tag)
            return [strand.clone() for strand in checkpoint.strands]
        if before_index is not None:
            eligible = [checkpoint for checkpoint in self.checkpoints if checkpoint.evidence_length <= before_index]
            if eligible:
                return [strand.clone() for strand in eligible[-1].strands]
        if not self.checkpoints:
            raise self.law_violation("no checkpoint available for recovery")
        return [strand.clone() for strand in self.checkpoints[-1].strands]

    def _find_checkpoint(self, checkpoint_tag: str | None) -> Checkpoint:
        if checkpoint_tag is None:
            if not self.checkpoints:
                raise self.law_violation("no checkpoints recorded")
            return self.checkpoints[-1]
        for checkpoint in self.checkpoints:
            if checkpoint.tag == checkpoint_tag:
                return checkpoint
        raise self.law_violation(f"unknown checkpoint: {checkpoint_tag}")


GOVERNING_LAWS = {
    1: "No active state becomes trusted or certified without verification",
    2: "Evidence log is append-only",
    3: "Trusted executions are replay-deterministic",
    4: "AUTH.CHECK precedes any state promotion",
    5: "Recovery preserves evidence",
    6: "Trusted state has deterministic recovery",
    7: "No crossing may delete evidence records",
    8: "Verification precedes promotion",
    9: "Promoted strands must carry explicit authority",
    10: "Tampered replays quarantine before restore",
}


class BraidExecutor:
    LAYERS = [
        "INPUT",
        "AUTHORITY",
        "VERIFICATION",
        "EXECUTION",
        "RECOVERY",
        "CERTIFICATION",
        "PERSISTENCE",
        "EVIDENCE",
    ]

    def __init__(self, authority_manager: AuthorityManager | None = None) -> None:
        self.authority_manager = authority_manager or AuthorityManager()

    def run(
        self,
        braid: Any,
        initial_strands: list[StrandState] | None = None,
        evidence_log: EvidenceLog | None = None,
    ) -> ExecutionResult:
        strands = [strand.clone() for strand in (initial_strands or braid.strands)]
        log = evidence_log or EvidenceLog()
        context = _ExecutionContext(self.authority_manager, log)
        for index, crossing in enumerate(braid.crossings):
            context.current_timestamp = index
            before_len = len(log)
            relevant_input = self._relevant_states(strands, crossing)
            input_hash = stable_hash([state.to_dict() for state in relevant_input])
            try:
                result = crossing.execute(strands, context)
            except LawViolation:
                self._append_record(log, crossing, index, input_hash, input_hash, "FAIL")
                if len(log) < before_len + 1:
                    raise LawViolation("Law 2/Law 7: evidence must grow monotonically")
                raise
            relevant_output = self._relevant_states(strands, crossing)
            output_hash = stable_hash([state.to_dict() for state in relevant_output])
            self._append_record(log, crossing, index, input_hash, output_hash, result)
            if len(log) != before_len + 1:
                raise LawViolation("Law 2/Law 7: evidence log is append-only and may not shrink or skip")
        proof_report = self._build_proof_report(strands, log, False, None, None, context.quarantined_tags, False)
        return ExecutionResult(
            final_strands=[strand.clone() for strand in strands],
            evidence_log=log,
            layer_trace=list(self.LAYERS),
            checkpoints=[checkpoint.clone() for checkpoint in context.checkpoints],
            memory=context.memory,
            quarantined_tags=list(context.quarantined_tags),
            recovered=False,
            proof_report=proof_report,
        )

    def replay(
        self,
        braid: Any,
        initial_strands: list[StrandState],
        reference: ExecutionResult,
    ) -> ExecutionResult:
        replay_result = self.run(braid, initial_strands=initial_strands)
        divergence_index = None
        divergence_tag = None
        for index, (expected, actual) in enumerate(zip(reference.evidence_log, replay_result.evidence_log)):
            if (
                expected.tag,
                expected.family,
                expected.opcode,
                expected.input_hash,
                expected.output_hash,
                expected.result,
            ) != (
                actual.tag,
                actual.family,
                actual.opcode,
                actual.input_hash,
                actual.output_hash,
                actual.result,
            ):
                divergence_index = index
                divergence_tag = actual.tag
                break
        if divergence_index is None and len(reference.evidence_log) != len(replay_result.evidence_log):
            divergence_index = min(len(reference.evidence_log), len(replay_result.evidence_log))
            divergence_tag = braid.crossings[divergence_index].tag if divergence_index < len(braid.crossings) else "length-divergence"
        if divergence_index is not None:
            replay_result.tampered = True
            replay_result.divergence_index = divergence_index
            replay_result.divergence_tag = divergence_tag
            crossing = braid.crossings[min(divergence_index, len(braid.crossings) - 1)]
            target = replay_result.final_strands[crossing.strand_i]
            target.trust_level = TrustLevel.QUARANTINED
            target.history.append(f"quarantine:{crossing.tag}")
            replay_result.quarantined_tags.append(crossing.tag)
            quarantine_hash = stable_hash(target.to_dict())
            replay_result.evidence_log.append(
                EvidenceRecord(
                    tag=f"quarantine:{crossing.tag}",
                    family=InstructionFamily.RECOV.value,
                    opcode=RecoveryOpcode.QUARANTINE.value,
                    timestamp=len(replay_result.evidence_log),
                    strand_i=crossing.strand_i,
                    strand_j=crossing.strand_j,
                    input_hash=quarantine_hash,
                    output_hash=quarantine_hash,
                    result="QUARANTINED",
                )
            )
            checkpoint = self._checkpoint_before(reference.checkpoints, divergence_index + 1)
            if checkpoint is not None:
                replay_result.final_strands = [strand.clone() for strand in checkpoint.strands]
                replay_result.final_strands[crossing.strand_i].history.append(f"restore:{checkpoint.tag}")
                restore_hash = stable_hash([strand.to_dict() for strand in replay_result.final_strands])
                replay_result.evidence_log.append(
                    EvidenceRecord(
                        tag=f"restore:{checkpoint.tag}",
                        family=InstructionFamily.RECOV.value,
                        opcode=RecoveryOpcode.RESTORE.value,
                        timestamp=len(replay_result.evidence_log),
                        strand_i=crossing.strand_i,
                        strand_j=crossing.strand_j,
                        input_hash=restore_hash,
                        output_hash=restore_hash,
                        result="PASS",
                    )
                )
                replay_result.recovered = True
        replay_result.proof_report = self._build_proof_report(
            replay_result.final_strands,
            replay_result.evidence_log,
            replay_result.tampered,
            replay_result.divergence_index,
            replay_result.divergence_tag,
            replay_result.quarantined_tags,
            replay_result.recovered,
        )
        return replay_result

    def _checkpoint_before(self, checkpoints: list[Checkpoint], evidence_index: int) -> Checkpoint | None:
        eligible = [checkpoint for checkpoint in checkpoints if checkpoint.evidence_length <= evidence_index]
        return eligible[-1].clone() if eligible else None

    def _append_record(
        self,
        log: EvidenceLog,
        crossing: ExecutableCrossing,
        timestamp: int,
        input_hash: str,
        output_hash: str,
        result: str,
    ) -> None:
        log.append(
            EvidenceRecord(
                tag=crossing.tag,
                family=crossing.family.value,
                opcode=crossing.opcode,
                timestamp=timestamp,
                strand_i=crossing.strand_i,
                strand_j=crossing.strand_j,
                input_hash=input_hash,
                output_hash=output_hash,
                result=result,
            )
        )

    def _relevant_states(self, strands: list[StrandState], crossing: ExecutableCrossing) -> list[StrandState]:
        indices = [crossing.strand_i]
        if crossing.strand_j != crossing.strand_i:
            indices.append(crossing.strand_j)
        return [strands[index].clone() for index in indices if index < len(strands)]

    def _build_proof_report(
        self,
        strands: list[StrandState],
        evidence_log: EvidenceLog,
        tampered: bool,
        divergence_index: int | None,
        divergence_tag: str | None,
        quarantined_tags: list[str],
        recovered: bool,
    ) -> dict[str, Any]:
        return {
            "tampered": tampered,
            "divergence_index": divergence_index,
            "divergence_tag": divergence_tag,
            "quarantined_tags": list(quarantined_tags),
            "recovered": recovered,
            "final_trust_levels": [strand.trust_level.value for strand in strands],
            "evidence_length": len(evidence_log),
            "state_hash": stable_hash([strand.to_dict() for strand in strands]),
            "laws_enforced": GOVERNING_LAWS,
        }
