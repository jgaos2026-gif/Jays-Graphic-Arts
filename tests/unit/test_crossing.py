from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    StrandState,
    TrustLevel,
)


def test_crossings_execute_and_promote_state() -> None:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"])
    braid = ExecutableBraid(
        strands=[
            StrandState(value={"counter": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"shadow": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda value: value["counter"] == 1}))
    braid.add_crossing(ExecutableCrossing("promote", InstructionFamily.INTEG, IntegrityOpcode.PROMOTE.value, 0, 1))

    result = braid.execute(BraidExecutor(manager))

    assert result.final_strands[0].trust_level == TrustLevel.CERTIFIED
    assert [record.tag for record in result.evidence_log] == ["auth", "verify", "promote"]
