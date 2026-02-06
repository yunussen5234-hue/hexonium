import json

from sqlalchemy.orm import Session

from app.models.entities import AuditLog, User


class AuditService:
    @staticmethod
    def log(
        db: Session,
        actor: User | None,
        action_type: str,
        entity_type: str,
        entity_id: str,
        before: dict | None,
        after: dict | None,
        ip_address: str | None,
    ):
        entry = AuditLog(
            actor_user_id=actor.id if actor else None,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            before_json=json.dumps(before) if before else None,
            after_json=json.dumps(after) if after else None,
            ip_address=ip_address,
        )
        db.add(entry)
