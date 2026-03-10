"""
CRM models — agent contacts and interactions from apiale's Moltbook sessions.
Separate from nAIm registry models but same DB, same Base.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class CRMAgent(Base):
    """An AI agent apiale has encountered on Moltbook."""
    __tablename__ = "crm_agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    handle: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)   # @someagent
    platform: Mapped[str] = mapped_column(String(32), default="moltbook")
    profile_url: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    capabilities: Mapped[str | None] = mapped_column(Text)   # comma-separated tags
    tags: Mapped[str | None] = mapped_column(Text)           # comma-separated tags
    karma: Mapped[int | None] = mapped_column(default=None)
    follower_count: Mapped[int | None] = mapped_column(default=None)
    naim_aware: Mapped[bool] = mapped_column(Boolean, default=False)  # has seen nAIm mentioned
    naim_interested: Mapped[bool] = mapped_column(Boolean, default=False)  # showed interest
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    interactions: Mapped[list["CRMInteraction"]] = relationship(back_populates="agent", cascade="all, delete-orphan")


class CRMInteraction(Base):
    """One interaction apiale had with an agent on Moltbook."""
    __tablename__ = "crm_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("crm_agents.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    topic: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    naim_mentioned: Mapped[bool] = mapped_column(Boolean, default=False)
    outcome: Mapped[str | None] = mapped_column(String(256))   # shared link / answered / listened
    sentiment: Mapped[str | None] = mapped_column(String(32))  # positive / neutral / negative
    follow_up: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    agent: Mapped["CRMAgent"] = relationship(back_populates="interactions")


class CRMSession(Base):
    """One full Moltbook session report from apiale."""
    __tablename__ = "crm_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(default=None)
    posts_made: Mapped[int] = mapped_column(default=0)
    mood: Mapped[str | None] = mapped_column(String(32))       # active | quiet | hostile | friendly
    observations: Mapped[str | None] = mapped_column(Text)     # JSON array stored as text
    naim_gaps: Mapped[str | None] = mapped_column(Text)        # JSON array stored as text
    raw_report: Mapped[str | None] = mapped_column(Text)       # full JSON from apiale
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


Index("ix_crm_agent_handle", CRMAgent.handle)
Index("ix_crm_interaction_date", CRMInteraction.date)
Index("ix_crm_session_date", CRMSession.date)
