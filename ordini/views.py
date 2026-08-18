import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from menu_digitale.models import Categoria, ImpostazioniMenu, Piatto
from prenotazioni.models import LayoutSala, Tavolo

from .forms import AggiungiPiattoForm
from .models import Ordine, RigaOrdine

SOGLIA_ATTESA_MINUTI = 15


def _genera_portate_standard_se_fisso(ordine, utente):
    """Se è attivo il menù fisso, crea automaticamente una riga per OGNI
    piatto fisso disponibile, con quantità pari ai coperti del tavolo — nel
    menù fisso, di norma, tutti i piatti fissi di una categoria (anche se
    sono più di uno, es. 2 antipasti) vengono serviti a tutti i coperti, non
    è una scelta tra opzioni. Non tocca mai una riga già esistente verso il
    basso (non cancella eccezioni già segnate dal cameriere) — al massimo la
    alza, se sono aumentati i coperti."""
    impostazioni = ImpostazioniMenu.ottieni()
    if impostazioni.modalita_attiva != ImpostazioniMenu.MODALITA_FISSO:
        return

    piatti_fissi = Piatto.objects.filter(
        tipo_menu=Piatto.TIPO_FISSO, disponibile=True
    ).select_related("categoria")

    for piatto in piatti_fissi:
        riga = ordine.righe.filter(piatto=piatto).first()
        if riga is None:
            RigaOrdine.objects.create(
                ordine=ordine,
                piatto=piatto,
                quantita=ordine.numero_coperti,
                portata=piatto.categoria.ordine or 1,
                origine=RigaOrdine.ORIGINE_STAFF,
                inviato_da=utente,
            )
        elif riga.quantita < ordine.numero_coperti:
            riga.quantita = ordine.numero_coperti
            riga.save()


def ordina_tavolo(request, numero_tavolo):
    """Pagina pubblica raggiungibile scansionando il QR code posato sul tavolo.
    Nessun login richiesto.
    - Se "Permetti ordini dal QR" è spento: il cliente vede SOLO il menù/la
      carta, in sola consultazione, senza nessuna possibilità di ordinare.
    - Se acceso e il menù fisso è attivo: il cliente vede solo gli 'extra' da
      ordinare (bevande ecc.), le portate del menù fisso sono già generate
      automaticamente in base ai coperti.
    - Se acceso e la carta è attiva: il cliente sceglie e ordina normalmente."""
    tavolo = get_object_or_404(Tavolo, numero=numero_tavolo, attivo=True)
    impostazioni = ImpostazioniMenu.ottieni()

    if not impostazioni.ordini_qr_abilitati:
        piatti_attivi_qs = Piatto.attivi().order_by("ordine", "nome")
        tutte_le_categorie = Categoria.objects.prefetch_related(
            Prefetch("piatti", queryset=piatti_attivi_qs, to_attr="piatti_attivi")
        ).order_by("ordine", "nome")
        categorie = [c for c in tutte_le_categorie if c.piatti_attivi]
        return render(
            request,
            "ordini/solo_menu_tavolo.html",
            {"tavolo": tavolo, "categorie": categorie, "impostazioni": impostazioni},
        )

    ordine = Ordine.per_tavolo_aperto(tavolo)
    solo_extra = impostazioni.modalita_attiva == ImpostazioniMenu.MODALITA_FISSO

    if request.method == "POST":
        form = AggiungiPiattoForm(request.POST, solo_extra=solo_extra)
        if form.is_valid():
            piatto = form.cleaned_data["piatto"]
            RigaOrdine.objects.create(
                ordine=ordine,
                piatto=piatto,
                quantita=form.cleaned_data["quantita"],
                note=form.cleaned_data["note"],
                origine=RigaOrdine.ORIGINE_CLIENTE,
                portata=piatto.categoria.ordine or 1,
            )
            messages.success(request, "Ordine inviato!")
            return redirect("ordini:ordina_tavolo", numero_tavolo=numero_tavolo)
    else:
        form = AggiungiPiattoForm(solo_extra=solo_extra)

    return render(
        request,
        "ordini/ordina_tavolo.html",
        {
            "tavolo": tavolo,
            "ordine": ordine,
            "form": form,
            "impostazioni": impostazioni,
            "solo_extra": solo_extra,
        },
    )


@login_required
def sala(request):
    """Vista d'insieme per lo staff: quali tavoli hanno un conto aperto, e
    quali hanno piatti pronti da ritirare (in attesa del cameriere)."""
    tavoli = Tavolo.objects.filter(attivo=True)
    ordini_aperti = {o.tavolo_id: o for o in Ordine.objects.filter(stato=Ordine.STATO_APERTO)}

    pronti_per_ordine = {
        r["ordine_id"]: r["totale"]
        for r in RigaOrdine.objects.filter(
            ordine__stato=Ordine.STATO_APERTO, stato=RigaOrdine.STATO_PRONTO
        )
        .values("ordine_id")
        .annotate(totale=Count("id"))
    }

    tavoli_con_ordine = []
    totale_pronti = 0
    for t in tavoli:
        ordine = ordini_aperti.get(t.id)
        pronti = pronti_per_ordine.get(ordine.id, 0) if ordine else 0
        totale_pronti += pronti
        tavoli_con_ordine.append((t, ordine, pronti))

    return render(
        request,
        "ordini/sala.html",
        {"tavoli_con_ordine": tavoli_con_ordine, "totale_pronti": totale_pronti},
    )


