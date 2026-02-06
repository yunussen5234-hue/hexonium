from sqlalchemy.orm import Session

from app.models.entities import BankAccount, User
from app.schemas.bank_account import BankAccountCreate, BankAccountUpdate
from app.services.audit_service import AuditService
from app.utils.iban import mask_iban, normalize_iban, validate_tr_iban
from app.utils.security import SecurityService
from app.utils.errors import api_error


class BankService:
    @staticmethod
    def list_accounts(db: Session, personnel_id: int | None = None):
        q = db.query(BankAccount).filter(BankAccount.deleted_at.is_(None))
        if personnel_id:
            q = q.filter(BankAccount.personnel_id == personnel_id)
        return q.order_by(BankAccount.created_at.desc()).all()

    @staticmethod
    def create(db: Session, payload: BankAccountCreate, actor: User, ip: str | None):
        iban = normalize_iban(payload.iban)
        if not validate_tr_iban(iban):
            api_error("INVALID_IBAN", "TR IBAN formatı geçersiz")
        if payload.is_primary:
            db.query(BankAccount).filter(BankAccount.personnel_id == payload.personnel_id).update({"is_primary": False})
        account = BankAccount(
            personnel_id=payload.personnel_id,
            iban_encrypted=SecurityService.encrypt_value(iban),
            iban_masked=mask_iban(iban),
            bank_name=payload.bank_name,
            branch_name=payload.branch_name,
            account_name=payload.account_name,
            currency=payload.currency,
            is_primary=payload.is_primary,
        )
        db.add(account)
        db.flush()
        AuditService.log(db, actor, "create", "bank_account", str(account.id), None, {"personnel_id": payload.personnel_id}, ip)
        return account

    @staticmethod
    def update(db: Session, account: BankAccount, payload: BankAccountUpdate, actor: User, ip: str | None):
        data = payload.model_dump(exclude_unset=True)
        if data.get("is_primary"):
            db.query(BankAccount).filter(BankAccount.personnel_id == account.personnel_id).update({"is_primary": False})
        for k, v in data.items():
            setattr(account, k, v)
        AuditService.log(db, actor, "update", "bank_account", str(account.id), None, data, ip)
        return account
