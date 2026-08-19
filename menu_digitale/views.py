from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ImpostazioniMenu, Menu, categorie_con_piatti_per_menu


def menu_pubblico(request):
    """Pagina pubblica "Il nostro Menu": mostra sempre e solo il Menù
    ATTIVO in questo momento (quello scelto a mano dallo staff)."""
    menu_attivo = Menu.ottieni_attivo()
    impostazioni = ImpostazioniMenu.ottieni()
    categorie = categorie_con_piatti_per_menu(menu_attivo)
    return render(
        request,
        "menu_digitale/menu.html",
        {"categorie": categorie, "menu_attivo": menu_attivo, "impostazioni": impostazioni},
    )


def menu_dettaglio(request, menu_id):
    """Pagina pubblica con i piatti di UN Menù specifico, ANCHE se non è
    quello attivo ora — usata dalla pagina "Tutti i menù" per far sfogliare
    ai clienti anche le edizioni future, con un avviso se non è il menù
    servito oggi davvero."""
    menu = get_object_or_404(Menu, id=menu_id)
    impostazioni = ImpostazioniMenu.ottieni()
    categorie = categorie_con_piatti_per_menu(menu)
    menu_veramente_attivo = Menu.ottieni_attivo()
    e_anteprima = menu_veramente_attivo is None or menu.id != menu_veramente_attivo.id
    return render(
        request,
        "menu_digitale/menu.html",
        {
            "categorie": categorie,
            "menu_attivo": menu,
            "impostazioni": impostazioni,
            "e_anteprima": e_anteprima,
        },
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