@login_required
def gestisci_tavolo(request, tavolo_id):
    """Vista per il cameriere: con menù fisso, imposta solo i coperti (le
    portate standard si generano da sole) e gestisce eccezioni/extra; con la
    carta, aggiunge i piatti scelti come sempre. Può sempre chiudere il conto
    a fine servizio."""
    tavolo = get_object_or_404(Tavolo, id=tavolo_id)
    ordine = Ordine.per_tavolo_aperto(tavolo)
    impostazioni = ImpostazioniMenu.ottieni()

    if request.method == "POST":
        azione = request.POST.get("azione")
        if azione == "aggiungi":
            form = AggiungiPiattoForm(request.POST)
            if form.is_valid():
                piatto = form.cleaned_data["piatto"]
                RigaOrdine.objects.create(
                    ordine=ordine,
                    piatto=piatto,
                    quantita=form.cleaned_data["quantita"],
                    note=form.cleaned_data["note"],
                    origine=RigaOrdine.ORIGINE_STAFF,
                    inviato_da=request.user,
                    portata=piatto.categoria.ordine or 1,
                )
                messages.success(request, f"Aggiunto: {piatto.nome}.")
        elif azione == "rimuovi":
            riga_id = request.POST.get("riga_id")
            RigaOrdine.objects.filter(id=riga_id, ordine=ordine).delete()
            messages.success(request, "Piatto rimosso.")
        elif azione == "cambia_portata":
            try:
                riga_id = request.POST.get("riga_id")
                nuova_portata = int(request.POST.get("portata"))
                if nuova_portata > 0:
                    RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(
                        portata=nuova_portata
                    )
                    messages.success(request, f"Spostato al giro {nuova_portata}.")
            except (TypeError, ValueError):
                pass
        elif azione == "cambia_note":
            riga_id = request.POST.get("riga_id")
            nuova_nota = request.POST.get("note", "").strip()
            RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(note=nuova_nota)
            messages.success(request, "Nota salvata.")
        elif azione == "giro_servito":
            portata = request.POST.get("portata")
            RigaOrdine.objects.filter(
                ordine=ordine, portata=portata, stato=RigaOrdine.STATO_PRONTO
            ).update(stato=RigaOrdine.STATO_SERVITO)
            messages.success(request, f"Giro {portata} segnato come servito.")
        elif azione == "cambia_quantita":
            try:
                riga_id = request.POST.get("riga_id")
                nuova_quantita = int(request.POST.get("quantita"))
                if nuova_quantita > 0:
                    RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(
                        quantita=nuova_quantita
                    )
                    messages.success(request, "Quantità aggiornata.")
                else:
                    # quantità azzerata: la riga non ha più senso, la togliamo
                    RigaOrdine.objects.filter(id=riga_id, ordine=ordine).delete()
                    messages.success(request, "Piatto rimosso (quantità azzerata).")
            except (TypeError, ValueError):
                pass
        elif azione == "aggiorna_coperti":
            try:
                nuovi_coperti = int(request.POST.get("numero_coperti", ordine.numero_coperti))
                if nuovi_coperti > 0:
                    ordine.numero_coperti = nuovi_coperti
                    ordine.save()
                    _genera_portate_standard_se_fisso(ordine, request.user)
                    messages.success(request, f"Coperti aggiornati a {nuovi_coperti}.")
            except (TypeError, ValueError):
                pass
        elif azione == "chiudi_conto":
            totale = ordine.totale
            ordine.chiudi()
            messages.success(
                request, f"Conto del tavolo {tavolo.numero} chiuso. Totale: €{totale}"
            )
            return redirect("ordini:sala")
        return redirect("ordini:gestisci_tavolo", tavolo_id=tavolo.id)

    form = AggiungiPiattoForm()
    righe = list(
        ordine.righe.select_related("piatto__categoria", "inviato_da").order_by(
            "portata", "creata_il"
        )
    )
    giri_map = {}
    for riga in righe:
        giri_map.setdefault(riga.portata, []).append(riga)

    giri = []
    for numero in sorted(giri_map.keys()):
        righe_giro = giri_map[numero]
        stati = {r.stato for r in righe_giro}
        if RigaOrdine.STATO_IN_ATTESA in stati:
            stato_giro = "in_cucina"
        elif RigaOrdine.STATO_PRONTO in stati:
            stato_giro = "pronto"
        else:
            stato_giro = "servito"
        giri.append({"numero": numero, "stato_giro": stato_giro, "righe": righe_giro})

    giri_pronti = sum(1 for g in giri if g["stato_giro"] == "pronto")

    return render(
        request,
        "ordini/gestisci_tavolo.html",
        {
            "tavolo": tavolo,
            "ordine": ordine,
            "form": form,
            "impostazioni": impostazioni,
            "giri": giri,
            "giri_pronti": giri_pronti,
            "chiave_notifica_tavolo": f"tavolo_{tavolo.id}",
        },
    )


