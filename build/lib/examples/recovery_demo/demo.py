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
    RecoveryOpcode,
    StrandState,
    TrustLevel,
)


def main() -> None:
    manager = AuthorityManager()
    token = manager.issue_token(role="RECOVER", scope=["execute"])
    braid = ExecutableBraid(
        strands=[
            StrandState(value={"counter": 9}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"checkpoint": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda value: value["counter"] == 9}))
    braid.add_crossing(ExecutableCrossing("detect", InstructionFamily.RECOV, RecoveryOpcode.DETECT.value, 0, 1, operands={"detector": lambda value: value["counter"] > 5}))
    braid.add_crossing(ExecutableCrossing("quarantine", InstructionFamily.RECOV, RecoveryOpcode.QUARANTINE.value, 0, 1))
    braid.add_crossing(ExecutableCrossing("restore", InstructionFamily.RECOV, RecoveryOpcode.RESTORE.value, 0, 1, operands={"checkpoint_tag": "verify"}))
    result = braid.execute(BraidExecutor(manager))
    print(json.dumps({
        "phase": "recovery_demo",
        "quarantined_tags": result.quarantined_tags,
        "final_trust_levels": [strand.trust_level.value for strand in result.final_strands],
        "evidence_length": len(result.evidence_log),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
