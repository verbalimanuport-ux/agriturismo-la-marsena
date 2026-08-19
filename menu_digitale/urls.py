from django.urls import path

from . import views

app_name = "menu_digitale"

urlpatterns = [
    path("", views.menu_pubblico, name="menu"),
    path("tutti/", views.elenco_menu, name="elenco_menu"),
    path("impostazioni/", views.impostazioni_menu, name="impostazioni"),
    path("<int:menu_id>/", views.menu_dettaglio, name="menu_dettaglio"),
]
