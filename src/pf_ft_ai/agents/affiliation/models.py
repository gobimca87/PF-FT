from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.agents.affiliation.states import AffiliationApplicationStatus


class ClubSummary(BaseModel):
    """`affiliation.get_club` tool response shape."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    club_id: str
    name: str
    county: str
    status: str


class ApplicationSummary(BaseModel):
    """`affiliation.get_application` tool response shape — flow doc PHASE 5-6."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    application_id: str
    club_id: str
    season: str
    status: AffiliationApplicationStatus
    total_fee: float = Field(ge=0)
    currency: str = "GBP"
    invoice_number: str | None = None
    is_cfa_review_required: bool = False
    rejection_reason: str | None = None
    cancellation_reason: str | None = None


class TeamSummary(BaseModel):
    """`affiliation.get_teams` tool response shape — one entry per team."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    team_id: str
    name: str
    age_group: str
    affiliated: bool = False


class OfficialSummary(BaseModel):
    """`affiliation.get_officials` tool response shape — flow doc PHASE 1 club checks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    official_id: str
    name: str
    role: str
    safeguarding_status: str
    suspended: bool = False


class InsuranceSummary(BaseModel):
    """`affiliation.get_insurance` tool response shape — flow doc PHASE 3."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    club_id: str
    public_liability_status: str
    personal_accident_status: str


class ProductSummary(BaseModel):
    """`affiliation.get_products` tool response shape — flow doc PHASE 2/4."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    product_id: str
    name: str
    category: str
    price: float = Field(ge=0)
    mandatory: bool = False


class PaymentStatusSummary(BaseModel):
    """`affiliation.get_payment_status` tool response shape — flow doc PHASE 6/10."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    application_id: str
    invoice_number: str | None = None
    status: str
    amount: float = Field(ge=0)
    paid_at: datetime | None = None
