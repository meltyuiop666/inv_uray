from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('masuk/', views.laporan_masuk, name='laporan_masuk'),
    path('masuk/excel/', views.export_masuk_excel, name='export_masuk_excel'),
    path('masuk/pdf/', views.export_masuk_pdf, name='export_masuk_pdf'),
    path('keluar/', views.laporan_keluar, name='laporan_keluar'),
    path('keluar/excel/', views.export_keluar_excel, name='export_keluar_excel'),
    path('keluar/pdf/', views.export_keluar_pdf, name='export_keluar_pdf'),
]
