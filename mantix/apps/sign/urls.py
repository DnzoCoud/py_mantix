from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('login', views.login),
    re_path('register', views.register),
    re_path('logout', views.logout),
    re_path('profile', views.profile),
    re_path('findUserDirectors', views.findUserDirectors),
    re_path('findTechnicals', views.findTechnicals),
    re_path('findManagers', views.findManagers),
    re_path('update', views.update),
    re_path(r'importUsersByExcel/(?P<role>\w+)', views.importUsersByExcel),  # \w+ para cadenas de texto
    re_path(r'findById/(?P<id>\d+)', views.findById, name='machine_find_by_id'),
    re_path('save', views.save),
    re_path('findAll', views.findAll),
    re_path('loginTechnical', views.loginTechnical),

]