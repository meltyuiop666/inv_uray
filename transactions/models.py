from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from inventory.models import Barang, Supplier

class StockLedger(models.Model):
    TIPE_CHOICES = (
        ('MASUK', 'Barang Masuk'),
        ('KELUAR', 'Barang Keluar'),
        ('KOREKSI', 'Koreksi Stok'),
        ('HAPUS_MASUK', 'Hapus Barang Masuk'),
        ('HAPUS_KELUAR', 'Hapus Barang Keluar'),
    )
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='ledger', verbose_name="Barang")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Pengguna")
    tanggal = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal/Waktu")
    stok_awal = models.IntegerField(verbose_name="Stok Awal")
    stok_akhir = models.IntegerField(verbose_name="Stok Akhir")
    perubahan = models.IntegerField(verbose_name="Perubahan")
    tipe_transaksi = models.CharField(max_length=20, choices=TIPE_CHOICES, verbose_name="Tipe Transaksi")
    referensi_id = models.IntegerField(null=True, blank=True, verbose_name="ID Referensi")
    keterangan = models.TextField(verbose_name="Keterangan")

    def __str__(self):
        return f"{self.barang.nama_produk} ({self.perubahan:+d}) pada {self.tanggal.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Stock Ledger"
        verbose_name_plural = "Stock Ledger"
        ordering = ['-tanggal']


class BarangMasuk(models.Model):
    tanggal = models.DateField(verbose_name="Tanggal Masuk")
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='barang_masuk', verbose_name="Barang")
    jumlah = models.PositiveIntegerField(verbose_name="Jumlah")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='barang_masuk', null=True, verbose_name="Supplier")
    keterangan = models.TextField(blank=True, null=True, verbose_name="Keterangan")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, user=None, **kwargs):
        if not self.pk:
            stok_awal = self.barang.stok
            self.barang.stok += self.jumlah
            self.barang.save()
            stok_akhir = self.barang.stok
            super().save(*args, **kwargs)
            
            # Log ledger
            StockLedger.objects.create(
                barang=self.barang,
                user=user,
                stok_awal=stok_awal,
                stok_akhir=stok_akhir,
                perubahan=self.jumlah,
                tipe_transaksi='MASUK',
                referensi_id=self.id,
                keterangan=f"Penerimaan barang masuk dari supplier {self.supplier.nama if self.supplier else '-'}"
            )
        else:
            orig = BarangMasuk.objects.get(pk=self.pk)
            stok_awal = self.barang.stok
            if orig.barang == self.barang:
                self.barang.stok += (self.jumlah - orig.jumlah)
                self.barang.save()
                stok_akhir = self.barang.stok
                super().save(*args, **kwargs)
                
                # Log ledger
                StockLedger.objects.create(
                    barang=self.barang,
                    user=user,
                    stok_awal=stok_awal,
                    stok_akhir=stok_akhir,
                    perubahan=self.jumlah - orig.jumlah,
                    tipe_transaksi='KOREKSI',
                    referensi_id=self.id,
                    keterangan=f"Koreksi jumlah barang masuk (dari {orig.jumlah} ke {self.jumlah})"
                )
            else:
                orig_barang = orig.barang
                orig_stok_awal = orig_barang.stok
                orig_barang.stok -= orig.jumlah
                orig_barang.save()
                orig_stok_akhir = orig_barang.stok
                
                # Log ledger for revert
                StockLedger.objects.create(
                    barang=orig_barang,
                    user=user,
                    stok_awal=orig_stok_awal,
                    stok_akhir=orig_stok_akhir,
                    perubahan=-orig.jumlah,
                    tipe_transaksi='KOREKSI',
                    referensi_id=self.id,
                    keterangan=f"Koreksi transaksi masuk: pemindahan produk ke {self.barang.nama_produk}"
                )
                
                stok_awal = self.barang.stok
                self.barang.stok += self.jumlah
                self.barang.save()
                stok_akhir = self.barang.stok
                super().save(*args, **kwargs)
                
                # Log ledger for new
                StockLedger.objects.create(
                    barang=self.barang,
                    user=user,
                    stok_awal=stok_awal,
                    stok_akhir=stok_akhir,
                    perubahan=self.jumlah,
                    tipe_transaksi='KOREKSI',
                    referensi_id=self.id,
                    keterangan=f"Koreksi transaksi masuk: produk dipindahkan dari {orig_barang.nama_produk}"
                )

    def delete(self, *args, user=None, **kwargs):
        stok_awal = self.barang.stok
        self.barang.stok -= self.jumlah
        self.barang.save()
        stok_akhir = self.barang.stok
        
        # Log ledger
        StockLedger.objects.create(
            barang=self.barang,
            user=user,
            stok_awal=stok_awal,
            stok_akhir=stok_akhir,
            perubahan=-self.jumlah,
            tipe_transaksi='HAPUS_MASUK',
            referensi_id=self.id,
            keterangan=f"Pembatalan/penghapusan transaksi barang masuk"
        )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Masuk: {self.barang.nama_produk} ({self.jumlah})"

    class Meta:
        verbose_name = "Barang Masuk"
        verbose_name_plural = "Barang Masuk"


