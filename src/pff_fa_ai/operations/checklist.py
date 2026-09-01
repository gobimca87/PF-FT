from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.engineering_agents.models import EngineeringAgentResult
from pff_fa_ai.operations.states import CheckFrequency

CheckRunner = Callable[[], Awaitable[EngineeringAgentResult]]


class OperationalCheck(BaseModel):
    """doc 28 §135-137 daily/weekly/monthly operational checklists, reusing Phase 18's
    `EngineeringAgentResult`/`Finding` contract — both answer the same question ("did
    this check pass, what's the severity, what was found"), just on a scheduled
    cadence instead of a PR trigger, so there's no reason to invent a second contract."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    check_id: str
    frequency: CheckFrequency
    description: str
    run: CheckRunner


class OperationalChecklistRunner:
    def __init__(self) -> None:
        self._checks: list[OperationalCheck] = []

    def register(self, check: OperationalCheck) -> None:
        if any(existing.check_id == check.check_id for existing in self._checks):
            raise ConfigurationError(f"Duplicate operational check registered: {check.check_id}")
        self._checks.append(check)

    def checks_for(self, frequency: CheckFrequency) -> tuple[OperationalCheck, ...]:
        return tuple(check for check in self._checks if check.frequency is frequency)

    async def run_due(self, frequency: CheckFrequency) -> tuple[EngineeringAgentResult, ...]:
        due = self.checks_for(frequency)
        return tuple(await asyncio.gather(*(check.run() for check in due)))
