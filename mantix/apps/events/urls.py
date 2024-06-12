from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('findAll', views.findAll, name='event_find_all'),
    re_path(r'findById/(?P<id>\d+)', views.findById, name='event_find_by_id'),
    re_path('save', views.save, name='event_save'),
    re_path('update', views.update, name='event_update'),
    path('findByDay/', views.findEventsByDay, name='find-events-by-day'),
    path('importEventsByExcel', views.importEventsByExcel, name='importEventsByExcel'),

]