from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('findAll', views.findAll, name='workOrder_find_all'),
    re_path(r'findWorkOrderByEventId/(?P<eventId>\d+)', views.findWorkOrderByEventId, name='workOrder_find_by_id'),
    re_path('save', views.save, name='workOrder_save'),
    # path('findByDay/', views.findworkOrdersByDay, name='find-workOrders-by-day'),
]