@login_required
def cucina(request):
    """Vista per la cucina: cosa preparare, raggruppato per tavolo e per giro.
    Un solo pulsante 'Pronto' per l'intero giro (non per singolo piatto): una
    volta segnato, il giro sparisce dalla vista cucina — da lì in poi tocca
    al cameriere, che lo vede pronto sulla pagina del tavolo e lo consegna."""
    if request.method == "POST":
        ordine_id = request.POST.get("ordine_id")
        portata = request.POST.get("portata")
        RigaOrdine.objects.filter(
            ordine_id=ordine_id, portata=portata, stato=RigaOrdine.STATO_IN_ATTESA
        ).update(stato=RigaOrdine.STATO_PRONTO)
        return redirect("ordini:cucina")

    righe = (
        RigaOrdine.objects.filter(
            ordine__stato=Ordine.STATO_APERTO, stato=RigaOrdine.STATO_IN_ATTESA
        )
        .select_related("ordine__tavolo", "piatto__categoria", "inviato_da")
        .order_by("ordine__aperto_il", "portata", "creata_il")
    )

    adesso = timezone.now()
    tavoli_raggruppati = {}
    for riga in righe:
        riga.minuti_attesa = int((adesso - riga.creata_il).total_seconds() // 60)
        riga.in_ritardo = riga.minuti_attesa >= SOGLIA_ATTESA_MINUTI
        tavolo = riga.ordine.tavolo
        tavoli_raggruppati.setdefault(tavolo, []).append(riga)

    return render(
        request,
        "ordini/cucina.html",
        {"tavoli_raggruppati": tavoli_raggruppati.items(), "totale_in_attesa": len(righe)},
    )


@login_required
def stampa_qr(request):
    """Pagina con i QR code di tutti i tavoli attivi, pronta da stampare."""
    tavoli = Tavolo.objects.filter(attivo=True)
    tavoli_con_url = [
        (t, request.build_absolute_uri(f"/ordini/tavolo/{t.numero}/")) for t in tavoli
    ]
    return render(request, "ordini/stampa_qr.html", {"tavoli_con_url": tavoli_con_url})


@login_required
def mappa_tavoli(request):
    """Mappa visiva della sala: perimetro disegnato a punti dallo staff,
    tavoli posizionabili trascinandoli. Cliccando su un tavolo (fuori dalla
    modalità modifica) si va alla sua pagina di gestione, come dalla Sala."""
    if request.method == "POST":
        try:
            dati = json.loads(request.body)
        except (ValueError, TypeError):
            return JsonResponse({"ok": False, "errore": "Dati non validi."}, status=400)

        for t in dati.get("tavoli", []):
            Tavolo.objects.filter(id=t.get("id")).update(pos_x=t.get("x"), pos_y=t.get("y"))

        layout = LayoutSala.ottieni()
        layout.punti = dati.get("perimetro", [])
        layout.save()
        return JsonResponse({"ok": True})

    tavoli_qs = Tavolo.objects.filter(attivo=True).order_by("numero")
    ordini_aperti = {o.tavolo_id: o for o in Ordine.objects.filter(stato=Ordine.STATO_APERTO)}
    pronti_per_ordine = {
        r["ordine_id"]: r["totale"]
        for r in RigaOrdine.objects.filter(
            ordine__stato=Ordine.STATO_APERTO, stato=RigaOrdine.STATO_PRONTO
        )
        .values("ordine_id")
        .annotate(totale=Count("id"))
    }

    tavoli_dati = []
    for i, t in enumerate(tavoli_qs):
        x, y = t.pos_x, t.pos_y
        if x is None or y is None:
            # posizione di partenza a griglia, finché lo staff non li trascina
            colonne = 4
            x = 15 + (i % colonne) * 25
            y = 20 + (i // colonne) * 25
        ordine = ordini_aperti.get(t.id)
        pronti = pronti_per_ordine.get(ordine.id, 0) if ordine else 0
        tavoli_dati.append(
            {
                "id": t.id,
                "numero": t.numero,
                "x": x,
                "y": y,
                "aperto": bool(ordine),
                "totale": float(ordine.totale) if ordine else 0,
                "pronti": pronti,
            }
        )

    layout = LayoutSala.ottieni()
    return render(
        request,
        "ordini/mappa_tavoli.html",
        {
            "tavoli_json": json.dumps(tavoli_dati),
            "perimetro_json": layout.perimetro_json,
        },
    )
