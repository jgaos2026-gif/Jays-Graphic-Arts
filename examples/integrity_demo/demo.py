from __future__ import annotations

import json
from pathlib import Path

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    MemoryOpcode,
    RoutingOpcode,
    StrandState,
    TrustLevel,
)


def build_braid(route_name: str) -> ExecutableBraid:
    braid = ExecutableBraid(
        strands=[
            StrandState(value={"counter": 1, "payload": "trusted-seed"}, trust_level=TrustLevel.ACTIVE),
            StrandState(value={"mirror": True}, trust_level=TrustLevel.ACTIVE),
        ]
    )
    braid.add_crossing(
        ExecutableCrossing(
            tag="auth-check",
            family=InstructionFamily.AUTH,
            opcode=AuthOpcode.CHECK.value,
            strand_i=0,
            strand_j=1,
            operands={"required_scope": "execute"},
        )
    )
    braid.add_crossing(
        ExecutableCrossing(
            tag="verify-state",
            family=InstructionFamily.INTEG,
            opcode=IntegrityOpcode.VERIFY.value,
            strand_i=0,
            strand_j=1,
            operands={"predicate": lambda value: value["counter"] == 1},
        )
    )
    braid.add_crossing(
        ExecutableCrossing(
            tag="route-main",
            family=InstructionFamily.ROUTE,
            opcode=RoutingOpcode.SELECT.value,
            strand_i=0,
            strand_j=1,
            operands={
                "predicate": lambda value: value["counter"] > 0,
                "on_true": route_name,
                "on_false": "recovery-lane",
            },
        )
    )
    braid.add_crossing(
        ExecutableCrossing(
            tag="store-state",
            family=InstructionFamily.MEM,
            opcode=MemoryOpcode.STORE_HOT.value,
            strand_i=0,
            strand_j=1,
            operands={"key": "integrity-demo"},
        )
    )
    braid.add_crossing(
        ExecutableCrossing(
            tag="promote-state",
            family=InstructionFamily.INTEG,
            opcode=IntegrityOpcode.PROMOTE.value,
            strand_i=0,
            strand_j=1,
        )
    )
    return braid


def attach_authority(braid: ExecutableBraid, token) -> None:
    for strand in braid.strands:
        strand.authority_token = token


def main() -> None:
    base_dir = Path(__file__).parent
    authority_manager = AuthorityManager()
    executor = BraidExecutor(authority_manager)
    token = authority_manager.issue_token(role="EXECUTOR", scope=["execute", "verify", "store"])

    trusted_braid = build_braid("trusted-lane")
    attach_authority(trusted_braid, token)
    trusted_result = trusted_braid.execute(executor)

    state_path = base_dir / "trusted_state.json"
    evidence_path = base_dir / "trusted_evidence.json"
    state_path.write_text(json.dumps([strand.to_dict() for strand in trusted_result.final_strands], indent=2), encoding="utf-8")
    evidence_path.write_text(json.dumps(trusted_result.evidence_log.to_dicts(), indent=2), encoding="utf-8")

    tampered_braid = build_braid("tampered-lane")
    attach_authority(tampered_braid, token)
    replay_result = executor.replay(tampered_braid, tampered_braid.strands, trusted_result)

    report = {
        "phase": "integrity_demo",
        "trusted_state_path": str(state_path),
        "trusted_evidence_path": str(evidence_path),
        "trusted_execution": trusted_result.proof_report,
        "tampered_replay": replay_result.proof_report,
    }
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
