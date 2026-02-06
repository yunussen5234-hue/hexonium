from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app
from app.models.entities import Base, Role, User
from app.utils.security import SecurityService

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth_header():
    db = TestingSessionLocal()
    if not db.query(User).filter(User.email == "admin@test.local").first():
        db.add(User(email="admin@test.local", full_name="Admin", hashed_password=SecurityService.hash_password("Admin123!"), role=Role.ADMIN))
        db.commit()
    db.close()
    token = client.post("/auth/login", json={"email": "admin@test.local", "password": "Admin123!"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health():
    assert client.get("/health").status_code == 200


def test_login():
    assert client.post("/auth/login", json={"email": "admin@test.local", "password": "Admin123!"}).status_code == 200


def test_create_site_and_list():
    h = auth_header()
    payload = {"code": "S1", "name": "Şantiye 1", "address": "A", "city": "İstanbul", "start_date": str(date.today()), "status": "Aktif"}
    assert client.post("/sites", json=payload, headers=h).status_code == 200
    assert client.get("/sites", headers=h).status_code == 200


def test_get_update_delete_site():
    h = auth_header()
    assert client.get("/sites/1", headers=h).status_code == 200
    assert client.patch("/sites/1", json={"name": "Güncel"}, headers=h).status_code == 200
    assert client.delete("/sites/1", headers=h).status_code == 200


def test_personnel_crud_and_assignments():
    h = auth_header()
    p = {
        "first_name": "Ali", "last_name": "Veli", "phone": "+905551112233", "email": "ali@test.local", "hire_date": str(date.today()),
        "role_type": "İşçi", "employment_type": "Kadrolu", "status": "Aktif"
    }
    assert client.post("/personnel", json=p, headers=h).status_code == 200
    assert client.get("/personnel", headers=h).status_code == 200
    assert client.get("/personnel/1", headers=h).status_code == 200
    assert client.patch("/personnel/1", json={"notes": "test"}, headers=h).status_code == 200
    assign = {"site_id": 1, "start_date": str(date.today()), "position_title": "Ustabaşı"}
    assert client.post("/personnel/1/assignments", json=assign, headers=h).status_code == 200
    assert client.get("/personnel/1/assignments", headers=h).status_code == 200
    assert client.patch("/personnel/assignments/1", json=assign, headers=h).status_code == 200
    assert client.delete("/personnel/assignments/1", headers=h).status_code == 200
    assert client.delete("/personnel/1", headers=h).status_code == 200


def test_bank_dashboard_audit():
    h = auth_header()
    p = {
        "first_name": "Ayşe", "last_name": "Y", "phone": "+905551112244", "email": "ayse@test.local", "hire_date": str(date.today()),
        "role_type": "Mühendis", "employment_type": "Kadrolu", "status": "Aktif"
    }
    client.post("/personnel", json=p, headers=h)
    ba = {"personnel_id": 2, "iban": "TR330006100519786457841326", "bank_name": "Ziraat", "is_primary": True}
    assert client.post("/bank-accounts", json=ba, headers=h).status_code == 200
    assert client.get("/bank-accounts", headers=h).status_code == 200
    assert client.get("/bank-accounts/1/reveal", headers=h).status_code == 200
    assert client.patch("/bank-accounts/1", json={"is_primary": True}, headers=h).status_code == 200
    assert client.delete("/bank-accounts/1", headers=h).status_code == 200
    assert client.get("/reports/dashboard", headers=h).status_code == 200
    assert client.get("/reports/sites/1/personnel.csv", headers=h).status_code == 200
    assert client.get("/audit-logs", headers=h).status_code == 200
