# Agent Instructions — lookatstore_inventory

Sistem informasi persediaan barang berbasis web untuk **UMKM Lookatstore.id Mempawah** (toko fashion wanita: dress, oneset, hijab, dan perlengkapan hijab). Sistem ini dirancang sebagai bagian dari skripsi **Uray Rizky Juniar (221103859)**, Program Studi Sistem Informasi, STMIK Pontianak.

Tujuan sistem: menggantikan pencatatan manual (catatan pribadi) dengan sistem terkomputerisasi yang akurat, real-time, dan mendukung pengambilan keputusan pemilik UMKM.

---

## Tech Stack

| Layer | Tool | Catatan |
|-------|------|---------|
| Backend | **Django 6.0** | Python 3.12, venv di `env/` |
| Database | **PostgreSQL** | Ganti SQLite default di `settings.py` → pakai `psycopg[binary]` |
| Templates | Django templates | Server-rendered HTML. Tidak pakai SPA/JS framework. |
| Styling | **Tailwind CSS via CDN** | Layout data-dense, tipografi Inter, hover states halus (`transition-all`, `hover:-translate-y-0.5`), row highlighting |
| Icons | SVG (Heroicons / Lucide) | **Tidak pakai emoji sebagai ikon** |

## Quick Start

```powershell
# Aktifkan venv (Windows)
.\env\Scripts\activate

# Install adapter PostgreSQL (belum terpasang)
pip install psycopg[binary]

# Jalankan dev server
python manage.py runserver

# Migrasi
python manage.py makemigrations
python manage.py migrate

# Buat superuser
python manage.py createsuperuser
```

## Project Layout

```
lookatstore_inventory/        ← Django project package (settings, urls, wsgi)
  settings.py                 ← DJANGO_SETTINGS_MODULE
  urls.py                     ← Root URL conf
manage.py                     ← Entry point
env/                          ← Python 3.12 virtualenv (JANGAN di-commit)
templates/                    ← Template HTML global
static/                       ← File CSS/JS/gambar statis
.gemini/skills/ui-ux-pro-max/  ← UI/UX design skill (searchable DB + scripts)
```

Setiap fitur utama dibuat sebagai Django app tersendiri (lihat bagian App Scope).

---

## Database Setup (WAJIB DILAKUKAN LEBIH DULU)

`settings.py` saat ini masih pakai SQLite. Ganti ke PostgreSQL:

