from datetime import datetime


class SoftDeleteMixin:
    @staticmethod
    def soft_delete(entity):
        entity.deleted_at = datetime.utcnow()
        return entity
