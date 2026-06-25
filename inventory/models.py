from django.db import models

class Kategori(models.Model):
    nama = models.CharField(max_length=25, unique=True, verbose_name="Nama Kategori")
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Deskripsi")

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Daftar Kategori"
        ordering = ['nama']


class Supplier(models.Model):
    nama = models.CharField(max_length=25, unique=True, verbose_name="Nama Supplier")
    kontak = models.CharField(max_length=20, blank=True, null=True, verbose_name="Kontak (Telepon/WA)")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    alamat = models.TextField(blank=True, null=True, verbose_name="Alamat")

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Daftar Supplier"
        ordering = ['nama']


class Barang(models.Model):
    SATUAN_CHOICES = [
        ('pcs', 'Pcs'),
        ('lusin', 'Lusin'),
        ('kodi', 'Kodi'),
    ]

    kode_barang = models.CharField(max_length=50, unique=True, verbose_name="Kode Barang")
    nama_produk = models.CharField(max_length=50, verbose_name="Nama Produk")
    kategori = models.ForeignKey(Kategori, on_delete=models.PROTECT, related_name='barang_list', null=True, verbose_name="Kategori")
    satuan = models.CharField(max_length=20, choices=SATUAN_CHOICES, default='pcs', verbose_name="Satuan")
    stok = models.IntegerField(default=0, verbose_name="Stok")
    stok_minimum = models.IntegerField(default=0, verbose_name="Stok Minimum")
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.kode_barang} - {self.nama_produk}"

    class Meta:
        verbose_name = "Barang"
        verbose_name_plural = "Daftar Barang"
        ordering = ['nama_produk']

