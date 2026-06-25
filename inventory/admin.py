from django.contrib import admin
from .models import Barang, Kategori, Supplier

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('nama', 'deskripsi')
    search_fields = ('nama', 'deskripsi')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kontak', 'email', 'alamat')
    search_fields = ('nama', 'kontak', 'email')

@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('kode_barang', 'nama_produk', 'kategori', 'satuan', 'stok', 'stok_minimum')
    search_fields = ('kode_barang', 'nama_produk', 'kategori__nama')
    list_filter = ('kategori', 'satuan')
    ordering = ('nama_produk',)

