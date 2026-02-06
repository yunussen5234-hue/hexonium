from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Personnel, Site, User
from app.schemas.site import SiteCreate, SiteUpdate
from app.services.audit_service import AuditService
from app.utils.errors import api_error


class SiteService:
    @staticmethod
    def list_sites(db: Session, q: str | None = None):
        query = db.query(Site).filter(Site.deleted_at.is_(None))
        if q:
            like = f"%{q}%"
            query = query.filter((Site.name.ilike(like)) | (Site.code.ilike(like)) | (Site.city.ilike(like)))
        sites = query.order_by(Site.created_at.desc()).all()
        result = []
        for s in sites:
            personnel_count = db.query(func.count(Personnel.id)).filter(
                Personnel.current_site_id == s.id, Personnel.deleted_at.is_(None)
            ).scalar()
            setattr(s, "personnel_count", personnel_count)
            result.append(s)
        return result

    @staticmethod
    def create(db: Session, payload: SiteCreate, actor: User, ip: str | None):
        exists = db.query(Site).filter(Site.code == payload.code).first()
        if exists:
            api_error("SITE_CODE_EXISTS", "Şantiye kodu benzersiz olmalıdır")
        site = Site(**payload.model_dump())
        db.add(site)
        db.flush()
        AuditService.log(db, actor, "create", "site", str(site.id), None, payload.model_dump(), ip)
        return site

    @staticmethod
    def update(db: Session, site: Site, payload: SiteUpdate, actor: User, ip: str | None):
        before = {"name": site.name, "status": site.status.value}
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(site, key, value)
        AuditService.log(db, actor, "update", "site", str(site.id), before, payload.model_dump(exclude_unset=True), ip)
        return site
