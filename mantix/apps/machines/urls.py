from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('findAll', views.findAll, name='machine_find_all'),
    re_path(r'findById/(?P<id>\d+)', views.findById, name='machine_find_by_id'),
    re_path('save', views.save, name='machine_save'),

    
]