from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Sum, F, Q
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
import json
from .models import Barang, Kategori, Supplier
from .forms import BarangForm, KategoriForm, SupplierForm
from transactions.models import BarangMasuk, BarangKeluar

@login_required
def dashboard(request):
    total_items = Barang.objects.count()
    
    # Sum of items received today
    masuk_today = BarangMasuk.objects.filter(tanggal=date.today()).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    # Sum of items released today
    keluar_today = BarangKeluar.objects.filter(tanggal=date.today()).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    
    # Items with critical stock (stok <= stok_minimum)
    critical_count = Barang.objects.filter(stok__lte=F('stok_minimum')).count()
    critical_items = Barang.objects.filter(stok__lte=F('stok_minimum')).order_by('stok')[:5]
    
    # Recent activity log
    masuk_recent = BarangMasuk.objects.select_related('barang').order_by('-created_at')[:5]
    keluar_recent = BarangKeluar.objects.select_related('barang').order_by('-created_at')[:5]
    
    activities = []
    for m in masuk_recent:
        activities.append({
            'type': 'masuk',
            'tanggal': m.tanggal,
            'barang': m.barang.nama_produk,
            'kode': m.barang.kode_barang,
            'jumlah': m.jumlah,
            'keterangan': f"Supplier: {m.supplier.nama if m.supplier else '-'}",
            'created_at': m.created_at
        })
    for k in keluar_recent:
        activities.append({
            'type': 'keluar',
            'tanggal': k.tanggal,
            'barang': k.barang.nama_produk,
            'kode': k.barang.kode_barang,
            'jumlah': k.jumlah,
            'keterangan': f"Alasan: {k.keterangan}",
            'created_at': k.created_at
        })
        
    activities = sorted(activities, key=lambda x: x['created_at'], reverse=True)[:5]
    
    # General low stock warning items
    low_stock_list = Barang.objects.filter(stok__lte=F('stok_minimum')).order_by('stok')
    
    # --- CHART TREND CALCULATION ---
    # Get last 30 days
    today = date.today()
    date_list = [today - timedelta(days=i) for i in range(29, -1, -1)]
    date_label_list = [d.strftime('%d %b') for d in date_list]
    
    categories = list(Kategori.objects.all())
    category_data = {cat.nama: [0]*30 for cat in categories}
    
    for cat in categories:
        products = list(Barang.objects.filter(kategori=cat))
        for i, d in enumerate(date_list):
            total_stock_at_d = 0
            for prod in products:
                current_stok = prod.stok
                inc_sum = BarangMasuk.objects.filter(barang=prod, tanggal__gt=d).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
                out_sum = BarangKeluar.objects.filter(barang=prod, tanggal__gt=d).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
                prod_stock_at_d = current_stok - inc_sum + out_sum
                total_stock_at_d += max(0, prod_stock_at_d)
            category_data[cat.nama][i] = total_stock_at_d

    colors = [
        {'border': '#f43f5e', 'bg': 'rgba(244, 63, 94, 0.05)'},  # Rose
        {'border': '#0ea5e9', 'bg': 'rgba(14, 165, 233, 0.05)'},  # Sky
        {'border': '#8b5cf6', 'bg': 'rgba(139, 92, 246, 0.05)'},  # Violet
        {'border': '#10b981', 'bg': 'rgba(16, 185, 129, 0.05)'},  # Emerald
        {'border': '#f59e0b', 'bg': 'rgba(245, 158, 11, 0.05)'},   # Amber
        {'border': '#64748b', 'bg': 'rgba(100, 116, 139, 0.05)'},  # Slate
    ]

    chart_datasets = []
    for idx, (cat_name, data_points) in enumerate(category_data.items()):
        color = colors[idx % len(colors)]
        chart_datasets.append({
            'label': cat_name,
            'data': data_points,
            'borderColor': color['border'],
            'backgroundColor': color['bg'],
            'tension': 0.3,
            'fill': True,
            'borderWidth': 2,
            'pointRadius': 1,
            'pointHoverRadius': 5,
        })

    chart_json = json.dumps({
        'labels': date_label_list,
        'datasets': chart_datasets
    })
    
    context = {
        'total_items': total_items,
        'masuk_today': masuk_today,
        'keluar_today': keluar_today,
        'critical_count': critical_count,
        'critical_items': critical_items,
        'activities': activities,
        'low_stock_list': low_stock_list,
        'chart_json': chart_json,
    }
    return render(request, 'dashboard.html', context)

