"""
seed_initial.py — Safe deployment seeder for LookAtStore.

Logic:
- Hanya membuat data JIKA belum ada sama sekali (cek per tabel).
- Jika data sudah ada → lewati, tidak ada yang dihapus / ditimpa.
- Aman dijalankan berulang kali (idempotent).
"""

import os
import sys
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lookatstore_inventory.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Barang, Kategori, Supplier
from transactions.models import BarangMasuk, BarangKeluar, StockLedger

User = get_user_model()


def seed_superuser():
    if User.objects.filter(is_superuser=True).exists():
        print("[SKIP] Superuser sudah ada — tidak dibuat ulang.")
        return None
    admin = User.objects.create_superuser('admin', 'admin@lookatstore.id', 'adminpassword123')
    print("[OK]   Superuser 'admin' dibuat.")
    return admin


def seed_kategori():
    names = ['Dress', 'Oneset', 'Hijab', 'Perlengkapan Hijab', 'Lainnya']
    created_count = 0
    kategoris = {}
    for name in names:
        obj, created = Kategori.objects.get_or_create(nama=name)
        kategoris[name] = obj
        if created:
            created_count += 1
    if created_count:
        print(f"[OK]   {created_count} kategori dibuat.")
    else:
        print("[SKIP] Semua kategori sudah ada.")
    return kategoris


def seed_supplier():
    supplier_data = [
        {"nama": "Supplier Hijab Pontianak", "kontak": "08123456789", "email": "pontianak@hijab.com",  "alamat": "Jl. Ahmad Yani No. 12, Pontianak"},
        {"nama": "CV Dress Indah Bandung",   "kontak": "08234567890", "email": "bandung@dress.com",    "alamat": "Kawasan Industri Batununggal, Bandung"},
        {"nama": "Grosir Oneset Jakarta",    "kontak": "08345678901", "email": "jakarta@oneset.com",   "alamat": "Tanah Abang Blok A, Jakarta"},
    ]
    created_count = 0
    suppliers = []
    for s_info in supplier_data:
        obj, created = Supplier.objects.get_or_create(
            nama=s_info["nama"],
            defaults={k: v for k, v in s_info.items() if k != "nama"},
        )
        suppliers.append(obj)
        if created:
            created_count += 1
    if created_count:
        print(f"[OK]   {created_count} supplier dibuat.")
    else:
        print("[SKIP] Semua supplier sudah ada.")
    return suppliers


def seed_barang(kategoris):
    products_data = [
        {"kode_barang": "DRS001", "nama_produk": "Dress Silk Jasmine",         "kategori": kategoris["Dress"],             "satuan": "pcs", "stok": 0, "stok_minimum": 5,  "deskripsi": "Dress sutra premium motif bunga melati"},
        {"kode_barang": "DRS002", "nama_produk": "Gamis Rayon Plain",           "kategori": kategoris["Dress"],             "satuan": "pcs", "stok": 0, "stok_minimum": 10, "deskripsi": "Gamis bahan rayon adem untuk harian"},
        {"kode_barang": "HJB001", "nama_produk": "Pashmina Ceruty Baby Doll",   "kategori": kategoris["Hijab"],             "satuan": "pcs", "stok": 0, "stok_minimum": 15, "deskripsi": "Hijab pashmina ceruty tekstur pasir premium"},
        {"kode_barang": "HJB002", "nama_produk": "Hijab Segiempat Voal Bella",  "kategori": kategoris["Hijab"],             "satuan": "pcs", "stok": 0, "stok_minimum": 20, "deskripsi": "Hijab voal segiempat bestseller harian"},
        {"kode_barang": "ONS001", "nama_produk": "Oneset Linen Cargo",          "kategori": kategoris["Oneset"],            "satuan": "pcs", "stok": 0, "stok_minimum": 4,  "deskripsi": "Satu set kemeja dan celana kargo bahan linen"},
        {"kode_barang": "ONS002", "nama_produk": "Oneset Knit Ribbed",          "kategori": kategoris["Oneset"],            "satuan": "pcs", "stok": 0, "stok_minimum": 5,  "deskripsi": "Setelan rajut rib hangat dan stylish"},
        {"kode_barang": "PLK001", "nama_produk": "Ciput Rajut Anti Pusing",     "kategori": kategoris["Perlengkapan Hijab"],"satuan": "pcs", "stok": 0, "stok_minimum": 8,  "deskripsi": "Inner hijab rajut nyaman tidak menekan telinga"},
        {"kode_barang": "LAI001", "nama_produk": "Gantungan Kunci Lookatstore", "kategori": kategoris["Lainnya"],           "satuan": "pcs", "stok": 0, "stok_minimum": 5,  "deskripsi": "Merchandise gantungan kunci akrilik"},
    ]
    created_count = 0
    products = []
    for p_info in products_data:
        obj, created = Barang.objects.get_or_create(
            kode_barang=p_info["kode_barang"],
            defaults={k: v for k, v in p_info.items() if k != "kode_barang"},
        )
        products.append(obj)
        if created:
            created_count += 1
    if created_count:
        print(f"[OK]   {created_count} barang dibuat.")
    else:
        print("[SKIP] Semua barang sudah ada.")
    return products, created_count


