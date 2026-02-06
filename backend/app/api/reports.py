import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.entities import Personnel, PersonnelStatus, Role, Site, SiteStatus

router = APIRouter(prefix="/reports", tags=["Raporlar"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING, Role.HR, Role.VIEWER))):
    return {
        "aktif_santiye": db.query(func.count(Site.id)).filter(Site.status == SiteStatus.ACTIVE, Site.deleted_at.is_(None)).scalar(),
        "aktif_personel": db.query(func.count(Personnel.id)).filter(Personnel.status == PersonnelStatus.ACTIVE, Personnel.deleted_at.is_(None)).scalar(),
    }


@router.get("/sites/{site_id}/personnel.csv")
def export_site_personnel(site_id: int, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING, Role.HR))):
    rows = db.query(Personnel).filter(Personnel.current_site_id == site_id, Personnel.deleted_at.is_(None)).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ad", "soyad", "telefon", "durum"])
    for r in rows:
        writer.writerow([r.first_name, r.last_name, r.phone, r.status.value])
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv")
