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


def build_braid(token) -> ExecutableBraid:
    braid = ExecutableBraid(
        strands=[StrandState(value={"counter": 3}, authority_token=token), StrandState(value={"mirror": True}, authority_token=token)]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda value: value["counter"] == 3}))
    braid.add_crossing(ExecutableCrossing("store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1, operands={"key": "replay"}))
    return braid


def test_replay_is_deterministic_against_reference_evidence() -> None:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"])
    executor = BraidExecutor(manager)

    reference = build_braid(token).execute(executor)
    replay = executor.replay(build_braid(token), build_braid(token).strands, reference)

    assert replay.tampered is False
    assert replay.evidence_log.to_dicts() == reference.evidence_log.to_dicts()
