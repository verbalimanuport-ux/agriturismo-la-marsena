from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import redirect, render

from .models import Categoria, ImpostazioniMenu, Menu, Piatto


def menu_pubblico(request):
    """Pagina pubblica "Il nostro Menu": mostra sempre e solo il Menù
    ATTIVO in questo momento (quello scelto a mano dallo staff)."""
    menu_attivo = Menu.ottieni_attivo()
    impostazioni = ImpostazioniMenu.ottieni()
    categorie = []
    if menu_attivo is not None:
        piatti_attivi_qs = Piatto.attivi().order_by("ordine", "nome")
        tutte_le_categorie = Categoria.objects.filter(menu=menu_attivo).prefetch_related(
            Prefetch("piatti", queryset=piatti_attivi_qs, to_attr="piatti_attivi")
        ).order_by("ordine", "nome")
        categorie = [c for c in tutte_le_categorie if c.piatti_attivi]
    return render(
        request,
        "menu_digitale/menu.html",
        {"categorie": categorie, "menu_attivo": menu_attivo, "impostazioni": impostazioni},
    )


def elenco_menu(request):
    """Pagina pubblica con TUTTI i menù (anche quelli non attivi ora, con le
    loro date previste) — per far scegliere ai clienti quando prenotare in
    base al menù che preferiscono, e per invogliarli a tornare per un menù
    a tema futuro."""
    menu_tutti = Menu.objects.all().order_by("-attivo", "data_inizio", "nome")
    return render(request, "menu_digitale/elenco_menu.html", {"menu_tutti": menu_tutti})


@login_required
def impostazioni_menu(request):
    """Impostazioni GENERALI del locale, valide per tutti i menù (QR, soglia
    ritardo cucina, coperto). La modalità e il prezzo del menù fisso non sono
    più qui: appartengono a ogni singola edizione di Menù, gestita da
    /admin/menu_digitale/menu/."""
    impostazioni = ImpostazioniMenu.ottieni()
    errore_prezzo = None
    if request.method == "POST":
        impostazioni.ordini_qr_abilitati = request.POST.get("ordini_qr_abilitati") == "on"
        impostazioni.coperto_attivo = request.POST.get("coperto_attivo") == "on"

        prezzo_raw = request.POST.get("prezzo_coperto", "").strip()
        if prezzo_raw:
            try:
                impostazioni.prezzo_coperto = Decimal(prezzo_raw)
            except InvalidOperation:
                errore_prezzo = "Il prezzo del coperto inserito non è un numero valido: non è stato modificato."

        try:
            soglia = int(request.POST.get("soglia_ritardo_cucina_minuti", ""))
            if 1 <= soglia <= 120:
                impostazioni.soglia_ritardo_cucina_minuti = soglia
        except (TypeError, ValueError):
            pass

        impostazioni.save()
        if not errore_prezzo:
            return redirect("menu_digitale:impostazioni")

    menu_attivo = Menu.ottieni_attivo()
    return render(
        request,
        "menu_digitale/impostazioni.html",
        {"impostazioni": impostazioni, "errore_prezzo": errore_prezzo, "menu_attivo": menu_attivo},
    )
