from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from pf_ft_ai.api.dependencies import AppState, get_app_state, get_correlation_ids
from pf_ft_ai.api.v1.envelope import ResponseEnvelope

router = APIRouter(prefix="/api/v1", tags=["health"])


class HealthData(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    environment: str
    platform_version: str
    configuration_hash: str


@router.get("/health", response_model=ResponseEnvelope[HealthData])
async def get_health(
    state: AppState = Depends(get_app_state),
    correlation: tuple[str, str] = Depends(get_correlation_ids),
) -> ResponseEnvelope[HealthData]:
    request_id, _correlation_id = correlation
    data = HealthData(
        status="READY",
        environment=state.environment,
        platform_version=state.platform_configuration.environment.platform_version,
        configuration_hash=state.platform_configuration.configuration_hash,
    )
    return ResponseEnvelope[HealthData](request_id=request_id, status="READY", data=data)
