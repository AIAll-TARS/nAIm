import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, ForeignKey, UniqueConstraint, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(128), nullable=False)

    services: Mapped[list["Service"]] = relationship(back_populates="category")


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_service_slug"),
        UniqueConstraint("canonical_provider", "base_url", name="uq_provider_base_url"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    canonical_provider: Mapped[str] = mapped_column(String(128), nullable=False)
    category_slug: Mapped[str] = mapped_column(String(64), ForeignKey("categories.slug"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    docs_url: Mapped[str] = mapped_column(String(512), nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    auth_type: Mapped[str] = mapped_column(String(32), nullable=False)       # api_key | oauth | none
    pricing_model: Mapped[str] = mapped_column(String(32), nullable=False)   # per_request | subscription | free | usage_based
    pricing_notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="pending")       # pending | approved | rejected
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    category: Mapped["Category"] = relationship(back_populates="services")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="service")


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("service_id", "rater_hash", name="uq_rating_per_rater"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), nullable=False)
    cost_score: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    latency_score: Mapped[float] = mapped_column(Float, nullable=False)
    reliability_score: Mapped[float] = mapped_column(Float, nullable=False)
    agent_id: Mapped[str | None] = mapped_column(String(256))
    rater_hash: Mapped[str | None] = mapped_column(String(64))   # not exposed publicly
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    service: Mapped["Service"] = relationship(back_populates="ratings")


# Index for fast delta queries
Index("ix_service_updated_at", Service.updated_at)
