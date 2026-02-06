# Hexonium

Şantiyeler, personeller ve IBAN bilgilerini tek panelde yöneten monorepo.

## Kurulum

```bash
cp .env.example backend/.env
docker compose up --build
```

## Backend

```bash
cd backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

Swagger: `http://localhost:8000/docs`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Roller
- Admin
- Muhasebe
- IK
- Santiye Sefi
- Goruntuleyici

## Test

```bash
cd backend
pytest -q
```
