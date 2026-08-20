from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .models import Categoria, ImpostazioniMenu, Menu, categorie_con_piatti_per_menu, categorie_per_ruolo

TITOLI_RUOLO = {
    Categoria.RUOLO_VINI: "Carta dei Vini",
    Categoria.RUOLO_DOLCI: "I Nostri Dolci",
    Categoria.RUOLO_BEVANDE: "Bevande & Caffetteria",
}


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


def menu_ruolo(request, ruolo):
    """Pagina pubblica dedicata a Vini, Dolci o Bevande — raggiunta con un
    pulsante dalla pagina principale del menù, sempre riferita al Menù
    ATTIVO in questo momento."""
    if ruolo not in TITOLI_RUOLO:
        raise Http404
    menu_attivo = Menu.ottieni_attivo()
    categorie = categorie_per_ruolo(menu_attivo, ruolo)
    return render(
        request,
        "menu_digitale/menu_ruolo.html",
        {
            "categorie": categorie,
            "menu_attivo": menu_attivo,
            "titolo": TITOLI_RUOLO[ruolo],
        },
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
    """Impostazioni GENERALI del locale (QR, soglia ritardo cucina, coperto)
    più un riepilogo/gestione rapida del menù bambini dell'edizione attiva
    (i suoi altri campi restano su /admin/menu_digitale/menu/). Due moduli
    distinti sulla stessa pagina, ognuno con la propria azione — inviarne
    uno non deve toccare i campi dell'altro."""
    impostazioni = ImpostazioniMenu.ottieni()
    menu_attivo = Menu.ottieni_attivo()
    errore_prezzo = None

    if request.method == "POST" and request.POST.get("azione") == "salva_generali":
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

    elif request.method == "POST" and request.POST.get("azione") == "salva_bambini" and menu_attivo:
        menu_attivo.menu_bambini_attivo = request.POST.get("menu_bambini_attivo") == "on"
        prezzo_bambini_raw = request.POST.get("prezzo_menu_bambini_a_persona", "").strip()
        if prezzo_bambini_raw:
            try:
                menu_attivo.prezzo_menu_bambini_a_persona = Decimal(prezzo_bambini_raw)
            except InvalidOperation:
                pass
        menu_attivo.save()
        return redirect("menu_digitale:impostazioni")

    return render(
        request,
        "menu_digitale/impostazioni.html",
        {"impostazioni": impostazioni, "errore_prezzo": errore_prezzo, "menu_attivo": menu_attivo},
    )
