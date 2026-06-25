from django.contrib import admin
from django.urls import path, include
from inventory.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('auth/', include('accounts.urls')),
    path('barang/', include('inventory.urls')),
    path('transaksi/', include('transactions.urls')),
    path('laporan/', include('reports.urls')),
]