```python
# lookatstore_inventory/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_lookatstore',
        'USER': 'postgres',
        'PASSWORD': 'valen123',  # Konfirmasi dengan pengguna sebelum menulis
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Konfirmasi kredensial dengan pengguna sebelum menulis ke file.** Selalu jalankan `makemigrations` lalu `migrate` setiap kali ada perubahan model.

Tambahkan juga konfigurasi template dan static files:

```python
TEMPLATES = [{ ..., 'DIRS': [BASE_DIR / 'templates'], ... }]
STATICFILES_DIRS = [BASE_DIR / 'static']
```

---

## App Scope & Batasan

### Ruang Lingkup (diperbarui)

Sistem ini mencakup:

1.  **Master Data**:
    *   **Data Barang** — master data produk (Dress, Oneset, Hijab, dll.).
    *   **Data Kategori** — master data kategori produk.
    *   **Data Supplier** — master data supplier/pemasok barang.
2.  **Barang Masuk** — penerimaan dari supplier (mengisi stok dan mencatat ledger).
3.  **Barang Keluar** — pengeluaran barang (mengurangi stok dan mencatat ledger dengan validasi anti-negatif).
4.  **Riwayat Perubahan Stok (Stock Ledger)** — log audit perubahan stok yang melacak pelaku, waktu, stok awal, stok akhir, selisih, dan tipe transaksi.
5.  **Laporan & Ekspor** — cetak laporan dan ekspor ke **PDF** (via ReportLab) dan **Excel** (via OpenPyXL) dengan filter periode.
6.  **Dashboard & Visualisasi** — visualisasi tren stok per kategori selama 30 hari terakhir menggunakan **Chart.js**.
7.  **Autentikasi** — login dan logout administrator.

---

## Fitur & Model Data

### 1. Autentikasi (`accounts` app)
- Login dan logout menggunakan sistem auth bawaan Django.
- Satu role: **Admin/Pemilik** — akses penuh ke semua master data dan transaksi.

### 2. Master Data & Persediaan (`inventory` app)

Model `Kategori`:
| Field | Tipe | Keterangan |
|-------|------|------------|
| nama | CharField (unique) | Nama kategori (misal: Dress, Hijab, Oneset) |
| deskripsi | TextField (nullable) | Deskripsi kategori |

Model `Supplier`:
| Field | Tipe | Keterangan |
|-------|------|------------|
| nama | CharField (unique) | Nama supplier |
| kontak | CharField (nullable) | Nomor telepon/WhatsApp supplier |
| email | EmailField (nullable) | Alamat email supplier |
| alamat | TextField (nullable) | Alamat fisik supplier |

Model `Barang`:
| Field | Tipe | Keterangan |
|-------|------|------------|
| kode_barang | CharField (unique) | Kode unik produk (misal: BRG-001) |
| nama_produk | CharField | Nama produk |
| kategori | ForeignKey → Kategori | Relasi ke master data kategori |
| satuan | CharField | Satuan (pcs, lusin, dll.) |
| stok | IntegerField | Jumlah stok tersedia (dihitung otomatis) |
| stok_minimum | IntegerField | Batas minimum stok (alert jika stok ≤ minimum) |
| deskripsi | TextField (nullable) | Keterangan tambahan |
| created_at / updated_at | DateTimeField | Timestamp |

### 3. Transaksi & Ledger (`transactions` app)

Model `BarangMasuk`:
| Field | Tipe | Keterangan |
|-------|------|------------|
| tanggal | DateField | Tanggal penerimaan |
| barang | ForeignKey → Barang | Produk yang diterima |
| jumlah | PositiveIntegerField | Jumlah diterima |
| supplier | ForeignKey → Supplier | Relasi ke master data supplier |
| keterangan | TextField (nullable) | Catatan tambahan |
| created_at | DateTimeField | Timestamp |

Model `BarangKeluar`:
| Field | Tipe | Keterangan |
|-------|------|------------|
| tanggal | DateField | Tanggal pengeluaran |
| barang | ForeignKey → Barang | Produk yang keluar |
| jumlah | PositiveIntegerField | Jumlah keluar |
| keterangan | CharField | Alasan (Penjualan / Lainnya) |
| created_at | DateTimeField | Timestamp |

Model `StockLedger` (Riwayat Perubahan Stok):
| Field | Tipe | Keterangan |
|-------|------|------------|
| barang | ForeignKey → Barang | Produk yang mengalami perubahan |
| user | ForeignKey → User (nullable) | Admin yang melakukan perubahan |
| tanggal | DateTimeField | Waktu pencatatan log (auto_now_add) |
| stok_awal | IntegerField | Jumlah stok sebelum perubahan |
| stok_akhir | IntegerField | Jumlah stok setelah perubahan |
| perubahan | IntegerField | Selisih perubahan (misal: +10, -5) |
| tipe_transaksi | CharField | Kategori aksi (Masuk, Keluar, Koreksi, Hapus) |
| referensi_id | IntegerField (nullable) | ID record transaksi (BarangMasuk/BarangKeluar) |
| keterangan | TextField | Penjelasan detail audit log |

### 4. Laporan (`reports` app)
- Laporan Barang Masuk & Keluar dengan filter periode tanggal.
- Fitur Cetak (Print layout ramah printer).
- Fitur **Ekspor Excel** menggunakan openpyxl.
- Fitur **Ekspor PDF** menggunakan reportlab.

---

## Alur Data & Logika Bisnis

```
Barang Masuk / Keluar → Pengecekan Validitas Stok (anti-negatif untuk Keluar)
                      ↓
           Update Stok pada model Barang
                      ↓
  Pencatatan Audit Log di StockLedger (stok_awal, stok_akhir, user, dll.)
