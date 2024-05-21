from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('findAll', views.findAll, name='location_find_all'),
    re_path(r'findById/(?P<id>\d+)', views.findById, name='location_find_by_id'),
    re_path('save', views.save, name='location_save'),
    re_path('importData', views.import_locations, name='location_import_data'),
]