from datetime import datetime

from pydantic import BaseModel

from app.models.entities import CurrencyType, RecordStatus


class BankAccountCreate(BaseModel):
    personnel_id: int
    iban: str
    bank_name: str
    branch_name: str | None = None
    account_name: str | None = None
    currency: CurrencyType = CurrencyType.TRY
    is_primary: bool = False


class BankAccountUpdate(BaseModel):
    bank_name: str | None = None
    status: RecordStatus | None = None
    is_primary: bool | None = None


class BankAccountOut(BaseModel):
    id: int
    personnel_id: int
    iban: str
    bank_name: str
    is_primary: bool
    status: RecordStatus
    created_at: datetime
    class Config:
        from_attributes = True
