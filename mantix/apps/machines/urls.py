from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('findAll', views.findAll, name='machine_find_all'),
    re_path(r'findById/(?P<id>\d+)', views.findById, name='machine_find_by_id'),
    re_path('save', views.save, name='machine_save'),
    re_path('importMachinesByExcel', views.importMachinesByExcel, name='machine_importMachinesByExcel'),
    re_path('update', views.update, name='machine_update'),
    re_path(r'delete/(?P<id>\d+)', views.delete, name='machine_delete'),
]