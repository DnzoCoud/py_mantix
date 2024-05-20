from django.urls import re_path, path
from . import views
urlpatterns = [
    re_path(r'getById/(?P<id>\d+)', views.findById, name='area_find_by_id'),
    path('getAll', views.findAll, name='area_find_all'),
    path('save', views.save, name='area_save')
]