from django.urls import path

from . import views

app_name = "ordini"

urlpatterns = [
    path("tavolo/<str:numero_tavolo>/", views.ordina_tavolo, name="ordina_tavolo"),
    path("staff/sala/", views.sala, name="sala"),
    path("staff/cucina/", views.cucina, name="cucina"),
    path("staff/qrcode/", views.stampa_qr, name="stampa_qr"),
    path("staff/tavolo/<int:tavolo_id>/", views.gestisci_tavolo, name="gestisci_tavolo"),
]
