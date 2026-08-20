from django.contrib import admin

from .models import Categoria, ImpostazioniMenu, Menu, Piatto


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        "nome", "attivo", "modalita_attiva", "prezzo_menu_fisso_a_persona",
        "menu_bambini_attivo", "prezzo_menu_bambini_a_persona", "data_inizio", "data_fine",
    )
    list_editable = (
        "attivo", "modalita_attiva", "prezzo_menu_fisso_a_persona",
        "menu_bambini_attivo", "prezzo_menu_bambini_a_persona", "data_inizio", "data_fine",
    )
    list_filter = ("attivo", "modalita_attiva")
    search_fields = ("nome", "descrizione")
    # Doppia colonna con checkbox: a sinistra tutti i piatti disponibili, a
    # destra quelli già scelti per questo menù — cerca e sposta con un clic.
    # "piatti_bambini" è lo stesso meccanismo ma per il percorso dedicato.
    filter_horizontal = ("piatti", "piatti_bambini")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ruolo", "richiede_cucina", "sempre_a_parte", "ordine")
    list_editable = ("ruolo", "richiede_cucina", "sempre_a_parte", "ordine")
    list_filter = ("ruolo",)


@admin.register(Piatto)
class PiattoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "prezzo", "disponibile", "ordine")
    list_editable = ("prezzo", "disponibile", "ordine")
    list_filter = ("categoria", "disponibile", "menus")
    search_fields = ("nome", "descrizione", "allergeni")


@admin.register(ImpostazioniMenu)
class ImpostazioniMenuAdmin(admin.ModelAdmin):
    list_display = ("ordini_qr_abilitati", "coperto_attivo", "prezzo_coperto", "soglia_ritardo_cucina_minuti")

    def has_add_permission(self, request):
        return not ImpostazioniMenu.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
