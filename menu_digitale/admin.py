from django.contrib import admin

from .models import Categoria, ImpostazioniMenu, Menu, Piatto, PiattoMenu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("nome", "attivo", "modalita_attiva", "prezzo_menu_fisso_a_persona", "data_inizio", "data_fine")
    list_editable = ("attivo", "modalita_attiva", "prezzo_menu_fisso_a_persona", "data_inizio", "data_fine")
    list_filter = ("attivo", "modalita_attiva")
    search_fields = ("nome", "descrizione")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "richiede_cucina", "ordine")
    list_editable = ("richiede_cucina", "ordine")


class PiattoMenuInline(admin.TabularInline):
    model = PiattoMenu
    extra = 1
    fields = ("menu", "tipo_menu")
    verbose_name = "Presenza in un menù"
    verbose_name_plural = "In quali menù compare, e con che tipo in ciascuno"


@admin.register(Piatto)
class PiattoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "prezzo", "disponibile", "ordine")
    list_editable = ("prezzo", "disponibile", "ordine")
    list_filter = ("categoria", "disponibile", "menus")
    search_fields = ("nome", "descrizione", "allergeni")
    inlines = [PiattoMenuInline]


@admin.register(PiattoMenu)
class PiattoMenuAdmin(admin.ModelAdmin):
    list_display = ("piatto", "menu", "tipo_menu")
    list_editable = ("tipo_menu",)
    list_filter = ("menu", "tipo_menu")
    search_fields = ("piatto__nome",)


@admin.register(ImpostazioniMenu)
class ImpostazioniMenuAdmin(admin.ModelAdmin):
    list_display = ("ordini_qr_abilitati", "coperto_attivo", "prezzo_coperto", "soglia_ritardo_cucina_minuti")

    def has_add_permission(self, request):
        return not ImpostazioniMenu.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
