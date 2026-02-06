from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.entities import EmploymentType, PersonnelStatus


class PersonnelBase(BaseModel):
    tc_no: str | None = Field(default=None, max_length=20)
    first_name: str
    last_name: str
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")
    email: EmailStr
    birth_date: date | None = None
    hire_date: date
    termination_date: date | None = None
    role_type: str
    employment_type: EmploymentType
    daily_wage: float | None = None
    salary: float | None = None
    status: PersonnelStatus = PersonnelStatus.ACTIVE
    current_site_id: int | None = None
    notes: str | None = None


class PersonnelCreate(PersonnelBase):
    pass


class PersonnelUpdate(BaseModel):
    phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    status: PersonnelStatus | None = None
    current_site_id: int | None = None
    notes: str | None = None


class PersonnelOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    status: PersonnelStatus
    role_type: str
    hire_date: date
    current_site_id: int | None
    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    site_id: int
    start_date: date
    end_date: date | None = None
    position_title: str
    note: str | None = None


class AssignmentOut(BaseModel):
    id: int
    personnel_id: int
    site_id: int
    start_date: date
    end_date: date | None
    position_title: str
    created_at: datetime
    class Config:
        from_attributes = True
