from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
import json
from .models import BarangMasuk, BarangKeluar, StockLedger
from .forms import BarangMasukForm, BarangKeluarForm

# --- BARANG MASUK VIEWS ---

@login_required
def masuk_list(request):
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    items = BarangMasuk.objects.select_related('barang', 'supplier').order_by('-tanggal', '-created_at')
    
    if query:
        items = items.filter(Q(barang__nama_produk__icontains=query) | Q(supplier__nama__icontains=query))
    if start_date:
        items = items.filter(tanggal__gte=start_date)
    if end_date:
        items = items.filter(tanggal__lte=end_date)
        
    context = {
        'items': items,
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'transactions/masuk_table_fragment.html', context)
        
    return render(request, 'transactions/masuk_list.html', context)

@login_required
def masuk_create(request):
    if request.method == 'POST':
        form = BarangMasukForm(request.POST)
        if form.is_valid():
            try:
                bm = form.save(commit=False)
                bm.save(user=request.user)
                form.save_m2m()
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({
                    'masukListChanged': None,
                    'showToast': {
                        'message': 'Transaksi barang masuk berhasil dicatat!',
                        'type': 'success'
                    }
                })
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = BarangMasukForm()
        
    return render(request, 'transactions/masuk_form_modal.html', {
        'form': form,
        'title': 'Tambah Barang Masuk'
    })

@login_required
def masuk_update(request, pk):
    bm = get_object_or_404(BarangMasuk, pk=pk)
    if request.method == 'POST':
        form = BarangMasukForm(request.POST, instance=bm)
        if form.is_valid():
            try:
                bm = form.save(commit=False)
                bm.save(user=request.user)
                form.save_m2m()
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({
                    'masukListChanged': None,
                    'showToast': {
                        'message': f"Transaksi masuk untuk '{bm.barang.nama_produk}' berhasil diubah!",
                        'type': 'success'
                    }
                })
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = BarangMasukForm(instance=bm)
        
    return render(request, 'transactions/masuk_form_modal.html', {
        'form': form,
        'transaction': bm,
        'title': 'Ubah Barang Masuk'
    })

@login_required
def masuk_delete(request, pk):
    bm = get_object_or_404(BarangMasuk, pk=pk)
    if request.method == 'POST':
        nama_produk = bm.barang.nama_produk
        bm.delete(user=request.user)
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'masukListChanged': None,
            'showToast': {
                'message': f"Transaksi masuk untuk '{nama_produk}' berhasil dihapus!",
                'type': 'success'
            }
        })
        return response
        
    return render(request, 'transactions/masuk_delete_confirm_modal.html', {'transaction': bm})


# --- BARANG KELUAR VIEWS ---

@login_required
def keluar_list(request):
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    items = BarangKeluar.objects.select_related('barang').order_by('-tanggal', '-created_at')
    
    if query:
        items = items.filter(Q(barang__nama_produk__icontains=query) | Q(keterangan__icontains=query))
    if start_date:
        items = items.filter(tanggal__gte=start_date)
    if end_date:
        items = items.filter(tanggal__lte=end_date)
        
    context = {
        'items': items,
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'transactions/keluar_table_fragment.html', context)
        
    return render(request, 'transactions/keluar_list.html', context)

@login_required
def keluar_create(request):
    if request.method == 'POST':
        form = BarangKeluarForm(request.POST)
        if form.is_valid():
            try:
                bk = form.save(commit=False)
                bk.save(user=request.user)
                form.save_m2m()
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({
                    'keluarListChanged': None,
                    'showToast': {
                        'message': 'Transaksi barang keluar berhasil dicatat!',
                        'type': 'success'
                    }
                })
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = BarangKeluarForm()
        
    return render(request, 'transactions/keluar_form_modal.html', {
        'form': form,
        'title': 'Tambah Barang Keluar'
    })

@login_required
def keluar_update(request, pk):
    bk = get_object_or_404(BarangKeluar, pk=pk)
    if request.method == 'POST':
        form = BarangKeluarForm(request.POST, instance=bk)
        if form.is_valid():
            try:
                bk = form.save(commit=False)
                bk.save(user=request.user)
                form.save_m2m()
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({
                    'keluarListChanged': None,
                    'showToast': {
                        'message': f"Transaksi keluar untuk '{bk.barang.nama_produk}' berhasil diubah!",
                        'type': 'success'
                    }
                })
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = BarangKeluarForm(instance=bk)
        
    return render(request, 'transactions/keluar_form_modal.html', {
        'form': form,
        'transaction': bk,
        'title': 'Ubah Barang Keluar'
    })

@login_required
def keluar_delete(request, pk):
    bk = get_object_or_404(BarangKeluar, pk=pk)
    if request.method == 'POST':
        nama_produk = bk.barang.nama_produk
        bk.delete(user=request.user)
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'keluarListChanged': None,
            'showToast': {
                'message': f"Transaksi keluar untuk '{nama_produk}' berhasil dihapus!",
                'type': 'success'
            }
        })
        return response
        
    return render(request, 'transactions/keluar_delete_confirm_modal.html', {'transaction': bk})


# --- AUDIT STOCK LEDGER VIEW ---

@login_required
def ledger_list(request):
    query = request.GET.get('q', '')
    items = StockLedger.objects.select_related('barang', 'user').all()
    if query:
        items = items.filter(Q(barang__nama_produk__icontains=query) | Q(keterangan__icontains=query))
    context = {'items': items, 'query': query}
    return render(request, 'transactions/ledger.html', context)

