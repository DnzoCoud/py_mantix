from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path("findAllRoles", views.findAllRoles),
    re_path("findAllMenus", views.findAllMenus),
    re_path("update_role_menus/", views.update_role_menus),
]
