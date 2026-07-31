from enum import Enum


class _StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class InstructionFamily(_StrEnum):
    INTEG = "INTEG"
    ROUTE = "ROUTE"
    RECOV = "RECOV"
    ROLE = "ROLE"
    AUTH = "AUTH"
    MEM = "MEM"


class IntegrityOpcode(_StrEnum):
    VERIFY = "VERIFY"
    PROMOTE = "PROMOTE"
    ATTEST = "ATTEST"
    SEAL = "SEAL"
    COMPARE = "COMPARE"


class RoutingOpcode(_StrEnum):
    SELECT = "SELECT"
    FORK = "FORK"
    JOIN = "JOIN"
    REDIRECT = "REDIRECT"
    REPLAY = "REPLAY"


class RecoveryOpcode(_StrEnum):
    DETECT = "DETECT"
    QUARANTINE = "QUARANTINE"
    RESTORE = "RESTORE"
    HEAL = "HEAL"
    ARCHIVE = "ARCHIVE"


class RoleOpcode(_StrEnum):
    TRANSFER = "TRANSFER"
    DELEGATE = "DELEGATE"
    REVOKE = "REVOKE"
    VERIFY_ROLE = "VERIFY_ROLE"


class AuthOpcode(_StrEnum):
    CHECK = "CHECK"
    GATE = "GATE"
    INHERIT = "INHERIT"
    SCOPE = "SCOPE"


class MemoryOpcode(_StrEnum):
    STORE_HOT = "STORE_HOT"
    LOAD_HOT = "LOAD_HOT"
    DEMOTE_WARM = "DEMOTE_WARM"
    PROMOTE_HOT = "PROMOTE_HOT"
    ARCHIVE_COLD = "ARCHIVE_COLD"
    RETRIEVE_COLD = "RETRIEVE_COLD"
    OPEN_POCKET = "OPEN_POCKET"
    CLOSE_POCKET = "CLOSE_POCKET"
    STITCH = "STITCH"
