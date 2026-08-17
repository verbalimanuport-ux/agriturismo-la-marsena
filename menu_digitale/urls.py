from django.urls import path

from . import views

app_name = "menu_digitale"

urlpatterns = [
    path("", views.menu_pubblico, name="menu"),
    path("impostazioni/", views.impostazioni_menu, name="impostazioni"),
]
