from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    DELETED = "Silindi"


class DocumentType(str, Enum):
    ISE_GIRIS = "ise_giris"
    SOZLESME = "sozlesme"
    IBRANAME = "ibraname"
    ISG = "isg"
    KKD = "kkd"
    ISTIFA = "istifa"
    CIKIS_BILDIRGESI = "cikis_bildirgesi"


class DocumentReviewStatus(str, Enum):
    UPLOADED = "Yuklu"
    MISSING = "Eksik"
    APPROVED = "Onayli"
    REJECTED = "Reddedildi"


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
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    hire_date: Mapped[date] = mapped_column(Date)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    termination_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exit_process_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    role_type: Mapped[str] = mapped_column(String(80))
    employment_type: Mapped[EmploymentType] = mapped_column(SqlEnum(EmploymentType))
    daily_wage: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    payment_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[PersonnelStatus] = mapped_column(SqlEnum(PersonnelStatus), default=PersonnelStatus.ACTIVE)
    current_site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
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


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    personnel_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True)
    site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    document_type: Mapped[DocumentType] = mapped_column(SqlEnum(DocumentType), nullable=False)
    file_name_original: Mapped[str] = mapped_column(String(255))
    file_storage_key: Mapped[str] = mapped_column(String(255), unique=True)
    mime_type: Mapped[str] = mapped_column(String(120))
    file_size: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[RecordStatus] = mapped_column(SqlEnum(RecordStatus), default=RecordStatus.ACTIVE)
    review_status: Mapped[DocumentReviewStatus] = mapped_column(SqlEnum(DocumentReviewStatus), default=DocumentReviewStatus.UPLOADED)
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


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