def seed_transactions(products, suppliers, admin_user):
    """Hanya dibuat jika belum ada transaksi sama sekali."""
    if BarangMasuk.objects.exists() or BarangKeluar.objects.exists():
        print("[SKIP] Data transaksi sudah ada — tidak dibuat ulang.")
        return

    print("[OK]   Membuat data transaksi 30 hari terakhir...")
    start_date = date.today() - timedelta(days=29)

    # Intake awal
    for p in products:
        intake_qty = random.randint(40, 80)
        bm = BarangMasuk(
            tanggal=start_date,
            barang=p,
            jumlah=intake_qty,
            supplier=random.choice(suppliers),
            keterangan="Stok awal pembukaan periode",
        )
        bm.save(user=admin_user)

    # Aktivitas harian
    for day_offset in range(1, 30):
        current_date = start_date + timedelta(days=day_offset)

        num_sales = random.randint(2, 5)
        sales_prods = random.sample(products, num_sales)
        for p in sales_prods:
            p.refresh_from_db()
            if p.stok > 10:
                qty_sold = random.randint(2, 6)
                bk = BarangKeluar(
                    tanggal=current_date,
                    barang=p,
                    jumlah=qty_sold,
                    keterangan="Penjualan",
                )
                bk.save(user=admin_user)

        if day_offset % 4 == 0:
            restock_prods = random.sample(products, 2)
            for p in restock_prods:
                qty_restock = random.randint(15, 25)
                bm = BarangMasuk(
                    tanggal=current_date,
                    barang=p,
                    jumlah=qty_restock,
                    supplier=random.choice(suppliers),
                    keterangan="Restock bulanan terjadwal",
                )
                bm.save(user=admin_user)

    print("[OK]   Data transaksi selesai dibuat.")


def run():
    print("=" * 50)
    print("  LookAtStore — Initial Data Seeder")
    print("  (Data yang sudah ada tidak akan ditimpa)")
    print("=" * 50)

    admin_user = seed_superuser()
    # Jika admin sudah ada, ambil dari DB untuk dipakai di transaksi
    if admin_user is None:
        admin_user = User.objects.filter(is_superuser=True).first()

    kategoris = seed_kategori()
    suppliers = seed_supplier()
    products, new_products_count = seed_barang(kategoris)

    # Seed transaksi hanya jika ada produk baru ATAU belum ada transaksi sama sekali
    if new_products_count > 0 or not BarangMasuk.objects.exists():
        seed_transactions(products, suppliers, admin_user)
    else:
        print("[SKIP] Data transaksi sudah ada — tidak dibuat ulang.")

    print("=" * 50)
    print("  Seeding selesai!")
    print("=" * 50)


if __name__ == "__main__":
    run()
