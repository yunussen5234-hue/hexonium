from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import Personnel, PersonnelSiteAssignment, Role
from app.schemas.personnel import AssignmentCreate, AssignmentOut, PersonnelCreate, PersonnelOut, PersonnelUpdate
from app.services.audit_service import AuditService
from app.services.personnel_service import PersonnelService
from app.utils.errors import api_error

router = APIRouter(prefix="/personnel", tags=["Personeller"])


@router.get("", response_model=list[PersonnelOut])
def list_personnel(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return PersonnelService.list_personnel(db)


@router.post("", response_model=PersonnelOut)
def create_personnel(payload: PersonnelCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR))):
    p = PersonnelService.create(db, payload, user, request.client.host if request.client else None)
    db.commit()
    db.refresh(p)
    return p


@router.get("/{personnel_id}")
def get_personnel(personnel_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.deleted_at.is_(None)).first()
    if not p:
        api_error("NOT_FOUND", "Personel bulunamadı", status_code=404)
    return p


@router.patch("/{personnel_id}")
def update_personnel(personnel_id: int, payload: PersonnelUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.SITE_CHIEF))):
    p = db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.deleted_at.is_(None)).first()
    if not p:
        api_error("NOT_FOUND", "Personel bulunamadı", status_code=404)
    PersonnelService.update(db, p, payload, user, request.client.host if request.client else None)
    db.commit()
    return p


@router.delete("/{personnel_id}")
def delete_personnel(personnel_id: int, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR))):
    p = db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.deleted_at.is_(None)).first()
    if not p:
        api_error("NOT_FOUND", "Personel bulunamadı", status_code=404)
    p.deleted_at = datetime.utcnow()
    AuditService.log(db, user, "delete", "personnel", str(personnel_id), {"deleted": False}, {"deleted": True}, request.client.host if request.client else None)
    db.commit()
    return {"ok": True}


@router.get("/{personnel_id}/assignments", response_model=list[AssignmentOut])
def list_assignments(personnel_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(PersonnelSiteAssignment).filter(PersonnelSiteAssignment.personnel_id == personnel_id).all()


@router.post("/{personnel_id}/assignments", response_model=AssignmentOut)
def create_assignment(personnel_id: int, payload: AssignmentCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.SITE_CHIEF))):
    assignment = PersonnelService.create_assignment(db, personnel_id, payload, user, request.client.host if request.client else None)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.patch("/assignments/{assignment_id}")
def update_assignment(assignment_id: int, payload: AssignmentCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.SITE_CHIEF))):
    assignment = db.query(PersonnelSiteAssignment).filter(PersonnelSiteAssignment.id == assignment_id).first()
    if not assignment:
        api_error("NOT_FOUND", "Atama bulunamadı", status_code=404)
    for k, v in payload.model_dump().items():
        setattr(assignment, k, v)
    AuditService.log(db, user, "update", "assignment", str(assignment_id), None, payload.model_dump(), request.client.host if request.client else None)
    db.commit()
    return assignment


@router.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.SITE_CHIEF))):
    assignment = db.query(PersonnelSiteAssignment).filter(PersonnelSiteAssignment.id == assignment_id).first()
    if not assignment:
        api_error("NOT_FOUND", "Atama bulunamadı", status_code=404)
    db.delete(assignment)
    AuditService.log(db, user, "delete", "assignment", str(assignment_id), None, None, request.client.host if request.client else None)
    db.commit()
    return {"ok": True}
