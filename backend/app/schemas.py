from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_validator


# --- Category ---

class CategoryCreate(BaseModel):
    slug: str
    label: str


class CategoryOut(BaseModel):
    slug: str
    label: str

    model_config = {"from_attributes": True}


# --- Service ---

class ServiceCreate(BaseModel):
    slug: str
    name: str
    canonical_provider: str
    category_slug: str
    description: str
    docs_url: str
    base_url: str
    auth_type: str
    pricing_model: str
    pricing_notes: str | None = None

    @field_validator("auth_type")
    @classmethod
    def valid_auth_type(cls, v):
        allowed = {"api_key", "oauth", "none"}
        if v not in allowed:
            raise ValueError(f"auth_type must be one of {allowed}")
        return v

    @field_validator("pricing_model")
    @classmethod
    def valid_pricing_model(cls, v):
        allowed = {"per_request", "subscription", "free", "usage_based"}
        if v not in allowed:
            raise ValueError(f"pricing_model must be one of {allowed}")
        return v


class ServiceOut(BaseModel):
    id: str
    slug: str
    name: str
    canonical_provider: str
    category_slug: str
    description: str
    docs_url: str
    base_url: str
    auth_type: str
    pricing_model: str
    pricing_notes: str | None
    status: str
    verified: bool
    avg_rating: float | None = None
    rating_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceTombstone(BaseModel):
    id: str
    slug: str
    deleted_at: datetime


# --- Rating ---

class RatingCreate(BaseModel):
    cost_score: float
    quality_score: float
    latency_score: float
    reliability_score: float
    agent_id: str | None = None
    notes: str | None = None

    @field_validator("cost_score", "quality_score", "latency_score", "reliability_score")
    @classmethod
    def score_range(cls, v):
        if not (1.0 <= v <= 5.0):
            raise ValueError("Scores must be between 1.0 and 5.0")
        return v


class RatingAggregated(BaseModel):
    service_id: str
    count: int
    avg_cost: float
    avg_quality: float
    avg_latency: float
    avg_reliability: float
    avg_overall: float
    updated_at: datetime | None


# --- Registry ---

class RegistryResponse(BaseModel):
    generated_at: datetime
    count: int
    services: list[ServiceOut]
    tombstones: list[ServiceTombstone] = []
