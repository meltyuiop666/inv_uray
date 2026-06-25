from django.contrib import admin
from .models import BarangMasuk, BarangKeluar, StockLedger

@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'barang', 'user', 'stok_awal', 'stok_akhir', 'perubahan', 'tipe_transaksi', 'referensi_id')
    search_fields = ('barang__nama_produk', 'barang__kode_barang', 'user__username', 'keterangan')
    list_filter = ('tanggal', 'tipe_transaksi')
    date_hierarchy = 'tanggal'

@admin.register(BarangMasuk)
class BarangMasukAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'barang', 'jumlah', 'supplier', 'created_at')
    search_fields = ('barang__nama_produk', 'barang__kode_barang', 'supplier__nama')
    list_filter = ('tanggal', 'barang__kategori')
    date_hierarchy = 'tanggal'

@admin.register(BarangKeluar)
class BarangKeluarAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'barang', 'jumlah', 'keterangan', 'created_at')
    search_fields = ('barang__nama_produk', 'barang__kode_barang', 'keterangan')
    list_filter = ('tanggal', 'barang__kategori', 'keterangan')
    date_hierarchy = 'tanggal'

