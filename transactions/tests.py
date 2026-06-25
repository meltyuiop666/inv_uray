from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import date
from inventory.models import Barang, Kategori, Supplier
from transactions.models import BarangMasuk, BarangKeluar, StockLedger

User = get_user_model()

class InventoryTransactionTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username="admin_test", password="password123")

        # Create test categories
        self.kategori_hijab = Kategori.objects.create(
            nama="Hijab",
            deskripsi="Semua jenis hijab"
        )
        self.kategori_dress = Kategori.objects.create(
            nama="Dress",
            deskripsi="Semua jenis dress/gamis"
        )

        # Create test suppliers
        self.supplier = Supplier.objects.create(
            nama="Supplier Hijab Pontianak",
            kontak="081234567890",
            email="supplier@mail.com",
            alamat="Pontianak"
        )

        # Create initial test products
        self.barang1 = Barang.objects.create(
            kode_barang="BRG001",
            nama_produk="Hijab Pashmina",
            kategori=self.kategori_hijab,
            satuan="pcs",
            stok=10,
            stok_minimum=5
        )
        self.barang2 = Barang.objects.create(
            kode_barang="BRG002",
            nama_produk="Dress Silk",
            kategori=self.kategori_dress,
            satuan="pcs",
            stok=5,
            stok_minimum=2
        )

    def test_barang_creation(self):
        """Test basic product model creation."""
        self.assertEqual(self.barang1.kode_barang, "BRG001")
        self.assertEqual(self.barang1.stok, 10)
        self.assertEqual(self.barang1.kategori.nama, "Hijab")

    def test_barang_masuk_adds_stock(self):
        """Test that registering BarangMasuk increases the product stock."""
        bm = BarangMasuk(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=15,
            supplier=self.supplier
        )
        bm.save(user=self.user)
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 25)

    def test_barang_masuk_delete_reverts_stock(self):
        """Test that deleting a BarangMasuk transaction correctly decreases/reverts the stock."""
        bm = BarangMasuk(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=15,
            supplier=self.supplier
        )
        bm.save(user=self.user)
        bm.delete(user=self.user)
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 10)

    def test_barang_masuk_update_adjusts_stock(self):
        """Test that updating the amount in BarangMasuk adjusts the stock correctly."""
        bm = BarangMasuk(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=15,
            supplier=self.supplier
        )
        bm.save(user=self.user)
        # Update quantity from 15 to 20
        bm.jumlah = 20
        bm.save(user=self.user)
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 30)

    def test_barang_masuk_change_product_adjusts_stock(self):
        """Test that changing the product of BarangMasuk updates both products' stocks correctly."""
        bm = BarangMasuk(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=15,
            supplier=self.supplier
        )
        bm.save(user=self.user)
        # Swapping product to barang2
        bm.barang = self.barang2
        bm.save(user=self.user)
        
        self.barang1.refresh_from_db()
        self.barang2.refresh_from_db()
        
        self.assertEqual(self.barang1.stok, 10)  # Reverted back to initial 10
        self.assertEqual(self.barang2.stok, 20)  # Initial 5 + 15

    def test_barang_keluar_reduces_stock(self):
        """Test that registering BarangKeluar reduces stock correctly."""
        bk = BarangKeluar(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=4,
            keterangan="Penjualan"
        )
        bk.save(user=self.user)
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 6)

    def test_barang_keluar_insufficient_stock_raises_validation_error(self):
        """Test that validation prevents stock from going negative."""
        bk = BarangKeluar(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=15,  # initial is 10, so 15 is too much
            keterangan="Penjualan"
        )
        with self.assertRaises(ValidationError):
            bk.save(user=self.user)
        # Verify stock remains unchanged
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 10)

    def test_barang_keluar_delete_reverts_stock(self):
        """Test that deleting a BarangKeluar transaction restores the stock."""
        bk = BarangKeluar(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=4,
            keterangan="Penjualan"
        )
        bk.save(user=self.user)
        bk.delete(user=self.user)
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 10)

    def test_barang_keluar_update_adjusts_stock(self):
        """Test that updating the amount in BarangKeluar adjusts the stock correctly."""
        bk = BarangKeluar(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=4,
            keterangan="Penjualan"
        )
        bk.save(user=self.user)
        # Change quantity from 4 to 6
        bk.jumlah = 6
        bk.save(user=self.user)
        self.barang1.refresh_from_db()
        self.assertEqual(self.barang1.stok, 4)

    def test_barang_keluar_change_product_adjusts_stock(self):
        """Test that changing the product of BarangKeluar updates both stocks correctly."""
        bk = BarangKeluar(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=4,
            keterangan="Penjualan"
        )
        bk.save(user=self.user)
        # Swap product from barang1 (initial 10) to barang2 (initial 5)
        bk.barang = self.barang2
        bk.save(user=self.user)
        
        self.barang1.refresh_from_db()
        self.barang2.refresh_from_db()
        
        self.assertEqual(self.barang1.stok, 10)  # Reverted back to initial 10
        self.assertEqual(self.barang2.stok, 1)   # Initial 5 - 4

    def test_stock_ledger_logging_details(self):
        """Test that saving and deleting transactions logs precise StockLedger entries."""
        # 1. Barang Masuk
        bm = BarangMasuk(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=10,
            supplier=self.supplier
        )
        bm.save(user=self.user)
        
        ledger_entries = StockLedger.objects.filter(barang=self.barang1, referensi_id=bm.id, tipe_transaksi='MASUK')
        self.assertEqual(ledger_entries.count(), 1)
        ledger = ledger_entries.first()
        self.assertEqual(ledger.stok_awal, 10)
        self.assertEqual(ledger.stok_akhir, 20)
        self.assertEqual(ledger.perubahan, 10)
        self.assertEqual(ledger.user, self.user)

        # 2. Barang Keluar
        bk = BarangKeluar(
            tanggal=date.today(),
            barang=self.barang1,
            jumlah=5,
            keterangan="Penjualan"
        )
        bk.save(user=self.user)
        
        ledger_entries = StockLedger.objects.filter(barang=self.barang1, referensi_id=bk.id, tipe_transaksi='KELUAR')
        self.assertEqual(ledger_entries.count(), 1)
        ledger = ledger_entries.first()
        self.assertEqual(ledger.stok_awal, 20)
        self.assertEqual(ledger.stok_akhir, 15)
        self.assertEqual(ledger.perubahan, -5)
        self.assertEqual(ledger.user, self.user)

        # 3. Delete Barang Masuk
        bm.delete(user=self.user)
        ledger_entries = StockLedger.objects.filter(barang=self.barang1, tipe_transaksi='HAPUS_MASUK')
        self.assertEqual(ledger_entries.count(), 1)
        ledger = ledger_entries.first()
        self.assertEqual(ledger.stok_awal, 15)
        self.assertEqual(ledger.stok_akhir, 5)
        self.assertEqual(ledger.perubahan, -10)
        self.assertEqual(ledger.user, self.user)
