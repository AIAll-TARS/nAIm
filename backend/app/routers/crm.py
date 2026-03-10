"""
CRM router — apiale submits session reports, AIAll views contacts and interactions.
All write endpoints require API key. Read endpoints are open (internal use).
"""
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_api_key
from app.crm_models import CRMAgent, CRMInteraction, CRMSession

router = APIRouter(prefix="/v1/crm", tags=["crm"])


# --- Pydantic schemas ---

class InteractionIn(BaseModel):
    agent_handle: str
    platform: str = "moltbook"
    topic: str | None = None
    naim_mentioned: bool = False
    outcome: str | None = None
    sentiment: str | None = None
    follow_up: bool = False

class PostMade(BaseModel):
    post_id: str
    content_summary: str | None = None
    submolt: str | None = None

class SessionReportIn(BaseModel):
    date: str                            # YYYY-MM-DD
    session_duration_minutes: int | None = None
    interactions: list[InteractionIn] = []
    posts_made: list[PostMade] = []
    observations: list[str] = []
    naim_gaps: list[str] = []
    mood: str | None = None


# --- Write: apiale submits a session report ---

@router.post("/sessions", dependencies=[Depends(require_api_key)], status_code=201)
def submit_session(report: SessionReportIn, db: Session = Depends(get_db)):
    date = datetime.fromisoformat(report.date).replace(tzinfo=timezone.utc)

    # Save session
    session = CRMSession(
        date=date,
        duration_minutes=report.session_duration_minutes,
        posts_made=len(report.posts_made),
        mood=report.mood,
        observations=json.dumps(report.observations),
        naim_gaps=json.dumps(report.naim_gaps),
        raw_report=report.model_dump_json(),
    )
    db.add(session)

    # Upsert agents + add interactions
    for ix in report.interactions:
        agent = db.query(CRMAgent).filter_by(handle=ix.agent_handle).first()
        if not agent:
            agent = CRMAgent(
                handle=ix.agent_handle,
                platform=ix.platform,
                profile_url=f"https://www.moltbook.com/u/{ix.agent_handle.lstrip('@')}",
            )
            db.add(agent)
            db.flush()

        if ix.naim_mentioned:
            agent.naim_aware = True
        if ix.sentiment == "positive" and ix.naim_mentioned:
            agent.naim_interested = True
        agent.last_seen = date

        interaction = CRMInteraction(
            agent_id=agent.id,
            date=date,
            topic=ix.topic,
            naim_mentioned=ix.naim_mentioned,
            outcome=ix.outcome,
            sentiment=ix.sentiment,
            follow_up=ix.follow_up,
        )
        db.add(interaction)

    db.commit()
    return {"status": "ok", "session_id": session.id, "interactions_saved": len(report.interactions)}


# --- Read: AIAll views CRM data ---

@router.get("/agents")
def list_agents(
    naim_aware: bool | None = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(CRMAgent)
    if naim_aware is not None:
        q = q.filter(CRMAgent.naim_aware == naim_aware)
    agents = q.order_by(CRMAgent.last_seen.desc()).limit(limit).all()
    return {"count": len(agents), "agents": [
        {
            "id": a.id,
            "handle": a.handle,
            "platform": a.platform,
            "profile_url": a.profile_url,
            "tags": a.tags,
            "naim_aware": a.naim_aware,
            "naim_interested": a.naim_interested,
            "first_seen": a.first_seen,
            "last_seen": a.last_seen,
            "interaction_count": len(a.interactions),
        }
        for a in agents
    ]}


@router.get("/agents/{handle}/interactions")
def get_agent_interactions(handle: str, db: Session = Depends(get_db)):
    agent = db.query(CRMAgent).filter_by(handle=handle).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "agent": handle,
        "interactions": [
            {
                "date": i.date,
                "topic": i.topic,
                "naim_mentioned": i.naim_mentioned,
                "outcome": i.outcome,
                "sentiment": i.sentiment,
                "follow_up": i.follow_up,
            }
            for i in sorted(agent.interactions, key=lambda x: x.date, reverse=True)
        ]
    }


@router.get("/sessions")
def list_sessions(limit: int = 20, db: Session = Depends(get_db)):
    sessions = db.query(CRMSession).order_by(CRMSession.date.desc()).limit(limit).all()
    return {"count": len(sessions), "sessions": [
        {
            "id": s.id,
            "date": s.date,
            "duration_minutes": s.duration_minutes,
            "posts_made": s.posts_made,
            "mood": s.mood,
            "observations": json.loads(s.observations) if s.observations else [],
            "naim_gaps": json.loads(s.naim_gaps) if s.naim_gaps else [],
        }
        for s in sessions
    ]}
