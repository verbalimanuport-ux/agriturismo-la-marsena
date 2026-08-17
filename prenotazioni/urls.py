from django.urls import path

from . import views

app_name = "prenotazioni"

urlpatterns = [
    path("prenota/", views.prenota, name="prenota"),
    path("prenota/grazie/", views.conferma, name="conferma"),
    path("staff/dashboard/", views.dashboard, name="dashboard"),
]
