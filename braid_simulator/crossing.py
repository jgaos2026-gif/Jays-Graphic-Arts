from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .instructions import (
    AuthOpcode,
    InstructionFamily,
    IntegrityOpcode,
    MemoryOpcode,
    RecoveryOpcode,
    RoleOpcode,
    RoutingOpcode,
)
from .state import StrandState, TrustLevel


class CrossingDirection(str, Enum):
    OVER = "OVER"
    UNDER = "UNDER"


@dataclass
class ExecutableCrossing:
    tag: str
    family: InstructionFamily | str
    opcode: str
    strand_i: int
    strand_j: int = 0
    direction: str = CrossingDirection.OVER
    operands: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.family = InstructionFamily(str(self.family))
        self.opcode = str(self.opcode)
        if self.direction not in {CrossingDirection.OVER, CrossingDirection.UNDER}:
            raise ValueError(f"unsupported crossing direction: {self.direction}")

    def execute(self, strands: list[StrandState], context: Any) -> str:
        context.ensure_strand_index(self.strand_i)
        context.ensure_strand_index(self.strand_j)
        if self.family == InstructionFamily.AUTH:
            return _execute_auth(self, strands, context)
        if self.family == InstructionFamily.INTEG:
            return _execute_integ(self, strands, context)
        if self.family == InstructionFamily.ROUTE:
            return _execute_route(self, strands, context)
        if self.family == InstructionFamily.RECOV:
            return _execute_recovery(self, strands, context)
        if self.family == InstructionFamily.ROLE:
            return _execute_role(self, strands, context)
        if self.family == InstructionFamily.MEM:
            return _execute_memory(self, strands, context)
        raise context.law_violation(f"unsupported instruction family: {self.family}")


def _touch(state: StrandState, tag: str) -> None:
    state.history.append(tag)


def _resolve_token(state: StrandState, context: Any) -> Any:
    """
    Return the live (manager-registry) version of a strand's authority token.

    AuthorityToken is an immutable value object.  When revoke_token() is called,
    the manager creates a new revoked object and replaces the registry entry, but
    strands that were cloned before revocation hold the old snapshot.  This helper
    consults the manager's registry so that all Law-9 checks always reflect the
    current revocation status.
    """
    token = state.authority_token
    if token is None:
        return None
    live = context.authority_manager.get_token(token.id)
    return live if live is not None else token


def _execute_auth(crossing: ExecutableCrossing, strands: list[StrandState], context: Any) -> str:
    state_i = strands[crossing.strand_i]
    opcode = AuthOpcode(crossing.opcode)
    if opcode in {AuthOpcode.CHECK, AuthOpcode.GATE}:
        required_scope = crossing.operands.get("required_scope", "execute")
        passed = context.authority_manager.check_scope(state_i.authority_token, required_scope)
        context.last_auth_result[crossing.strand_i] = passed
        _touch(state_i, crossing.tag)
        return "PASS" if passed else "FAIL"
    if opcode == AuthOpcode.INHERIT:
        if state_i.authority_token is None:
            raise context.law_violation("AUTH.INHERIT requires a parent authority token")
        delegated = context.authority_manager.delegate_token(
            state_i.authority_token,
            scope=crossing.operands.get("scope", state_i.authority_token.scope),
            role=crossing.operands.get("role"),
        )
        strands[crossing.strand_j].authority_token = delegated
        _touch(state_i, crossing.tag)
        _touch(strands[crossing.strand_j], crossing.tag)
        return "PASS"
    if opcode == AuthOpcode.SCOPE:
        if state_i.authority_token is None:
            raise context.law_violation("AUTH.SCOPE requires an authority token")
        scoped = context.authority_manager.delegate_token(
            state_i.authority_token,
            scope=crossing.operands["scope"],
            role=state_i.authority_token.role,
        )
        state_i.authority_token = scoped
        _touch(state_i, crossing.tag)
        return "PASS"
    raise context.law_violation(f"unsupported AUTH opcode: {crossing.opcode}")


