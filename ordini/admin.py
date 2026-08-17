from django.contrib import admin

from .models import Ordine, RigaOrdine


class RigaOrdineInline(admin.TabularInline):
    model = RigaOrdine
    extra = 0
    readonly_fields = ("subtotale",)
    fields = ("piatto", "quantita", "prezzo_unitario", "portata", "origine", "inviato_da", "stato", "note", "subtotale")


@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    list_display = ("tavolo", "stato", "aperto_il", "chiuso_il", "totale_display")
    list_filter = ("stato", "tavolo")
    inlines = [RigaOrdineInline]

    def totale_display(self, obj):
        return f"€{obj.totale}"

    totale_display.short_description = "Totale"
