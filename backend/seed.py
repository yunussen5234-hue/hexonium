from datetime import date

from app.db.session import SessionLocal, engine
from app.models.entities import (
    Base,
    BankAccount,
    EmploymentType,
    Personnel,
    PersonnelStatus,
    Role,
    Site,
    SiteStatus,
    User,
)
from app.utils.iban import mask_iban
from app.utils.security import SecurityService

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(Site).first():
    sites = [
        Site(code="SNT-001", name="Merkez Şantiye", address="Adres 1", city="İstanbul", start_date=date(2024, 1, 5), status=SiteStatus.ACTIVE),
        Site(code="SNT-002", name="Ankara Şantiye", address="Adres 2", city="Ankara", start_date=date(2024, 2, 1), status=SiteStatus.ACTIVE),
        Site(code="SNT-003", name="İzmir Şantiye", address="Adres 3", city="İzmir", start_date=date(2024, 3, 1), status=SiteStatus.PASSIVE),
    ]
    db.add_all(sites)
    db.flush()

    users = [
        User(email="admin@hexonium.local", full_name="Sistem Admin", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.ADMIN),
        User(email="muhasebe@hexonium.local", full_name="Muhasebe Kullanıcısı", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.ACCOUNTING),
        User(email="sef1@hexonium.local", full_name="Şef 1", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.SITE_CHIEF, site_id=1),
        User(email="sef2@hexonium.local", full_name="Şef 2", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.SITE_CHIEF, site_id=2),
    ]
    db.add_all(users)

    people = []
    for i in range(1, 16):
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
                current_site_id=(i % 3) + 1,
            )
        )
    db.add_all(people)
    db.flush()

    iban = "TR330006100519786457841326"
    for i in range(1, 11):
        db.add(
            BankAccount(
                personnel_id=i,
                iban_encrypted=SecurityService.encrypt_value(iban),
                iban_masked=mask_iban(iban),
                bank_name="Ziraat",
                is_primary=True,
            )
        )

    db.commit()

print("Seed tamamlandı")