class BarangKeluar(models.Model):
    tanggal = models.DateField(verbose_name="Tanggal Keluar")
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='barang_keluar', verbose_name="Barang")
    jumlah = models.PositiveIntegerField(verbose_name="Jumlah")
    keterangan = models.CharField(
        max_length=50,
        choices=[('Penjualan', 'Penjualan'), ('Lainnya', 'Lainnya')],
        default='Penjualan',
        verbose_name="Alasan Keluar"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, user=None, **kwargs):
        if not self.pk:
            stok_available = self.barang.stok
            change = self.jumlah
        else:
            orig = BarangKeluar.objects.get(pk=self.pk)
            if orig.barang == self.barang:
                stok_available = self.barang.stok + orig.jumlah
                change = self.jumlah
            else:
                stok_available = self.barang.stok
                change = self.jumlah

        # Enforce no negative stock
        if stok_available < change:
            raise ValidationError(f"Stok tidak mencukupi. Stok tersedia: {stok_available}, diajukan: {change}")

        if not self.pk:
            stok_awal = self.barang.stok
            self.barang.stok -= self.jumlah
            self.barang.save()
            stok_akhir = self.barang.stok
            super().save(*args, **kwargs)
            
            # Log ledger
            StockLedger.objects.create(
                barang=self.barang,
                user=user,
                stok_awal=stok_awal,
                stok_akhir=stok_akhir,
                perubahan=-self.jumlah,
                tipe_transaksi='KELUAR',
                referensi_id=self.id,
                keterangan=f"Pengeluaran barang keluar (Alasan: {self.keterangan})"
            )
        else:
            orig = BarangKeluar.objects.get(pk=self.pk)
            stok_awal = self.barang.stok
            if orig.barang == self.barang:
                self.barang.stok -= (self.jumlah - orig.jumlah)
                self.barang.save()
                stok_akhir = self.barang.stok
                super().save(*args, **kwargs)
                
                # Log ledger
                StockLedger.objects.create(
                    barang=self.barang,
                    user=user,
                    stok_awal=stok_awal,
                    stok_akhir=stok_akhir,
                    perubahan=-(self.jumlah - orig.jumlah),
                    tipe_transaksi='KOREKSI',
                    referensi_id=self.id,
                    keterangan=f"Koreksi jumlah barang keluar (dari {orig.jumlah} ke {self.jumlah})"
                )
            else:
                orig_barang = orig.barang
                orig_stok_awal = orig_barang.stok
                orig_barang.stok += orig.jumlah
                orig_barang.save()
                orig_stok_akhir = orig_barang.stok
                
                # Log ledger for revert
                StockLedger.objects.create(
                    barang=orig_barang,
                    user=user,
                    stok_awal=orig_stok_awal,
                    stok_akhir=orig_stok_akhir,
                    perubahan=orig.jumlah,
                    tipe_transaksi='KOREKSI',
                    referensi_id=self.id,
                    keterangan=f"Koreksi transaksi keluar: pemindahan produk ke {self.barang.nama_produk}"
                )
                
                stok_awal = self.barang.stok
                self.barang.stok -= self.jumlah
                self.barang.save()
                stok_akhir = self.barang.stok
                super().save(*args, **kwargs)
                
                # Log ledger for new
                StockLedger.objects.create(
                    barang=self.barang,
                    user=user,
                    stok_awal=stok_awal,
                    stok_akhir=stok_akhir,
                    perubahan=-self.jumlah,
                    tipe_transaksi='KOREKSI',
                    referensi_id=self.id,
                    keterangan=f"Koreksi transaksi keluar: produk dipindahkan dari {orig_barang.nama_produk}"
                )

    def delete(self, *args, user=None, **kwargs):
        stok_awal = self.barang.stok
        self.barang.stok += self.jumlah
        self.barang.save()
        stok_akhir = self.barang.stok
        
        # Log ledger
        StockLedger.objects.create(
            barang=self.barang,
            user=user,
            stok_awal=stok_awal,
            stok_akhir=stok_akhir,
            perubahan=self.jumlah,
            tipe_transaksi='HAPUS_KELUAR',
            referensi_id=self.id,
            keterangan=f"Pembatalan/penghapusan transaksi barang keluar"
        )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Keluar: {self.barang.nama_produk} ({self.jumlah})"

    class Meta:
        verbose_name = "Barang Keluar"
        verbose_name_plural = "Barang Keluar"

