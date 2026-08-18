from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import redirect, render

from .models import Categoria, ImpostazioniMenu, Piatto


def menu_pubblico(request):
    piatti_attivi_qs = Piatto.attivi().order_by("ordine", "nome")
    tutte_le_categorie = Categoria.objects.prefetch_related(
        Prefetch("piatti", queryset=piatti_attivi_qs, to_attr="piatti_attivi")
    ).order_by("ordine", "nome")
    categorie = [c for c in tutte_le_categorie if c.piatti_attivi]
    impostazioni = ImpostazioniMenu.ottieni()
    return render(
        request, "menu_digitale/menu.html", {"categorie": categorie, "impostazioni": impostazioni}
    )


@login_required
def impostazioni_menu(request):
    impostazioni = ImpostazioniMenu.ottieni()
    errore_prezzo = None
    if request.method == "POST":
        nuova_modalita = request.POST.get("modalita_attiva")
        if nuova_modalita in dict(ImpostazioniMenu.MODALITA_CHOICES):
            impostazioni.modalita_attiva = nuova_modalita

        prezzo_raw = request.POST.get("prezzo_menu_fisso_a_persona", "").strip()
        if prezzo_raw:
            try:
                impostazioni.prezzo_menu_fisso_a_persona = Decimal(prezzo_raw)
            except InvalidOperation:
                errore_prezzo = "Il prezzo inserito non è un numero valido: non è stato modificato."
        # Se il campo è lasciato vuoto, il prezzo precedente resta invariato
        # (non viene mai azzerato per errore).

        impostazioni.ordini_qr_abilitati = request.POST.get("ordini_qr_abilitati") == "on"

        impostazioni.save()
        if not errore_prezzo:
            return redirect("menu_digitale:impostazioni")
    return render(
        request,
        "menu_digitale/impostazioni.html",
        {"impostazioni": impostazioni, "errore_prezzo": errore_prezzo},
    )
