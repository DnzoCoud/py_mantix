from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('get_machines', views.get_machines),
    
]