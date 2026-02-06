from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.entities import AuditLog, Role

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("")
def list_logs(entityType: str | None = None, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN))):
    q = db.query(AuditLog)
    if entityType:
        q = q.filter(AuditLog.entity_type == entityType)
    return q.order_by(AuditLog.created_at.desc()).all()