@login_required
def barang_list(request):
    query = request.GET.get('q', '')
    kategori = request.GET.get('kategori', '')
    stok_alert = request.GET.get('stok_alert', '')
    
    items = Barang.objects.all()
    
    if query:
        items = items.filter(Q(kode_barang__icontains=query) | Q(nama_produk__icontains=query))
    if kategori:
        items = items.filter(kategori_id=kategori)
    if stok_alert == 'critical':
        items = items.filter(stok__lte=F('stok_minimum'))
        
    try:
        kategori_id = int(kategori) if kategori else None
    except ValueError:
        kategori_id = None

    kategori_choices = Kategori.objects.all()
    
    context = {
        'items': items,
        'query': query,
        'kategori': kategori,
        'kategori_id': kategori_id,
        'stok_alert': stok_alert,
        'kategori_choices': kategori_choices,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'inventory/barang_table_fragment.html', context)
        
    return render(request, 'inventory/list.html', context)

@login_required
def barang_create(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'barangListChanged': None,
                'showToast': {
                    'message': 'Barang berhasil ditambahkan!',
                    'type': 'success'
                }
            })
            return response
    else:
        form = BarangForm()
        
    return render(request, 'inventory/barang_form_modal.html', {'form': form, 'title': 'Tambah Barang'})

@login_required
def barang_update(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    if request.method == 'POST':
        form = BarangForm(request.POST, instance=barang)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'barangListChanged': None,
                'showToast': {
                    'message': f"Barang '{barang.nama_produk}' berhasil diubah!",
                    'type': 'success'
                }
            })
            return response
    else:
        form = BarangForm(instance=barang)
        
    return render(request, 'inventory/barang_form_modal.html', {
        'form': form,
        'barang': barang,
        'title': 'Ubah Barang'
    })

@login_required
def barang_delete(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    if request.method == 'POST':
        nama_produk = barang.nama_produk
        barang.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'barangListChanged': None,
            'showToast': {
                'message': f"Barang '{nama_produk}' berhasil dihapus!",
                'type': 'success'
            }
        })
        return response
        
    return render(request, 'inventory/barang_delete_confirm_modal.html', {'barang': barang})


# --- KATEGORI VIEWS ---
@login_required
def kategori_list(request):
    query = request.GET.get('q', '')
    items = Kategori.objects.all()
    if query:
        items = items.filter(nama__icontains=query)
    context = {'items': items, 'query': query}
    if request.headers.get('HX-Request'):
        return render(request, 'inventory/kategori_table_fragment.html', context)
    return render(request, 'inventory/kategori_list.html', context)

@login_required
def kategori_create(request):
    if request.method == 'POST':
        form = KategoriForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'kategoriListChanged': None,
                'showToast': {
                    'message': 'Kategori berhasil ditambahkan!',
                    'type': 'success'
                }
            })
            return response
    else:
        form = KategoriForm()
    return render(request, 'inventory/kategori_form_modal.html', {'form': form, 'title': 'Tambah Kategori'})

@login_required
def kategori_update(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    if request.method == 'POST':
        form = KategoriForm(request.POST, instance=kategori)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'kategoriListChanged': None,
                'showToast': {
                    'message': f"Kategori '{kategori.nama}' berhasil diubah!",
                    'type': 'success'
                }
            })
            return response
    else:
        form = KategoriForm(instance=kategori)
    return render(request, 'inventory/kategori_form_modal.html', {'form': form, 'kategori': kategori, 'title': 'Ubah Kategori'})

@login_required
def kategori_delete(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    if request.method == 'POST':
        nama_kategori = kategori.nama
        kategori.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'kategoriListChanged': None,
            'showToast': {
                'message': f"Kategori '{nama_kategori}' berhasil dihapus!",
                'type': 'success'
            }
        })
        return response
    return render(request, 'inventory/kategori_delete_confirm_modal.html', {'kategori': kategori})


# --- SUPPLIER VIEWS ---
@login_required
def supplier_list(request):
    query = request.GET.get('q', '')
    items = Supplier.objects.all()
    if query:
        items = items.filter(Q(nama__icontains=query) | Q(kontak__icontains=query))
    context = {'items': items, 'query': query}
    if request.headers.get('HX-Request'):
        return render(request, 'inventory/supplier_table_fragment.html', context)
    return render(request, 'inventory/supplier_list.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'supplierListChanged': None,
                'showToast': {
                    'message': 'Supplier berhasil ditambahkan!',
                    'type': 'success'
                }
            })
            return response
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form_modal.html', {'form': form, 'title': 'Tambah Supplier'})

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'supplierListChanged': None,
                'showToast': {
                    'message': f"Supplier '{supplier.nama}' berhasil diubah!",
                    'type': 'success'
                }
            })
            return response
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form_modal.html', {'form': form, 'supplier': supplier, 'title': 'Ubah Supplier'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        nama_supplier = supplier.nama
        supplier.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'supplierListChanged': None,
            'showToast': {
                'message': f"Supplier '{nama_supplier}' berhasil dihapus!",
                'type': 'success'
            }
        })
        return response
    return render(request, 'inventory/supplier_delete_confirm_modal.html', {'supplier': supplier})

