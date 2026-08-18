from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", core_views.home, name="home"),
    path("azienda-agricola/", core_views.azienda_agricola, name="azienda_agricola"),
    path("md-ranch/", core_views.md_ranch, name="md_ranch"),
    path("menu/", include("menu_digitale.urls")),
    path("ordini/", include("ordini.urls")),
    path("", include("prenotazioni.urls")),
    path(
        "staff/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("staff/logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
