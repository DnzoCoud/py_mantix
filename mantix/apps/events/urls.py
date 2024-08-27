from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path("findAll", views.findAll, name="event_find_all"),
    re_path(r"findById/(?P<id>\d+)", views.findById, name="event_find_by_id"),
    re_path("save", views.save, name="event_save"),
    re_path("update", views.update, name="event_update"),
    path("findByDay/", views.findEventsByDay, name="find-events-by-day"),
    path("importEventsByExcel", views.importEventsByExcel, name="importEventsByExcel"),
    path(
        "get_technician_performance",
        views.get_technician_performance,
        name="get_technician_performance",
    ),
    path(
        "get_activities_by_technical_and_event",
        views.get_activities_by_technical_and_event,
        name="get_activities_by_technical_and_event",
    ),
    path(
        "get_events_by_technical",
        views.get_events_by_technical,
        name="get_events_by_technical",
    ),
    path(
        "reprogram_request",
        views.reprogram_request,
        name="reprogram_request",
    ),
    path(
        "get_history_for_machine",
        views.get_history_for_machine,
        name="get_history_for_machine",
    ),
]
