from django.contrib import admin

from .models import Categoria, ImpostazioniMenu, Piatto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordine")
    list_editable = ("ordine",)


@admin.register(Piatto)
class PiattoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "tipo_menu", "prezzo", "disponibile", "ordine")
    list_editable = ("tipo_menu", "prezzo", "disponibile", "ordine")
    list_filter = ("categoria", "tipo_menu", "disponibile")
    search_fields = ("nome", "descrizione", "allergeni")


@admin.register(ImpostazioniMenu)
class ImpostazioniMenuAdmin(admin.ModelAdmin):
    list_display = ("modalita_attiva", "prezzo_menu_fisso_a_persona")

    def has_add_permission(self, request):
        return not ImpostazioniMenu.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
