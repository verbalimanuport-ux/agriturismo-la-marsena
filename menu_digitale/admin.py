from django.contrib import admin

from .models import Categoria, ImpostazioniMenu, Menu, Piatto


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("nome", "attivo", "modalita_attiva", "prezzo_menu_fisso_a_persona", "data_inizio", "data_fine")
    list_editable = ("attivo", "modalita_attiva", "prezzo_menu_fisso_a_persona", "data_inizio", "data_fine")
    list_filter = ("attivo", "modalita_attiva")
    search_fields = ("nome", "descrizione")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "menu", "richiede_cucina", "ordine")
    list_editable = ("richiede_cucina", "ordine")
    list_filter = ("menu",)


@admin.register(Piatto)
class PiattoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "tipo_menu", "prezzo", "disponibile", "ordine")
    list_editable = ("tipo_menu", "prezzo", "disponibile", "ordine")
    list_filter = ("categoria__menu", "categoria", "tipo_menu", "disponibile")
    search_fields = ("nome", "descrizione", "allergeni")


@admin.register(ImpostazioniMenu)
class ImpostazioniMenuAdmin(admin.ModelAdmin):
    list_display = ("ordini_qr_abilitati", "coperto_attivo", "prezzo_coperto", "soglia_ritardo_cucina_minuti")

    def has_add_permission(self, request):
        return not ImpostazioniMenu.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
