from django.urls import re_path, path
from . import views
urlpatterns = [
    re_path(r'findById/(?P<id>\d+)', views.findById, name='area_find_by_id'),
    path('findAll', views.findAll, name='area_find_all'),
    path('save', views.save, name='area_save')
]