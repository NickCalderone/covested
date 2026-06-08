from django.urls import path, include

urlpatterns = [
    path("", include("expenses.urls")),
    path("", include("labor.urls")),
    path("", include("properties.urls")),
]