def _execute_integ(crossing: ExecutableCrossing, strands: list[StrandState], context: Any) -> str:
    state_i = strands[crossing.strand_i]
    opcode = IntegrityOpcode(crossing.opcode)
    if opcode == IntegrityOpcode.VERIFY:
        live_token = _resolve_token(state_i, context)
        if live_token is None or live_token.revoked:
            raise context.law_violation("Law 9: verified strands require an explicit non-revoked authority token")
        if not context.last_auth_result.get(crossing.strand_i, False):
            raise context.law_violation("Law 4: AUTH.CHECK must precede INTEG.VERIFY")
        predicate = crossing.operands.get("predicate")
        expected_hash = crossing.operands.get("expected_hash")
        passed = True
        if callable(predicate):
            passed = bool(predicate(state_i.value))
        elif expected_hash is not None:
            passed = context.stable_hash(state_i.value) == expected_hash
        if passed:
            if state_i.trust_level == TrustLevel.ACTIVE:
                state_i.trust_level = TrustLevel.TRUSTED
            context.last_verify_result[crossing.strand_i] = True
            context.record_checkpoint(crossing.tag, strands)
            _touch(state_i, crossing.tag)
            return "PASS"
        context.last_verify_result[crossing.strand_i] = False
        _touch(state_i, crossing.tag)
        return "FAIL"
    if opcode == IntegrityOpcode.PROMOTE:
        if state_i.trust_level == TrustLevel.ACTIVE:
            raise context.law_violation("Law 1: active state cannot be promoted without INTEG.VERIFY")
        live_token = _resolve_token(state_i, context)
        if live_token is None or live_token.revoked:
            raise context.law_violation("Law 9: promoted strands require an explicit non-revoked authority token")
        if not context.last_auth_result.get(crossing.strand_i, False):
            raise context.law_violation("Law 4: AUTH.CHECK must precede state promotion")
        if not context.last_verify_result.get(crossing.strand_i, False):
            raise context.law_violation("Law 1: promotion requires prior successful INTEG.VERIFY")
        state_i.trust_level = TrustLevel.CERTIFIED
        context.record_checkpoint(crossing.tag, strands)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == IntegrityOpcode.ATTEST:
        attestation = crossing.operands.get("attestation", "self")
        if isinstance(state_i.value, dict):
            state_i.value = {**state_i.value, "attestation": attestation}
        else:
            state_i.value = {"value": state_i.value, "attestation": attestation}
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == IntegrityOpcode.SEAL:
        if state_i.trust_level == TrustLevel.ACTIVE:
            raise context.law_violation("Law 1: active state cannot be sealed without verification")
        live_token = _resolve_token(state_i, context)
        if live_token is None or live_token.revoked:
            raise context.law_violation("Law 9: sealed strands require an explicit non-revoked authority token")
        if not context.last_auth_result.get(crossing.strand_i, False):
            raise context.law_violation("Law 4: AUTH.CHECK must precede state promotion")
        state_i.trust_level = TrustLevel.CERTIFIED
        context.record_checkpoint(crossing.tag, strands)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == IntegrityOpcode.COMPARE:
        passed = context.stable_hash(strands[crossing.strand_i].value) == context.stable_hash(strands[crossing.strand_j].value)
        _touch(strands[crossing.strand_i], crossing.tag)
        _touch(strands[crossing.strand_j], crossing.tag)
        return "PASS" if passed else "FAIL"
    raise context.law_violation(f"unsupported INTEG opcode: {crossing.opcode}")


def _execute_route(crossing: ExecutableCrossing, strands: list[StrandState], context: Any) -> str:
    state_i = strands[crossing.strand_i]
    opcode = RoutingOpcode(crossing.opcode)
    if opcode == RoutingOpcode.SELECT:
        predicate = crossing.operands.get("predicate", lambda value: True)
        route = crossing.operands.get("on_true", "primary") if predicate(state_i.value) else crossing.operands.get("on_false", "recovery")
        if isinstance(state_i.value, dict):
            state_i.value = {**state_i.value, "route": route}
        else:
            state_i.value = {"value": state_i.value, "route": route}
        context.route_decisions[crossing.tag] = route
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == RoutingOpcode.FORK:
        strands[crossing.strand_j] = state_i.clone()
        _touch(state_i, crossing.tag)
        _touch(strands[crossing.strand_j], crossing.tag)
        return "PASS"
    if opcode == RoutingOpcode.JOIN:
        left = strands[crossing.strand_i].value
        right = strands[crossing.strand_j].value
        merge_fn = crossing.operands.get("merge_fn")
        strands[crossing.strand_i].value = merge_fn(left, right) if callable(merge_fn) else {"left": left, "right": right}
        _touch(strands[crossing.strand_i], crossing.tag)
        _touch(strands[crossing.strand_j], crossing.tag)
        return "PASS"
    if opcode == RoutingOpcode.REDIRECT:
        destination = crossing.operands.get("destination", "alternate")
        if isinstance(state_i.value, dict):
            state_i.value = {**state_i.value, "redirected_to": destination}
        else:
            state_i.value = {"value": state_i.value, "redirected_to": destination}
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == RoutingOpcode.REPLAY:
        replay_value = context.replay_value(crossing.operands.get("checkpoint_tag"))
        strands[crossing.strand_i] = replay_value.clone()
        _touch(strands[crossing.strand_i], crossing.tag)
        return "PASS"
    raise context.law_violation(f"unsupported ROUTE opcode: {crossing.opcode}")


