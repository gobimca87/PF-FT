from __future__ import annotations

from enum import StrEnum


class ConversationStatus(StrEnum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    WAITING_FOR_EXTERNAL_EVENT = "WAITING_FOR_EXTERNAL_EVENT"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"
