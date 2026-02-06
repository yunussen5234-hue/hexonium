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

## 2) Windows CMD ile Docker Kurulumu (ÖNERİLEN)

Sizde hata veren nokta doğru: **CMD içinde `bash` ve `cp` komutları çalışmaz**.
Bu yüzden aşağıdaki komutları **aynen CMD'de** kullanın.

### Adım 1: Proje klasörüne girin

```cmd
cd C:\Users\Yunus Emre\Desktop\hexonium-codex-create-project-plan-for-management-system
```

### Adım 2: `.env` dosyasını oluşturun (CMD)

```cmd
copy .env.example backend\.env
```

> Eğer `copy` başarısız olursa PowerShell alternatifi:
>
> ```powershell
> Copy-Item .env.example backend/.env
> ```

### Adım 3: Docker servislerini başlatın

```cmd
docker compose up --build
```

### Adım 4: Uygulama adresleri
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### Adım 5: Seed veri yükleme (yeni CMD penceresi)

```cmd
docker compose exec backend python seed.py
```

### Adım 6: Durdurma

```cmd
docker compose down
```

---

## 3) Sık Hata ve Net Çözüm

### Hata: `bash ... /bin/bash no such file`
Sebep: WSL/Git Bash ortamı yok.
Çözüm: CMD'de `bash` kullanmayın, direkt `docker compose ...` kullanın.

### Hata: `'cp' is not recognized`
Sebep: `cp` Linux komutu.
Çözüm: CMD'de `copy`, PowerShell'de `Copy-Item` kullanın.


### Hata: `docker compose up --build` sırasında `frontend` adımında takılıyor
Sebep: Önceki sürümde frontend build aşamasında `npm install` gerekiyordu. Bazı ağ/proxy ortamlarında bu adım kilitlenebiliyordu.

✅ Güncel sürümde frontend Docker imajı **npm çalıştırmaz** (nginx ile statik servis).
Bu yüzden artık doğrudan şu komut yeterli:

```cmd
docker compose down
docker compose up --build
```

Detaylı log için (doğru compose global flag sözdizimi):

```cmd
docker compose --progress=plain build --no-cache frontend
```

### Hata: `docker compose` komutu yok
Çözüm:
1. Docker Desktop kurulu mu kontrol edin.
2. Docker Desktop açık mı kontrol edin.
3. Yeni CMD açıp tekrar deneyin:

```cmd
docker --version
docker compose version
```

---

## 4) Lokal Kurulum (Docker'sız)

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

## 5) Roller
- Admin
- Muhasebe
- IK
- Santiye Sefi
- Goruntuleyici

## 6) Test

```bash
cd backend
pytest -q
```
