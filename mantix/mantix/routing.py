from django.urls import re_path
from apps.events.consumers.consumer import EventConsumer

ws_urlpatterns = [
    re_path(r"ws/events/$", EventConsumer.as_asgi()),
]
