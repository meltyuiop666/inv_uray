from django import forms
from .models import Barang, Kategori, Supplier

class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = ['nama', 'deskripsi']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'placeholder': 'Contoh: Hijab'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'rows': '3',
                'placeholder': 'Deskripsi kategori...'
            }),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['nama', 'kontak', 'email', 'alamat']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'placeholder': 'Contoh: CV Hijab Berkah'
            }),
            'kontak': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'placeholder': 'Contoh: 081234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'placeholder': 'Contoh: supplier@email.com'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'rows': '3',
                'placeholder': 'Alamat lengkap supplier...'
            }),
        }

class BarangForm(forms.ModelForm):
    kategori = forms.ModelChoiceField(
        queryset=Kategori.objects.all(),
        empty_label="Pilih Kategori",
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm'
        })
    )

    class Meta:
        model = Barang
        fields = ['kode_barang', 'nama_produk', 'kategori', 'satuan', 'stok_minimum', 'deskripsi']
        widgets = {
            'kode_barang': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'placeholder': 'Contoh: BRG-001'
            }),
            'nama_produk': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'placeholder': 'Contoh: Dress Silk Premium'
            }),
            'satuan': forms.Select(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm'
            }),
            'stok_minimum': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'min': '0'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'rows': '3',
                'placeholder': 'Keterangan tambahan barang...'
            }),
        }

