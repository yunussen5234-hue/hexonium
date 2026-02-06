from sqlalchemy.orm import Session

from app.models.entities import Personnel, PersonnelSiteAssignment, User
from app.schemas.personnel import AssignmentCreate, PersonnelCreate, PersonnelUpdate
from app.services.audit_service import AuditService


class PersonnelService:
    @staticmethod
    def list_personnel(db: Session):
        return db.query(Personnel).filter(Personnel.deleted_at.is_(None)).order_by(Personnel.created_at.desc()).all()

    @staticmethod
    def create(db: Session, payload: PersonnelCreate, actor: User, ip: str | None):
        person = Personnel(**payload.model_dump())
        db.add(person)
        db.flush()
        AuditService.log(db, actor, "create", "personnel", str(person.id), None, payload.model_dump(), ip)
        return person

    @staticmethod
    def update(db: Session, person: Personnel, payload: PersonnelUpdate, actor: User, ip: str | None):
        changes = payload.model_dump(exclude_unset=True)
        for k, v in changes.items():
            setattr(person, k, v)
        AuditService.log(db, actor, "update", "personnel", str(person.id), None, changes, ip)
        return person

    @staticmethod
    def create_assignment(db: Session, personnel_id: int, payload: AssignmentCreate, actor: User, ip: str | None):
        assignment = PersonnelSiteAssignment(personnel_id=personnel_id, **payload.model_dump())
        db.add(assignment)
        db.query(Personnel).filter(Personnel.id == personnel_id).update({"current_site_id": payload.site_id})
        AuditService.log(db, actor, "create", "assignment", str(personnel_id), None, payload.model_dump(), ip)
        return assignment
