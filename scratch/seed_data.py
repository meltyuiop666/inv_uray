import os
import sys
import django
import random
from datetime import date, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lookatstore_inventory.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Barang, Kategori, Supplier
from transactions.models import BarangMasuk, BarangKeluar, StockLedger

User = get_user_model()

def seed():
    print("Clearing old transactional and product data...")
    BarangKeluar.objects.all().delete()
    BarangMasuk.objects.all().delete()
    StockLedger.objects.all().delete()
    Barang.objects.all().delete()
    Supplier.objects.all().delete()
    
    # Ensure admin user exists
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@lookatstore.id', 'adminpassword123')
        print("Created superuser 'admin'")
    else:
        print("Superuser 'admin' already exists.")
    
    # Seed Kategori if not exist
    kategori_names = ['Dress', 'Oneset', 'Hijab', 'Perlengkapan Hijab', 'Lainnya']
    kategoris = {}
    for name in kategori_names:
        cat, created = Kategori.objects.get_or_create(nama=name)
        kategoris[name] = cat
    print("Categories checked.")
    
    # Seed Suppliers
    suppliers = []
    supplier_data = [
        {"nama": "Supplier Hijab Pontianak", "kontak": "08123456789", "email": "pontianak@hijab.com", "alamat": "Jl. Ahmad Yani No. 12, Pontianak"},
        {"nama": "CV Dress Indah Bandung", "kontak": "08234567890", "email": "bandung@dress.com", "alamat": "Kawasan Industri Batununggal, Bandung"},
        {"nama": "Grosir Oneset Jakarta", "kontak": "08345678901", "email": "jakarta@oneset.com", "alamat": "Tanah Abang Blok A, Jakarta"},
    ]
    for s_info in supplier_data:
        sup = Supplier.objects.create(**s_info)
        suppliers.append(sup)
    print("Suppliers created.")
    
    # Seed Barang (Products)
    products_data = [
        {"kode_barang": "DRS001", "nama_produk": "Dress Silk Jasmine", "kategori": kategoris["Dress"], "satuan": "pcs", "stok": 0, "stok_minimum": 5, "deskripsi": "Dress sutra premium motif bunga melati"},
        {"kode_barang": "DRS002", "nama_produk": "Gamis Rayon Plain", "kategori": kategoris["Dress"], "satuan": "pcs", "stok": 0, "stok_minimum": 10, "deskripsi": "Gamis bahan rayon adem untuk harian"},
        {"kode_barang": "HJB001", "nama_produk": "Pashmina Ceruty Baby Doll", "kategori": kategoris["Hijab"], "satuan": "pcs", "stok": 0, "stok_minimum": 15, "deskripsi": "Hijab pashmina ceruty tekstur pasir premium"},
        {"kode_barang": "HJB002", "nama_produk": "Hijab Segiempat Voal Bella", "kategori": kategoris["Hijab"], "satuan": "pcs", "stok": 0, "stok_minimum": 20, "deskripsi": "Hijab voal segiempat bestseller harian"},
        {"kode_barang": "ONS001", "nama_produk": "Oneset Linen Cargo", "kategori": kategoris["Oneset"], "satuan": "pcs", "stok": 0, "stok_minimum": 4, "deskripsi": "Satu set kemeja dan celana kargo bahan linen"},
        {"kode_barang": "ONS002", "nama_produk": "Oneset Knit Ribbed", "kategori": kategoris["Oneset"], "satuan": "pcs", "stok": 0, "stok_minimum": 5, "deskripsi": "Setelan rajut rib hangat dan stylish"},
        {"kode_barang": "PLK001", "nama_produk": "Ciput Rajut Anti Pusing", "kategori": kategoris["Perlengkapan Hijab"], "satuan": "pcs", "stok": 0, "stok_minimum": 8, "deskripsi": "Inner hijab rajut nyaman tidak menekan telinga"},
        {"kode_barang": "LAI001", "nama_produk": "Gantungan Kunci Lookatstore", "kategori": kategoris["Lainnya"], "satuan": "pcs", "stok": 0, "stok_minimum": 5, "deskripsi": "Merchandise gantungan kunci akrilik"},
    ]
    
    products = []
    for p_info in products_data:
        p = Barang.objects.create(**p_info)
        products.append(p)
    print("Products created.")
    
    # Initial date 30 days ago
    start_date = date.today() - timedelta(days=29)
    
    # Day 1: Large stock intake
    print("Seeding initial stock intakes...")
    for p in products:
        intake_qty = random.randint(40, 80)
        bm = BarangMasuk(
            tanggal=start_date,
            barang=p,
            jumlah=intake_qty,
            supplier=random.choice(suppliers),
            keterangan="Stok awal pembukaan periode"
        )
        bm.save(user=admin_user)
        
    # Day 2 to 30: Daily activity
    print("Seeding daily transactions...")
    for day_offset in range(1, 30):
        current_date = start_date + timedelta(days=day_offset)
        
        # Check a few random products for sales on this day
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
                    keterangan="Penjualan"
                )
                bk.save(user=admin_user)
                
        # Occasional restock
        if day_offset % 4 == 0:
            restock_prods = random.sample(products, 2)
            for p in restock_prods:
                qty_restock = random.randint(15, 25)
                bm = BarangMasuk(
                    tanggal=current_date,
                    barang=p,
                    jumlah=qty_restock,
                    supplier=random.choice(suppliers),
                    keterangan="Restock bulanan terjadwal"
                )
                bm.save(user=admin_user)
                
    # Refresh all products to display updated stocks
    for p in products:
        p.refresh_from_db()
        print(f"Product {p.kode_barang} final stock: {p.stok}")
        
    print("Data seeding completed successfully!")

if __name__ == "__main__":
    seed()
