from django.urls import path, include

urlpatterns = [
    path("expenses/", include("expenses.urls")),
    path("labor/", include("labor.urls")),
    path("properties/", include("properties.urls")),
]