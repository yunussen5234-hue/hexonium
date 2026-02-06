from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    ADMIN = "Admin"
    ACCOUNTING = "Muhasebe"
    HR = "IK"
    SITE_CHIEF = "SantiyeSefi"
    VIEWER = "Goruntuleyici"


class SiteStatus(str, Enum):
    ACTIVE = "Aktif"
    PASSIVE = "Pasif"


class PersonnelStatus(str, Enum):
    ACTIVE = "Aktif"
    ON_LEAVE = "Izinli"
    LEFT = "Ayrildi"


class EmploymentType(str, Enum):
    FULL_TIME = "Kadrolu"
    CONTRACTOR = "Taseron"
    DAILY = "Gunluk"


class CurrencyType(str, Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"


class RecordStatus(str, Enum):
    ACTIVE = "Aktif"
    PASSIVE = "Pasif"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SqlEnum(Role), nullable=False)
    site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[SiteStatus] = mapped_column(SqlEnum(SiteStatus), default=SiteStatus.ACTIVE)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Personnel(Base):
    __tablename__ = "personnel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tc_no: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(120))
    last_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    hire_date: Mapped[date] = mapped_column(Date)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    role_type: Mapped[str] = mapped_column(String(80))
    employment_type: Mapped[EmploymentType] = mapped_column(SqlEnum(EmploymentType))
    daily_wage: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[PersonnelStatus] = mapped_column(SqlEnum(PersonnelStatus), default=PersonnelStatus.ACTIVE)
    current_site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PersonnelSiteAssignment(Base):
    __tablename__ = "personnel_site_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    personnel_id: Mapped[int] = mapped_column(ForeignKey("personnel.id"))
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    position_title: Mapped[str] = mapped_column(String(120))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    personnel_id: Mapped[int] = mapped_column(ForeignKey("personnel.id"))
    iban_encrypted: Mapped[str] = mapped_column(Text)
    iban_masked: Mapped[str] = mapped_column(String(34))
    bank_name: Mapped[str] = mapped_column(String(120))
    branch_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    account_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    currency: Mapped[CurrencyType] = mapped_column(SqlEnum(CurrencyType), default=CurrencyType.TRY)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[RecordStatus] = mapped_column(SqlEnum(RecordStatus), default=RecordStatus.ACTIVE)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(50))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(80))
    before_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
