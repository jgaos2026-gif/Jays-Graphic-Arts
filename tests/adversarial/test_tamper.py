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


def build_braid(route_name: str, token) -> ExecutableBraid:
    braid = ExecutableBraid(
        strands=[
            StrandState(value={"counter": 1}, trust_level=TrustLevel.ACTIVE, authority_token=token),
            StrandState(value={"peer": True}, trust_level=TrustLevel.ACTIVE, authority_token=token),
        ]
    )
    braid.add_crossing(ExecutableCrossing("auth", InstructionFamily.AUTH, AuthOpcode.CHECK.value, 0, 1, operands={"required_scope": "execute"}))
    braid.add_crossing(ExecutableCrossing("verify", InstructionFamily.INTEG, IntegrityOpcode.VERIFY.value, 0, 1, operands={"predicate": lambda value: value["counter"] == 1}))
    braid.add_crossing(ExecutableCrossing("route", InstructionFamily.ROUTE, RoutingOpcode.SELECT.value, 0, 1, operands={"predicate": lambda value: True, "on_true": route_name, "on_false": "bad"}))
    braid.add_crossing(ExecutableCrossing("store", InstructionFamily.MEM, MemoryOpcode.STORE_HOT.value, 0, 1, operands={"key": "tamper"}))
    return braid


def test_tampered_replay_is_detected_and_quarantined() -> None:
    manager = AuthorityManager()
    token = manager.issue_token(role="EXECUTOR", scope=["execute"])
    executor = BraidExecutor(manager)

    trusted = build_braid("trusted", token).execute(executor)
    tampered = build_braid("tampered", token)
    replay = executor.replay(tampered, tampered.strands, trusted)

    assert replay.tampered is True
    assert replay.divergence_tag == "route"
    assert "route" in replay.quarantined_tags
    assert replay.recovered is True
    assert replay.final_strands[0].trust_level in {TrustLevel.TRUSTED, TrustLevel.CERTIFIED}
