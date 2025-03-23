from django.urls import path

from .views import root_api

urlpatterns = [
    path("", root_api, name="root_api"),
]
