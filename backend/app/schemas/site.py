from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.entities import SiteStatus


class SiteBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str
    address: str
    city: str
    start_date: date
    end_date: date | None = None
    status: SiteStatus = SiteStatus.ACTIVE
    description: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.start_date >= self.end_date:
            raise ValueError("Başlangıç tarihi bitiş tarihinden küçük olmalıdır")
        return self


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SiteStatus | None = None
    description: str | None = None


class SiteOut(BaseModel):
    id: int
    code: str
    name: str
    city: str
    status: SiteStatus
    start_date: date
    personnel_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class AssignPersonnelRequest(BaseModel):
    personnel_ids: list[int]
