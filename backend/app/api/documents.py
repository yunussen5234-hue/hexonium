import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import Document, DocumentType, Personnel, PersonnelStatus, RecordStatus, Role
from app.schemas.document import DocumentCreate, DocumentOut, NewVersionRequest
from app.schemas.personnel import TerminatePersonnelRequest
from app.services.audit_service import AuditService
from app.utils.errors import api_error

router = APIRouter(tags=["Evraklar"])

BASE_UPLOAD = Path("storage/uploads")
BASE_UPLOAD.mkdir(parents=True, exist_ok=True)
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE = 20 * 1024 * 1024


@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.ACCOUNTING))):
    if file.content_type not in ALLOWED_TYPES:
        api_error("INVALID_FILE_TYPE", "Sadece pdf/jpg/png/docx yüklenebilir")
    content = await file.read()
    if len(content) > MAX_SIZE:
        api_error("FILE_TOO_LARGE", "Maksimum dosya boyutu 20MB")
    ext = Path(file.filename).suffix
    key = f"{datetime.utcnow().strftime('%Y/%m')}/{uuid.uuid4().hex}{ext}"
    path = BASE_UPLOAD / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return {"storageKey": key, "fileNameOriginal": file.filename, "mimeType": file.content_type, "fileSize": len(content)}


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    siteId: int | None = None,
    personnelId: int | None = None,
    type: DocumentType | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Document).filter(Document.deleted_at.is_(None))
    if siteId:
        q = q.filter(Document.site_id == siteId)
    if personnelId:
        q = q.filter(Document.personnel_id == personnelId)
    if type:
        q = q.filter(Document.document_type == type)
    return q.order_by(Document.uploaded_at.desc()).all()


@router.post("/documents", response_model=DocumentOut)
def create_document(payload: DocumentCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.ACCOUNTING))):
    doc = Document(**payload.model_dump(), uploaded_by_user_id=user.id)
    db.add(doc)
    db.flush()
    AuditService.log(db, user, "create", "document", str(doc.id), None, payload.model_dump(), request.client.host if request.client else None)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/documents/{doc_id}/new-version", response_model=DocumentOut)
def new_version(doc_id: int, payload: NewVersionRequest, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.ACCOUNTING))):
    old = db.query(Document).filter(Document.id == doc_id, Document.deleted_at.is_(None)).first()
    if not old:
        api_error("NOT_FOUND", "Evrak bulunamadı", status_code=404)
    doc = Document(
        personnel_id=old.personnel_id,
        site_id=old.site_id,
        document_type=old.document_type,
        file_name_original=payload.file_name_original,
        file_storage_key=payload.file_storage_key,
        mime_type=payload.mime_type,
        file_size=payload.file_size,
        version=old.version + 1,
        uploaded_by_user_id=user.id,
        description=old.description,
        effective_date=old.effective_date,
    )
    db.add(doc)
    AuditService.log(db, user, "new_version", "document", str(doc_id), {"version": old.version}, {"version": old.version + 1}, request.client.host if request.client else None)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents/{doc_id}/download")
def download(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.deleted_at.is_(None)).first()
    if not doc:
        api_error("NOT_FOUND", "Evrak bulunamadı", status_code=404)
    file_path = BASE_UPLOAD / doc.file_storage_key
    if not file_path.exists():
        api_error("FILE_NOT_FOUND", "Dosya depoda bulunamadı", status_code=404)
    return FileResponse(path=file_path, filename=doc.file_name_original, media_type=doc.mime_type)


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR, Role.ACCOUNTING))):
    doc = db.query(Document).filter(Document.id == doc_id, Document.deleted_at.is_(None)).first()
    if not doc:
        api_error("NOT_FOUND", "Evrak bulunamadı", status_code=404)
    doc.deleted_at = datetime.utcnow()
    doc.status = RecordStatus.DELETED
    AuditService.log(db, user, "delete", "document", str(doc_id), {"deleted": False}, {"deleted": True}, request.client.host if request.client else None)
    db.commit()
    return {"ok": True}


@router.get("/personnel/{personnel_id}/documents/summary")
def personnel_documents_summary(personnel_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    docs = db.query(Document).filter(Document.personnel_id == personnel_id, Document.deleted_at.is_(None)).all()
    loaded = {d.document_type.value for d in docs}
    required = {DocumentType.ISE_GIRIS.value, DocumentType.SOZLESME.value, DocumentType.ISG.value, DocumentType.KKD.value}
    missing = sorted(list(required - loaded))
    return {"loadedCount": len(required) - len(missing), "requiredCount": len(required), "missingTypes": missing}


@router.post("/personnel/{personnel_id}/terminate")
def terminate_personnel(personnel_id: int, payload: TerminatePersonnelRequest, request: Request, db: Session = Depends(get_db), user=Depends(require_roles(Role.ADMIN, Role.HR))):
    person = db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.deleted_at.is_(None)).first()
    if not person:
        api_error("NOT_FOUND", "Personel bulunamadı", status_code=404)

    required = {DocumentType.CIKIS_BILDIRGESI}
    existing = {
        d.document_type
        for d in db.query(Document).filter(Document.personnel_id == personnel_id, Document.deleted_at.is_(None)).all()
    }
    missing = [d.value for d in required if d not in existing]

    person.termination_date = payload.termination_date
    person.termination_reason = payload.reason
    if missing:
        person.exit_process_status = "Taslak"
        AuditService.log(
            db,
            user,
            "terminate_draft",
            "personnel",
            str(personnel_id),
            None,
            {"missing": missing, "terminationDate": str(payload.termination_date)},
            request.client.host if request.client else None,
        )
        db.commit()
        return {"status": "draft", "message": "Çıkış evrakları eksik. Lütfen Çıkış Bildirgesi yükleyin.", "missing": missing}

    person.status = PersonnelStatus.LEFT
    person.exit_process_status = "Tamamlandi"
    AuditService.log(db, user, "terminate", "personnel", str(personnel_id), None, payload.model_dump(), request.client.host if request.client else None)
    db.commit()
    return {"status": "completed"}
