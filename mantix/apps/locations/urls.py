from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('findAll', views.findAll, name='location_find_all'),
    re_path(r'findById/(?P<id>\d+)', views.findById, name='location_find_by_id'),
    re_path('save', views.save, name='location_save'),
    re_path('importLocationsByExcel', views.importLocationsByExcel, name='location_importLocationsByExcel'),
    re_path('update', views.update, name='location_update'),
    re_path(r'delete/(?P<id>\d+)', views.delete, name='location_delete'),


]