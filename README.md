# Hexonium

Şantiyeler, personeller ve IBAN bilgilerini tek panelde yöneten monorepo.

## 1) Ön Koşullar (özellikle Windows için)

> `npm not found` hatası alıyorsanız büyük ihtimalle Node.js kurulu değil veya PATH'e eklenmemiştir.

### Gerekli yazılımlar
- **Git**
- **Docker Desktop** (önerilen, en kolay yol)
- **Node.js 20+** (frontend'i lokal çalıştıracaksanız)
- **Python 3.11+** (backend'i lokal çalıştıracaksanız)

### Windows'ta Node.js (npm) kurulumu
1. Node.js LTS indirin: `https://nodejs.org/`
2. Kurulumda **"Add to PATH"** seçeneği açık olsun.
3. Kurulum sonrası **CMD'yi kapatıp yeniden açın**.
4. Doğrulama:

```cmd
node -v
npm -v
```

Eğer hala `npm is not recognized` görüyorsanız:
- Bilgisayarı yeniden başlatın.
- `where npm` çalıştırın.
- PATH içine şu klasörün eklendiğini kontrol edin:
  - `C:\Program Files\nodejs\`

---

## 2) En Kolay Kurulum (Docker ile - npm/Python zorunlu değil)

Bu yöntemle host makinede npm kurulu olmasa da proje ayağa kalkar.

```bash
cp .env.example backend/.env
docker compose up --build
```

Servisler:
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

İlk çalıştırmada seed için (opsiyonel):

```bash
docker compose exec backend python seed.py
```

---

## 3) Lokal Kurulum (Docker'sız)

## Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

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

---

## 4) Roller
- Admin
- Muhasebe
- IK
- Santiye Sefi
- Goruntuleyici

## 5) Test

```bash
cd backend
pytest -q
```
