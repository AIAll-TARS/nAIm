import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Rating
from app.schemas import RatingCreate, RatingAggregated

router = APIRouter(prefix="/v1", tags=["ratings"])


def _rater_hash(request: Request, agent_id: str | None) -> str:
    raw = f"{request.client.host}:{agent_id or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


@router.get("/services/{service_id}/ratings", response_model=RatingAggregated)
def get_ratings(service_id: str, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id, Service.deleted_at.is_(None)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    result = db.query(
        func.count(Rating.id).label("count"),
        func.avg(Rating.cost_score).label("avg_cost"),
        func.avg(Rating.quality_score).label("avg_quality"),
        func.avg(Rating.latency_score).label("avg_latency"),
        func.avg(Rating.reliability_score).label("avg_reliability"),
        func.max(Rating.created_at).label("updated_at"),
    ).filter(Rating.service_id == service_id).one()

    if result.count == 0:
        return RatingAggregated(
            service_id=service_id, count=0,
            avg_cost=0, avg_quality=0, avg_latency=0, avg_reliability=0,
            avg_overall=0, updated_at=None,
        )

    avg_overall = (result.avg_cost + result.avg_quality + result.avg_latency + result.avg_reliability) / 4

    return RatingAggregated(
        service_id=service_id,
        count=result.count,
        avg_cost=round(result.avg_cost, 2),
        avg_quality=round(result.avg_quality, 2),
        avg_latency=round(result.avg_latency, 2),
        avg_reliability=round(result.avg_reliability, 2),
        avg_overall=round(avg_overall, 2),
        updated_at=result.updated_at,
    )


@router.post("/services/{service_id}/ratings", status_code=201)
def submit_rating(
    service_id: str,
    payload: RatingCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id, Service.deleted_at.is_(None)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    rater_hash = _rater_hash(request, payload.agent_id)

    rating = Rating(
        service_id=service_id,
        rater_hash=rater_hash,
        **payload.model_dump(),
    )
    db.add(rating)
    db.commit()
    return {"status": "ok", "id": rating.id}
