from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.common.exceptions import ValidationError
from pff_fa_ai.context.collection.states import BatchStatus


class BatchRange(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=1)
    start: int = Field(ge=1)
    end: int = Field(ge=1)

    @property
    def record_count(self) -> int:
        return self.end - self.start + 1


def split_into_batches(total_count: int, *, batch_size: int) -> list[BatchRange]:
    """doc 8 §36-38 — the agreed batch size is 20."""
    if batch_size <= 0:
        raise ValidationError("batch_size must be greater than zero")
    if total_count <= 0:
        return []

    batches: list[BatchRange] = []
    start = 1
    index = 1
    while start <= total_count:
        end = min(start + batch_size - 1, total_count)
        batches.append(BatchRange(index=index, start=start, end=end))
        start = end + 1
        index += 1
    return batches


class Batch(BaseModel):
    model_config = ConfigDict(frozen=True)

    batch_id: str
    collection: str
    range: BatchRange
    status: BatchStatus = BatchStatus.PENDING
    attempt: int = Field(ge=1, default=1)
