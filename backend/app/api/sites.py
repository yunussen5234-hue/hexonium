from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import Personnel, Role, Site
from app.schemas.site import AssignPersonnelRequest, SiteCreate, SiteOut, SiteUpdate
from app.services.audit_service import AuditService
from app.services.site_service import SiteService
from app.utils.errors import api_error

router = APIRouter(prefix="/sites", tags=["Şantiyeler"])


@router.get("", response_model=list[SiteOut])
def list_sites(q: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == Role.SITE_CHIEF and user.site_id:
        site = db.query(Site).filter(Site.id == user.site_id, Site.deleted_at.is_(None)).all()
        return site
    return SiteService.list_sites(db, q)


@router.post("", response_model=SiteOut)
def create_site(payload: SiteCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN))):
    site = SiteService.create(db, payload, user, request.client.host if request.client else None)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}")
def get_site(site_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    site = db.query(Site).filter(Site.id == site_id, Site.deleted_at.is_(None)).first()
    if not site:
        api_error("NOT_FOUND", "Şantiye bulunamadı", status_code=404)
    return site


@router.patch("/{site_id}")
def update_site(site_id: int, payload: SiteUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING))):
    site = db.query(Site).filter(Site.id == site_id, Site.deleted_at.is_(None)).first()
    if not site:
        api_error("NOT_FOUND", "Şantiye bulunamadı", status_code=404)
    SiteService.update(db, site, payload, user, request.client.host if request.client else None)
    db.commit()
    return site


@router.delete("/{site_id}")
def delete_site(site_id: int, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN))):
    site = db.query(Site).filter(Site.id == site_id, Site.deleted_at.is_(None)).first()
    if not site:
        api_error("NOT_FOUND", "Şantiye bulunamadı", status_code=404)
    site.deleted_at = __import__("datetime").datetime.utcnow()
    AuditService.log(db, user, "delete", "site", str(site_id), {"deleted": False}, {"deleted": True}, request.client.host if request.client else None)
    db.commit()
    return {"ok": True}


@router.post("/{site_id}/assign-personnel")
def assign_personnel(site_id: int, payload: AssignPersonnelRequest, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.SITE_CHIEF))):
    people = db.query(Personnel).filter(Personnel.id.in_(payload.personnel_ids)).all()
    for p in people:
        p.current_site_id = site_id
    AuditService.log(db, user, "update", "site_assignment", str(site_id), None, payload.model_dump(), request.client.host if request.client else None)
    db.commit()
    return {"assigned": len(people)}


@router.post("/{site_id}/unassign-personnel")
def unassign_personnel(site_id: int, payload: AssignPersonnelRequest, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.SITE_CHIEF))):
    people = db.query(Personnel).filter(Personnel.id.in_(payload.personnel_ids), Personnel.current_site_id == site_id).all()
    for p in people:
        p.current_site_id = None
    AuditService.log(db, user, "update", "site_unassignment", str(site_id), None, payload.model_dump(), request.client.host if request.client else None)
    db.commit()
    return {"unassigned": len(people)}
