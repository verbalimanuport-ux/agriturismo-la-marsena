from django.urls import path

from . import views

app_name = "menu_digitale"

urlpatterns = [
    path("", views.menu_pubblico, name="menu"),
    path("vini/", views.menu_ruolo, {"ruolo": "vini"}, name="menu_vini"),
    path("dolci/", views.menu_ruolo, {"ruolo": "dolci"}, name="menu_dolci"),
    path("bevande/", views.menu_ruolo, {"ruolo": "bevande"}, name="menu_bevande"),
    path("tutti/", views.elenco_menu, name="elenco_menu"),
    path("impostazioni/", views.impostazioni_menu, name="impostazioni"),
    path("<int:menu_id>/", views.menu_dettaglio, name="menu_dettaglio"),
]
