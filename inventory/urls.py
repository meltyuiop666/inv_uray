from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.barang_list, name='barang_list'),
    path('tambah/', views.barang_create, name='barang_create'),
    path('ubah/<int:pk>/', views.barang_update, name='barang_update'),
    path('hapus/<int:pk>/', views.barang_delete, name='barang_delete'),

    # Kategori
    path('kategori/', views.kategori_list, name='kategori_list'),
    path('kategori/tambah/', views.kategori_create, name='kategori_create'),
    path('kategori/ubah/<int:pk>/', views.kategori_update, name='kategori_update'),
    path('kategori/hapus/<int:pk>/', views.kategori_delete, name='kategori_delete'),

    # Supplier
    path('supplier/', views.supplier_list, name='supplier_list'),
    path('supplier/tambah/', views.supplier_create, name='supplier_create'),
    path('supplier/ubah/<int:pk>/', views.supplier_update, name='supplier_update'),
    path('supplier/hapus/<int:pk>/', views.supplier_delete, name='supplier_delete'),
]

