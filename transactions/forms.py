from django import forms
from .models import BarangMasuk, BarangKeluar
from inventory.models import Barang, Supplier

class BarangMasukForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        empty_label="Pilih Supplier",
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm'
        })
    )

    class Meta:
        model = BarangMasuk
        fields = ['tanggal', 'barang', 'jumlah', 'supplier', 'keterangan']
        widgets = {
            'tanggal': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                }
            ),
            'barang': forms.Select(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
            }),
            'jumlah': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'min': '1'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'rows': '2',
                'placeholder': 'Catatan penerimaan barang...'
            }),
        }



class BarangKeluarForm(forms.ModelForm):
    class Meta:
        model = BarangKeluar
        fields = ['tanggal', 'barang', 'jumlah', 'keterangan']
        widgets = {
            'tanggal': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                }
            ),
            'barang': forms.Select(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
            }),
            'jumlah': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
                'min': '1'
            }),
            'keterangan': forms.Select(attrs={
                'class': 'block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:bg-white focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all text-sm',
            }),
        }
