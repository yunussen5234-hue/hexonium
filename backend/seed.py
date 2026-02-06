from datetime import date

from app.db.session import SessionLocal, engine
from app.models.entities import (
    Base,
    Document,
    DocumentType,
    EmploymentType,
    Personnel,
    PersonnelStatus,
    Role,
    Site,
    SiteStatus,
    User,
)
from app.utils.security import SecurityService

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(Site).first():
    sites = [
        Site(code="SNT-001", name="Merkez Şantiye", address="Adres 1", city="İstanbul", start_date=date(2024, 1, 5), status=SiteStatus.ACTIVE),
        Site(code="SNT-002", name="Ankara Şantiye", address="Adres 2", city="Ankara", start_date=date(2024, 2, 1), status=SiteStatus.ACTIVE),
    ]
    db.add_all(sites)
    db.flush()

    users = [
        User(email="admin@hexonium.local", full_name="Sistem Admin", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.ADMIN),
        User(email="hr@hexonium.local", full_name="IK Uzmanı", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.HR),
    ]
    db.add_all(users)

    people = []
    for i in range(1, 11):
        people.append(
            Personnel(
                first_name=f"Personel{i}",
                last_name="Test",
                phone=f"+905550000{i:03d}",
                email=f"personel{i}@hexonium.local",
                hire_date=date(2024, 1, 1),
                role_type="İşçi",
                employment_type=EmploymentType.FULL_TIME,
                status=PersonnelStatus.ACTIVE,
                current_site_id=(i % 2) + 1,
                payment_type="Banka",
            )
        )
    db.add_all(people)
    db.flush()

    docs = [
        Document(
            personnel_id=1,
            site_id=1,
            document_type=DocumentType.ISE_GIRIS,
            file_name_original="ise-giris-1.pdf",
            file_storage_key="seed/ise-giris-1.pdf",
            mime_type="application/pdf",
            file_size=12345,
            version=1,
            uploaded_by_user_id=1,
        ),
        Document(
            personnel_id=1,
            site_id=1,
            document_type=DocumentType.SOZLESME,
            file_name_original="sozlesme-1.pdf",
            file_storage_key="seed/sozlesme-1.pdf",
            mime_type="application/pdf",
            file_size=12345,
            version=1,
            uploaded_by_user_id=1,
        ),
        Document(
            personnel_id=2,
            site_id=2,
            document_type=DocumentType.CIKIS_BILDIRGESI,
            file_name_original="cikis-2.pdf",
            file_storage_key="seed/cikis-2.pdf",
            mime_type="application/pdf",
            file_size=12000,
            version=1,
            uploaded_by_user_id=1,
        ),
    ]
    db.add_all(docs)
    db.commit()

print("Seed tamamlandı")
