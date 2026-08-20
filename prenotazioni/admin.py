from django.contrib import admin

from .models import Prenotazione, Tavolo


@admin.register(Tavolo)
class TavoloAdmin(admin.ModelAdmin):
    list_display = ("numero", "capienza", "zona", "attivo")
    list_editable = ("capienza", "zona", "attivo")
    search_fields = ("numero", "zona")
    list_filter = ("attivo", "zona")


@admin.register(Prenotazione)
class PrenotazioneAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "data",
        "ora",
        "numero_coperti",
        "numero_bambini",
        "numero_seggioloni",
        "bambini_menu_dedicato",
        "tavolo",
        "stato",
        "interesse_lezione_cavallo",
        "telefono",
        "email",
        "creata_il",
    )
    list_editable = ("tavolo", "stato", "bambini_menu_dedicato")
    list_filter = ("stato", "data", "interesse_lezione_cavallo")
    search_fields = ("nome", "telefono", "email", "note")
    date_hierarchy = "data"
    ordering = ("data", "ora")
