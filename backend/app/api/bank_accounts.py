from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import BankAccount, Role
from app.schemas.bank_account import BankAccountCreate, BankAccountOut, BankAccountUpdate
from app.services.audit_service import AuditService
from app.services.bank_service import BankService
from app.utils.errors import api_error
from app.utils.security import SecurityService

router = APIRouter(prefix="/bank-accounts", tags=["IBAN Yönetimi"])


@router.get("", response_model=list[BankAccountOut])
def list_accounts(personnelId: int | None = None, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING, Role.HR, Role.SITE_CHIEF))):
    rows = BankService.list_accounts(db, personnelId)
    can_reveal = user.role in (Role.ADMIN, Role.ACCOUNTING)
    out = []
    for r in rows:
        out.append(BankAccountOut(
            id=r.id,
            personnel_id=r.personnel_id,
            iban=SecurityService.decrypt_value(r.iban_encrypted) if can_reveal else r.iban_masked,
            bank_name=r.bank_name,
            is_primary=r.is_primary,
            status=r.status,
            created_at=r.created_at,
        ))
    return out


@router.post("", response_model=BankAccountOut)
def create_account(payload: BankAccountCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING))):
    account = BankService.create(db, payload, user, request.client.host if request.client else None)
    db.commit()
    db.refresh(account)
    return BankAccountOut(
        id=account.id,
        personnel_id=account.personnel_id,
        iban=account.iban_masked,
        bank_name=account.bank_name,
        is_primary=account.is_primary,
        status=account.status,
        created_at=account.created_at,
    )


@router.patch("/{account_id}")
def update_account(account_id: int, payload: BankAccountUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING))):
    account = db.query(BankAccount).filter(BankAccount.id == account_id, BankAccount.deleted_at.is_(None)).first()
    if not account:
        api_error("NOT_FOUND", "Banka hesabı bulunamadı", status_code=404)
    BankService.update(db, account, payload, user, request.client.host if request.client else None)
    db.commit()
    return {"ok": True}


@router.delete("/{account_id}")
def delete_account(account_id: int, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING))):
    account = db.query(BankAccount).filter(BankAccount.id == account_id, BankAccount.deleted_at.is_(None)).first()
    if not account:
        api_error("NOT_FOUND", "Banka hesabı bulunamadı", status_code=404)
    account.deleted_at = datetime.utcnow()
    AuditService.log(db, user, "delete", "bank_account", str(account_id), None, {"deleted": True}, request.client.host if request.client else None)
    db.commit()
    return {"ok": True}


@router.get("/{account_id}/reveal")
def reveal_account(account_id: int, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.ACCOUNTING))):
    account = db.query(BankAccount).filter(BankAccount.id == account_id, BankAccount.deleted_at.is_(None)).first()
    if not account:
        api_error("NOT_FOUND", "Banka hesabı bulunamadı", status_code=404)
    return {"iban": SecurityService.decrypt_value(account.iban_encrypted)}
