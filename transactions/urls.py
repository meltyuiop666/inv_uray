from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Barang Masuk
    path('masuk/', views.masuk_list, name='masuk_list'),
    path('masuk/tambah/', views.masuk_create, name='masuk_create'),
    path('masuk/ubah/<int:pk>/', views.masuk_update, name='masuk_update'),
    path('masuk/hapus/<int:pk>/', views.masuk_delete, name='masuk_delete'),
    
    # Barang Keluar
    path('keluar/', views.keluar_list, name='keluar_list'),
    path('keluar/tambah/', views.keluar_create, name='keluar_create'),
    path('keluar/ubah/<int:pk>/', views.keluar_update, name='keluar_update'),
    path('keluar/hapus/<int:pk>/', views.keluar_delete, name='keluar_delete'),

    # Stock Ledger
    path('ledger/', views.ledger_list, name='ledger_list'),
]