```

---

## Dashboard

Komponen halaman utama setelah login:

- **Stat cards:** Total item barang, total barang masuk hari ini, total barang keluar hari ini, jumlah barang dengan stok kritis (≤ stok_minimum)
- **Tabel ringkasan stok** — daftar barang dengan highlight stok rendah (merah/kuning)
- **Aktivitas terkini** — transaksi barang masuk/keluar terbaru (badge hijau = masuk, merah = keluar)
- **Alert stok kritis** — daftar barang yang stoknya sudah di bawah minimum

---

## Konvensi

- **Bahasa UI:** Indonesia (Bahasa Indonesia) untuk semua teks label, judul, pesan, dan konten yang terlihat pengguna
- **Settings module:** `lookatstore_inventory.settings`
- **Struktur app:** setiap fitur besar = 1 Django app (`inventory`, `transactions`, `reports`, `accounts`)
- **Auth:** gunakan sistem auth bawaan Django; tidak perlu role/profile tambahan (single user/admin)
- **Templates:** `DIRS = [BASE_DIR / 'templates']`
- **Static:** `STATICFILES_DIRS = [BASE_DIR / 'static']`
- **Semua elemen klikable** wajib punya `cursor-pointer`
- **Responsif** di 375px, 768px, 1024px, 1440px
- **Tidak pakai unicode bullet** sebagai ikon — pakai SVG

---

 This configuration is universally compatible across AI environments (AGENTS.md, CLAUDE.md, GEMINI.md).

As an AI agent, you must navigate the gap between probabilistic LLM reasoning and the strict, deterministic logic required for real-world applications. To achieve maximum reliability, you will operate strictly under a 3-Tier Workflow.

## The 3-Tier Workflow

**Tier 1: The Blueprint (Directives)**
- Located in the `directives/` folder as Markdown files.
- These are your standard operating procedures (SOPs). They define your objectives, required inputs, authorized scripts, expected outputs, and how to handle edge cases.
- Treat these as clear, natural-language instructions from a human manager.

**Tier 2: The Brain (Orchestration)**
- This is your primary role: intelligent delegation and routing.
- You read the blueprints, trigger the right tools in the correct sequence, manage errors, request human input when stuck, and refine directives based on new findings.
- You are the bridge. Instead of executing complex tasks (like web scraping) directly, you parse the directive and trigger the corresponding script (e.g., `execution/web_scraper.py`).

**Tier 3: The Muscle (Execution)**
- Located in the `execution/` folder as Python scripts.
- These are deterministic, hard-coded tools.
- They handle API requests, file management, data crunching, and database queries.
- They must be fast, heavily commented, and reliable. All sensitive keys reside in `.env`.

*The Philosophy:* Relying solely on AI for multi-step execution causes compounding errors (e.g., 90% accuracy over 5 steps drops to 59% success rate). We solve this by offloading the actual "doing" to deterministic code, freeing you to focus entirely on "thinking" and decision-making.

## Core Rules of Engagement

**1. Search Before You Build**
Always check the `execution/` folder for existing scripts before writing new code. Avoid redundant tool creation.

**2. The Auto-Correction Protocol**
- When an error occurs, analyze the stack trace immediately.
- Fix the execution script and re-test it (unless it consumes paid API credits, in which case you must prompt the user first).
- If you hit constraints (e.g., rate limits), adapt the script, test it, and document the solution.

**3. Evolve the Blueprints**
Directives are living documents. Whenever you discover a better workflow, API limitation, or common bug, update the corresponding file in `directives/`. However, never overwrite or delete a directive entirely without explicit permission. Your instructions must be preserved and improved over time.

## File Organization & Architecture

**Output Types:**
- **Final Deliverables:** Cloud-based access points (Google Sheets, Slides, etc.) meant for the end-user.
- **Temporary Data:** Intermediary files used during operations.

**Directory Map:**
- `.tmp/` - Disposable data (scraped text, temp JSONs). Safe to delete and recreate.
- `execution/` - The deterministic Python scripts.
- `directives/` - Your Markdown instruction manuals.
- `.env` - Environment variables (strictly local).
- `credentials.json` / `token.json` - Auth files (must remain in `.gitignore`).

## System Summary
Your job is to bridge human intent with code execution. Read the blueprints, make smart routing decisions, run the deterministic tools, catch your own errors, and constantly optimize the workflow. Be reliable, practical, and self-correcting.