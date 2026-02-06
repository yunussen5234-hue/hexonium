# Hexonium

Şantiyeler, personeller, IBAN ve evrak süreçlerini tek panelde yöneten monorepo.

## Hızlı Başlatma (Windows CMD)

```cmd
cd C:\Users\Yunus Emre\Desktop\hexonium\hexonium
copy .env.example backend\.env
docker compose up --build
```

Adresler:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

Seed yüklemek için:

```cmd
docker compose exec backend python seed.py
```

## Modüller
- Personel Yönetimi (3 aşama wizard UI)
- Evrak Yönetimi (dosya gezgini görünümü + personel evrak özeti)
- Şantiye (liste + filtre)
- IBAN yönetimi (maskeli/tam rol bazlı)
- Audit log

## Yeni API'ler (minimum)
- `POST /files/upload` (multipart)
- `GET /documents`
- `POST /documents`
- `POST /documents/:id/new-version`
- `GET /documents/:id/download`
- `DELETE /documents/:id`
- `GET /personnel/:id/documents/summary`
- `POST /personnel/:id/terminate`

## Çıkış Kuralı
`POST /personnel/:id/terminate` çağrısında `cikis_bildirgesi` yoksa personel **Taslak çıkış** durumuna alınır ve uyarı döner.

## Lokal Çalıştırma

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

### Frontend
Frontend Docker içinde nginx ile statik servis edilir (`frontend/index.html`).


## Backend Hatası: `email-validator is not installed`
Eğer `docker compose up --build` logunda bu hatayı görürseniz, image eski cache ile kalmış olabilir.

```cmd
docker compose down
docker compose build --no-cache backend
docker compose up
```

Bu repo içinde backend bağımlılığına `email-validator` eklendi.
