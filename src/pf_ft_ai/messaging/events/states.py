from __future__ import annotations

from enum import StrEnum


class EventProcessingStatus(StrEnum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    DUPLICATE = "DUPLICATE"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    DEAD_LETTERED = "DEAD_LETTERED"