def _execute_recovery(crossing: ExecutableCrossing, strands: list[StrandState], context: Any) -> str:
    state_i = strands[crossing.strand_i]
    opcode = RecoveryOpcode(crossing.opcode)
    if opcode == RecoveryOpcode.DETECT:
        detector = crossing.operands.get("detector")
        expected_hash = crossing.operands.get("expected_hash")
        anomaly = False
        if callable(detector):
            anomaly = bool(detector(state_i.value))
        elif expected_hash is not None:
            anomaly = context.stable_hash(state_i.value) != expected_hash
        context.anomalies.append({"tag": crossing.tag, "anomaly": anomaly})
        _touch(state_i, crossing.tag)
        return "FAIL" if anomaly else "PASS"
    if opcode == RecoveryOpcode.QUARANTINE:
        state_i.trust_level = TrustLevel.QUARANTINED
        context.quarantined_tags.append(crossing.tag)
        _touch(state_i, crossing.tag)
        return "QUARANTINED"
    if opcode == RecoveryOpcode.RESTORE:
        restored = context.restore_checkpoint(
            crossing.operands.get("checkpoint_tag"),
            before_index=crossing.operands.get("before_index"),
        )
        strands[:] = [item.clone() for item in restored]
        _touch(strands[crossing.strand_i], crossing.tag)
        return "PASS"
    if opcode == RecoveryOpcode.HEAL:
        repair_fn = crossing.operands.get("repair_fn")
        replacement = crossing.operands.get("replacement")
        if callable(repair_fn):
            state_i.value = repair_fn(state_i.value)
        elif replacement is not None:
            state_i.value = replacement
        state_i.trust_level = TrustLevel.ACTIVE
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == RecoveryOpcode.ARCHIVE:
        context.archived.append(state_i.clone())
        state_i.trust_level = TrustLevel.QUARANTINED
        _touch(state_i, crossing.tag)
        return "QUARANTINED"
    raise context.law_violation(f"unsupported RECOV opcode: {crossing.opcode}")


def _execute_role(crossing: ExecutableCrossing, strands: list[StrandState], context: Any) -> str:
    state_i = strands[crossing.strand_i]
    state_j = strands[crossing.strand_j]
    opcode = RoleOpcode(crossing.opcode)
    if opcode == RoleOpcode.TRANSFER:
        state_j.authority_token = state_i.authority_token
        state_i.authority_token = None
        _touch(state_i, crossing.tag)
        _touch(state_j, crossing.tag)
        return "PASS"
    if opcode == RoleOpcode.DELEGATE:
        if state_i.authority_token is None:
            raise context.law_violation("ROLE.DELEGATE requires a source authority token")
        delegated = context.authority_manager.delegate_token(
            state_i.authority_token,
            scope=crossing.operands.get("scope", state_i.authority_token.scope),
            role=crossing.operands.get("role"),
        )
        target = crossing.operands.get("target", "j")
        recipient = state_j if target == "j" else state_i
        recipient.authority_token = delegated
        _touch(state_i, crossing.tag)
        _touch(recipient, crossing.tag)
        return "PASS"
    if opcode == RoleOpcode.REVOKE:
        if state_i.authority_token is None:
            raise context.law_violation("ROLE.REVOKE requires an authority token")
        state_i.authority_token = context.authority_manager.revoke_token(state_i.authority_token)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == RoleOpcode.VERIFY_ROLE:
        expected_role = crossing.operands["role"]
        passed = state_i.authority_token is not None and state_i.authority_token.role == expected_role and not state_i.authority_token.revoked
        _touch(state_i, crossing.tag)
        return "PASS" if passed else "FAIL"
    raise context.law_violation(f"unsupported ROLE opcode: {crossing.opcode}")


def _execute_memory(crossing: ExecutableCrossing, strands: list[StrandState], context: Any) -> str:
    state_i = strands[crossing.strand_i]
    opcode = MemoryOpcode(crossing.opcode)
    key = crossing.operands.get("key", crossing.tag)
    if opcode == MemoryOpcode.STORE_HOT:
        context.memory["hot"][key] = state_i.clone()
        context.record_checkpoint(crossing.tag, strands)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.LOAD_HOT:
        strands[crossing.strand_i] = context.memory["hot"][key].clone()
        _touch(strands[crossing.strand_i], crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.DEMOTE_WARM:
        context.memory["warm"][key] = context.memory["hot"].pop(key)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.PROMOTE_HOT:
        context.memory["hot"][key] = context.memory["warm"].pop(key)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.ARCHIVE_COLD:
        context.memory["cold"][key] = context.memory["warm"].pop(key)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.RETRIEVE_COLD:
        context.memory["warm"][key] = context.memory["cold"][key]
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.OPEN_POCKET:
        context.memory["pockets"][key] = {"scope": crossing.operands.get("scope", "default")}
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.CLOSE_POCKET:
        context.memory["pockets"].pop(key, None)
        _touch(state_i, crossing.tag)
        return "PASS"
    if opcode == MemoryOpcode.STITCH:
        context.memory["stitches"].append((crossing.operands.get("region_a"), crossing.operands.get("region_b")))
        _touch(state_i, crossing.tag)
        return "PASS"
    raise context.law_violation(f"unsupported MEM opcode: {crossing.opcode}")
