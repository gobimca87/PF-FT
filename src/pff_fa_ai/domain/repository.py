from __future__ import annotations

from typing import Protocol, TypeVar

from pff_fa_ai.domain.state_transition import StateActor, StateTransition

EntityT = TypeVar("EntityT")


class StateRepository(Protocol[EntityT]):
    async def create(self, entity: EntityT) -> EntityT: ...

    async def get(self, entity_id: str) -> EntityT | None: ...

    async def update(self, entity: EntityT, *, expected_version: int) -> EntityT: ...

    async def checkpoint(self, entity_id: str, *, expected_version: int) -> EntityT: ...

    async def transition(
        self,
        entity_id: str,
        *,
        to_state: str,
        reason: str,
        actor: StateActor,
        expected_version: int,
    ) -> StateTransition: ...

    async def resume(self, entity_id: str) -> EntityT: ...

    async def cancel(self, entity_id: str, *, reason: str) -> EntityT: ...
