from datetime import date, datetime

from pydantic import BaseModel

from app.models.entities import DocumentType, RecordStatus


class DocumentCreate(BaseModel):
    personnel_id: int | None = None
    site_id: int | None = None
    document_type: DocumentType
    file_name_original: str
    file_storage_key: str
    mime_type: str
    file_size: int
    description: str | None = None
    effective_date: date | None = None


class NewVersionRequest(BaseModel):
    file_storage_key: str
    file_name_original: str
    mime_type: str
    file_size: int


class DocumentOut(BaseModel):
    id: int
    personnel_id: int | None
    site_id: int | None
    document_type: DocumentType
    file_name_original: str
    file_storage_key: str
    mime_type: str
    file_size: int
    version: int
    status: RecordStatus
    uploaded_at: datetime
    description: str | None

    class Config:
        from_attributes = True
