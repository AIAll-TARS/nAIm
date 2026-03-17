import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Category, Rating
from app.schemas import CategoryCreate, ServiceCreate, ServiceOut, CategoryOut, RegistryResponse, ServiceTombstone
from app.auth import require_api_key

router = APIRouter(prefix="/v1", tags=["services"])

_registry_cache: dict = {"data": None, "expires_at": 0.0}
REGISTRY_CACHE_TTL = 60  # seconds


def _attach_ratings(services: list, db: Session) -> list[ServiceOut]:
    """Attach avg_rating and rating_count to a list of Service ORM objects."""
    if not services:
        return []
    service_ids = [s.id for s in services]
    rows = db.query(
        Rating.service_id,
        func.count(Rating.id).label("cnt"),
        func.avg((Rating.cost_score + Rating.quality_score + Rating.latency_score + Rating.reliability_score) / 4).label("avg"),
    ).filter(Rating.service_id.in_(service_ids)).group_by(Rating.service_id).all()

    rating_map = {r.service_id: (round(r.avg, 2), r.cnt) for r in rows}

    result = []
    for s in services:
        out = ServiceOut.model_validate(s)
        avg, cnt = rating_map.get(s.id, (None, 0))
        out.avg_rating = avg
        out.rating_count = cnt
        result.append(out)
    return result


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    existing = db.query(Category).filter(Category.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category with this slug already exists")

    category = Category(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category already exists")
    db.refresh(category)
    return category


@router.get("/services", response_model=list[ServiceOut])
def list_services(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Service).filter(Service.status == "approved", Service.deleted_at.is_(None))
    if category:
        q = q.filter(Service.category_slug == category)
    services = q.order_by(Service.created_at.desc()).all()
    return _attach_ratings(services, db)


@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: str, db: Session = Depends(get_db)):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.status == "approved",
        Service.deleted_at.is_(None),
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return _attach_ratings([service], db)[0]


@router.post("/services", response_model=ServiceOut, status_code=201)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    if not db.query(Category).filter(Category.slug == payload.category_slug).first():
        raise HTTPException(status_code=400, detail=f"Unknown category: {payload.category_slug}")

    existing = db.query(Service).filter(Service.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Service with this slug already exists")

    service = Service(**payload.model_dump(), status="approved")
    db.add(service)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service already exists (slug or provider+url conflict)")
    db.refresh(service)
    return service


@router.get("/registry.json", response_model=RegistryResponse)
def registry(
    since: datetime | None = Query(None, description="ISO8601 timestamp — return only changes after this time"),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    if since:
        # Delta requests — always hit DB, no cache
        services = db.query(Service).filter(
            Service.status == "approved",
            Service.deleted_at.is_(None),
            Service.updated_at > since,
        ).all()
        tombstones_q = db.query(Service).filter(
            Service.deleted_at.isnot(None),
            Service.deleted_at > since,
        ).all()
        tombstones = [ServiceTombstone(id=s.id, slug=s.slug, deleted_at=s.deleted_at) for s in tombstones_q]
        return RegistryResponse(
            generated_at=now,
            count=len(services),
            services=_attach_ratings(services, db),
            tombstones=tombstones,
        )

    # Full dump — serve from cache if fresh
    if _registry_cache["data"] and time.time() < _registry_cache["expires_at"]:
        return _registry_cache["data"]

    services = db.query(Service).filter(
        Service.status == "approved",
        Service.deleted_at.is_(None),
    ).all()

    response = RegistryResponse(
        generated_at=now,
        count=len(services),
        services=_attach_ratings(services, db),
        tombstones=[],
    )
    _registry_cache["data"] = response
    _registry_cache["expires_at"] = time.time() + REGISTRY_CACHE_TTL
    return response
