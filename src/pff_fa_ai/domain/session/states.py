from __future__ import annotations

from enum import StrEnum


class SessionStatus(StrEnum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
