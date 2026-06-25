# 🚀 Deploy LookAtStore ke Coolify via Docker Compose

Panduan lengkap untuk mendeploy aplikasi **LookAtStore** (Django 6.0.5 + PostgreSQL) ke [Coolify](https://coolify.io) menggunakan Docker Compose tanpa standalone database service terpisah — semua berjalan dalam satu Compose stack.

---

## 📁 Struktur File yang Digunakan

```
lookatstore_inventory/
├── Dockerfile              # Build image Django + Gunicorn
├── docker-compose.yml      # Stack: db + web + nginx
├── entrypoint.sh           # Auto migrate, collectstatic, start Gunicorn
├── nginx.conf              # Reverse proxy + serve static files
├── .env.example            # Template environment variables
├── .dockerignore           # File yang dikecualikan dari Docker build
└── lookatstore_inventory/
    └── settings.py         # Sudah di-update untuk baca dari env vars
```

---

## ✅ Prasyarat

| Kebutuhan | Detail |
|-----------|--------|
| Coolify Server | VPS/server dengan Coolify sudah terinstall |
| Git Repository | Kode project sudah di-push ke GitHub/GitLab/Gitea |
| Domain (opsional) | Untuk HTTPS otomatis via Let's Encrypt |

---

## 🔧 Langkah 1 — Persiapan Repository

### 1.1 Pastikan semua file sudah ada di repo

```bash
git status
# File baru yang harus di-commit:
# - Dockerfile
# - docker-compose.yml
# - entrypoint.sh
# - nginx.conf
# - .env.example
# - .dockerignore
```

### 1.2 Commit dan push ke repository

```bash
git add Dockerfile docker-compose.yml entrypoint.sh nginx.conf .env.example .dockerignore
git add lookatstore_inventory/settings.py
git commit -m "chore: add Docker & Coolify deployment files"
git push origin main
```

> [!IMPORTANT]
> **JANGAN** commit file `.env`! File `.env` sudah ada di `.gitignore`.
> Semua secret key dan password diatur di Coolify, bukan di repository.

---

## 🖥️ Langkah 2 — Setup di Coolify

### 2.1 Buat Project Baru

1. Login ke dashboard Coolify
2. Klik **"+ New Project"**
3. Beri nama project: `lookatstore`
4. Klik **"+ New Resource"**

### 2.2 Tambah Service Docker Compose

1. Pilih tab **"Docker Compose"**
2. Pilih source: **Git Repository**
3. Hubungkan ke GitHub/GitLab/Gitea kamu
4. Pilih repository **lookatstore_inventory**
5. Branch: `main`
6. **Docker Compose File**: `docker-compose.yml`
7. Klik **"Save"**

---

## 🔐 Langkah 3 — Environment Variables

Di halaman service Coolify, masuk ke tab **"Environment Variables"** dan tambahkan variabel berikut:

### Variabel Wajib

| Key | Value | Keterangan |
|-----|-------|------------|
| `SECRET_KEY` | *(generate di bawah)* | Django secret key |
| `DB_PASSWORD` | `password_aman_kamu` | Password database PostgreSQL |

### Generate SECRET_KEY

Jalankan perintah ini untuk generate secret key yang aman:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Atau gunakan Python langsung:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Semua Variabel Environment

```env
SECRET_KEY=hasil-generate-di-atas
DEBUG=False
ALLOWED_HOSTS=domain-kamu.com,www.domain-kamu.com
DB_NAME=db_lookatstore
DB_USER=postgres
DB_PASSWORD=password_aman_kamu
GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=120
```

> [!WARNING]
> Ganti `domain-kamu.com` dengan domain yang sebenarnya. Jika belum punya domain, gunakan IP server sebagai sementara.

---

## 🌐 Langkah 4 — Konfigurasi Domain & HTTPS

### 4.1 Di Coolify

1. Masuk ke tab **"Domains"** pada service nginx
2. Klik **"+ Add Domain"**
3. Masukkan domain: `https://lookatstore.domain-kamu.com`
4. Centang **"Generate SSL Certificate"** → Coolify akan otomatis pakai Let's Encrypt

### 4.2 Update ALLOWED_HOSTS

Setelah domain terdaftar, update environment variable:

```
ALLOWED_HOSTS=lookatstore.domain-kamu.com,www.lookatstore.domain-kamu.com
```

### 4.3 Arahkan DNS ke Server

Di registrar domain kamu, tambahkan record:

```
Type  : A
Name  : lookatstore (atau @)
Value : IP_SERVER_COOLIFY
TTL   : 300
```

---

## 🚢 Langkah 5 — Deploy

### 5.1 Deploy Pertama

1. Di dashboard Coolify, klik tombol **"Deploy"**
2. Pantau log di tab **"Logs"**
3. Urutan yang akan terjadi:
   - Build Docker image
   - Start container `db` (PostgreSQL)
   - Start container `web` (Django + Gunicorn)
     - Menunggu DB ready
     - Jalankan `python manage.py migrate`
     - Jalankan `python manage.py collectstatic`
     - Start Gunicorn
   - Start container `nginx`

### 5.2 Cek Log Deploy

```
==> Waiting for database to be ready...
Database ready after 3 attempt(s).
==> Running database migrations...
Running migrations:
  Applying accounts.0001_initial... OK
  ...
==> Collecting static files...
...static files copied to '/app/staticfiles'.
==> Starting Gunicorn...
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8000
```

---

## 👤 Langkah 6 — Buat Superuser (Opsional)

Setelah deploy berhasil, buat akun admin Django:

### Via Coolify Terminal

1. Di halaman service `web`, buka tab **"Terminal"**
2. Jalankan:

```bash
python manage.py createsuperuser
```

### Via SSH ke Server

```bash
# SSH ke server
ssh user@IP_SERVER

# Masuk ke container web
docker exec -it <nama-container-web> sh

# Buat superuser
python manage.py createsuperuser
```

---

## 🔄 Langkah 7 — Auto-Deploy (CI/CD)

### Aktifkan Webhook

1. Di Coolify → Service → tab **"Webhooks"**
2. Copy URL webhook yang tersedia
3. Di GitHub: **Settings → Webhooks → Add webhook**
4. Paste URL webhook, pilih event **"Push"**
5. Klik **"Add webhook"**

Sekarang setiap kali kamu `git push`, Coolify akan otomatis rebuild dan redeploy!

---

## 🗄️ Backup Database

### Manual Backup

```bash
# SSH ke server Coolify
docker exec -t <container-db> pg_dump -U postgres db_lookatstore > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
docker exec -i <container-db> psql -U postgres db_lookatstore < backup_20260101.sql
```

---

## 🛠️ Troubleshooting

### Error: `DB_PASSWORD is required`

**Penyebab**: Environment variable `DB_PASSWORD` belum diset di Coolify.
**Solusi**: Pastikan `DB_PASSWORD` sudah ditambahkan di tab Environment Variables Coolify.

---

### Error: `ALLOWED_HOSTS` (400 Bad Request)

**Penyebab**: Domain belum ditambahkan ke `ALLOWED_HOSTS`.
**Solusi**: Update environment variable:
```
ALLOWED_HOSTS=domain-kamu.com,www.domain-kamu.com
```

---

### Static files tidak muncul (CSS/JS kosong)

**Penyebab**: `collectstatic` gagal atau path volume tidak tepat.
**Solusi**:
```bash
# Masuk ke container web
docker exec -it <container-web> sh
python manage.py collectstatic --noinput
```

---

### Container `web` terus restart

**Penyebab**: Database belum siap saat web dimulai.
**Solusi**: `entrypoint.sh` sudah handle ini dengan retry 30x. Cek log untuk detail error.

---

### Error 502 Bad Gateway

**Penyebab**: Nginx tidak bisa terhubung ke Gunicorn.
**Solusi**: Pastikan container `web` berjalan normal:
```bash
docker ps
docker logs <container-web>
```

---

## 📊 Arsitektur Deployment

```
Internet
   │
   ▼
[Coolify Proxy / Traefik]
   │ HTTPS (443)
   ▼
[nginx:80]  ──────────────────┐
   │                          │
   │ /static/  →  staticfiles │ (shared volume)
   │ /media/   →  mediafiles  │
   │                          │
   │ / (proxy_pass)           │
   ▼                          │
[web:8000 - Gunicorn]         │
   │                          │
   │ DB connection            │
   ▼                          │
[db:5432 - PostgreSQL]        │
   │                          │
   └──── postgres_data ───────┘ (named volume)
```

---

*Dibuat untuk project LookAtStore — Django 6.0.5 + PostgreSQL*
