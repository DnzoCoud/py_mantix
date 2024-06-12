from django.urls import re_path, path
from . import views
urlpatterns = [
    re_path(r'findById/(?P<id>\d+)', views.findById, name='area_find_by_id'),
    path('findAll', views.findAll, name='area_find_all'),
    path('save', views.save, name='area_save'),
    path('importAreasByExcel', views.importAreasByExcel, name='area_importAreasByExcel'),
    path('update', views.update, name='area_update'),
    re_path(r'delete/(?P<id>\d+)', views.delete, name='area_delete'),



]