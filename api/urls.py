from django.urls import path, include

urlpatterns = [
    path("properties/", include("properties.urls")),
]