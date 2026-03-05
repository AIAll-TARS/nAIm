import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Category
from app.schemas import ServiceCreate, ServiceOut, CategoryOut, RegistryResponse, ServiceTombstone
from app.auth import require_api_key

router = APIRouter(prefix="/v1", tags=["services"])

_registry_cache: dict = {"data": None, "expires_at": 0.0}
REGISTRY_CACHE_TTL = 60  # seconds


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/services", response_model=list[ServiceOut])
def list_services(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Service).filter(Service.status == "approved", Service.deleted_at.is_(None))
    if category:
        q = q.filter(Service.category_slug == category)
    return q.order_by(Service.created_at.desc()).all()


@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: str, db: Session = Depends(get_db)):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.status == "approved",
        Service.deleted_at.is_(None),
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


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

    service = Service(**payload.model_dump())
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
            services=services,
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
        services=services,
        tombstones=[],
    )
    _registry_cache["data"] = response
    _registry_cache["expires_at"] = time.time() + REGISTRY_CACHE_TTL
    return response
