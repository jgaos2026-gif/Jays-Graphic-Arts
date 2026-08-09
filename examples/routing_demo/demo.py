from __future__ import annotations

import json

from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    RoutingOpcode,
    StrandState,
)


def main() -> None:
    manager = AuthorityManager()
    token = manager.issue_token(role="ROUTER", scope=["execute"])
    braid = ExecutableBraid(
        strands=[
            StrandState(value={"counter": 2}, authority_token=token),
            StrandState(value={"counter": 0}, authority_token=token),
        ]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda value: value["counter"] >= 0}))
    braid.add_crossing(ExecutableCrossing("fork", InstructionFamily.ROUTE, RoutingOpcode.FORK.value, 0, 1))
    braid.add_crossing(ExecutableCrossing("join", InstructionFamily.ROUTE, RoutingOpcode.JOIN.value, 0, 1))
    result = braid.execute(BraidExecutor(manager))
    print(json.dumps({
        "phase": "routing_demo",
        "trust_levels": [strand.trust_level.value for strand in result.final_strands],
        "evidence_length": len(result.evidence_log),
        "state": [strand.to_dict() for strand in result.final_strands],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
