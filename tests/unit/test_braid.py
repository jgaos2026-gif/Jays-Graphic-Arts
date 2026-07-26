from braid_simulator import (
    AuthOpcode,
    AuthorityManager,
    BraidExecutor,
    ExecutableBraid,
    ExecutableCrossing,
    InstructionFamily,
    IntegrityOpcode,
    MemoryOpcode,
    StrandState,
)


def test_braid_composition_records_evidence_in_order() -> None:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"])
    braid = ExecutableBraid(
        strands=[StrandState(value={"x": 1}, authority_token=token), StrandState(value={"y": 2}, authority_token=token)]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda value: value["x"] == 1}))
    braid.add_crossing(ExecutableCrossing("store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1, operands={"key": "k"}))

    result = braid.execute(BraidExecutor(manager))

    assert [record.tag for record in result.evidence_log] == ["auth", "verify", "store"]
    assert braid.get_evidence().to_dicts() == result.evidence_log.to_dicts()
