import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from menu_digitale.models import Categoria, ImpostazioniMenu, Piatto
from prenotazioni.models import LayoutSala, Tavolo

from .forms import AggiungiPiattoForm
from .models import Ordine, RigaOrdine

SOGLIA_ATTESA_MINUTI = 15


def _riepilogo_tavoli():
    """Stato sintetico di tutti i tavoli attivi, usato da Sala, Mappa e dalla
    striscia di riepilogo nella schermata Cucina — un solo posto dove
    calcolarlo, per non ripetere la stessa logica in tre punti diversi."""
    tavoli = Tavolo.objects.filter(attivo=True).order_by("numero")
    ordini_aperti = {
        o.tavolo_id: o
        for o in Ordine.objects.filter(stato=Ordine.STATO_APERTO).prefetch_related(
            "righe__piatto__categoria"
        )
    }
    risultato = []
    for t in tavoli:
        ordine = ordini_aperti.get(t.id)
        if ordine is None:
            risultato.append(
                {"tavolo": t, "ordine": None, "pronti": 0, "stato_sala": "libero", "giro": None}
            )
            continue
        righe = list(ordine.righe.all())
        pronti = sum(1 for r in righe if r.stato == RigaOrdine.STATO_PRONTO)
        risultato.append(
            {
                "tavolo": t,
                "ordine": ordine,
                "pronti": pronti,
                "stato_sala": ordine.stato_sala,
                "giro": ordine.giro_in_evidenza,
            }
        )
    return risultato


def _genera_portate_standard_se_fisso(ordine, utente):
    """Se è attivo il menù fisso, crea automaticamente una riga per OGNI
    piatto fisso disponibile, con quantità pari ai coperti del tavolo — nel
    menù fisso, di norma, tutti i piatti fissi di una categoria (anche se
    sono più di uno, es. 2 antipasti) vengono serviti a tutti i coperti, non
    è una scelta tra opzioni. Non tocca mai una riga già esistente verso il
    basso (non cancella eccezioni già segnate dal cameriere) — al massimo la
    alza, se sono aumentati i coperti. Le righe partono come "Da inviare":
    tocca al cameriere premere "Invia in cucina" quando ha finito di comporre
    l'ordine (note, extra ecc.)."""
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
                stato=RigaOrdine.STATO_BOZZA,
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
                stato=RigaOrdine.STATO_BOZZA,
            )
            messages.success(request, "Richiesta ricevuta! Il cameriere la invierà a breve.")
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
    """Vista d'insieme per lo staff: colore e stato di ogni tavolo, quanti
    piatti sono pronti da ritirare."""
    dati = _riepilogo_tavoli()
    totale_pronti = sum(d["pronti"] for d in dati)
    return render(
        request,
        "ordini/sala.html",
        {"dati_tavoli": dati, "totale_pronti": totale_pronti},
    )


@login_required
def gestisci_tavolo(request, tavolo_id):
    """Vista per il cameriere. Se il tavolo è libero, chiede conferma prima
    di aprirlo davvero (evita di 'occupare' un tavolo solo guardandolo dalla
    mappa/Sala). Una volta aperto: con menù fisso, imposta i coperti (le
    portate standard si generano da sole, come bozza); il cameriere compone
    l'ordine con calma (note, extra) e preme "Invia in cucina" quando è
    pronto — solo da lì in poi la cucina lo vede."""
    tavolo = get_object_or_404(Tavolo, id=tavolo_id)
    ordine_esistente = Ordine.objects.filter(tavolo=tavolo, stato=Ordine.STATO_APERTO).first()

    if request.method == "POST" and request.POST.get("azione") == "apri_tavolo":
        Ordine.per_tavolo_aperto(tavolo)
        return redirect("ordini:gestisci_tavolo", tavolo_id=tavolo.id)

    if ordine_esistente is None:
        return render(request, "ordini/conferma_apertura_tavolo.html", {"tavolo": tavolo})

    ordine = ordine_esistente
    impostazioni = ImpostazioniMenu.ottieni()

    if request.method == "POST":
        azione = request.POST.get("azione")
        salvataggio_automatico = request.POST.get("salvataggio_automatico") == "1"

        if salvataggio_automatico:
            # Salvataggio silenzioso in background (il cameriere è uscito da un
            # campo): nessun messaggio, nessun ricaricamento della pagina.
            riga_id = request.POST.get("riga_id")
            if azione == "cambia_note":
                RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(
                    note=request.POST.get("note", "").strip()
                )
            elif azione == "cambia_portata":
                try:
                    valore = int(request.POST.get("portata"))
                    if valore > 0:
                        RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(portata=valore)
                except (TypeError, ValueError):
                    pass
            elif azione == "cambia_quantita":
                try:
                    valore = int(request.POST.get("quantita"))
                    if valore > 0:
                        RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(quantita=valore)
                    else:
                        RigaOrdine.objects.filter(id=riga_id, ordine=ordine).delete()
                except (TypeError, ValueError):
                    pass
            return JsonResponse({"ok": True})

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
                    stato=RigaOrdine.STATO_BOZZA,
                )
                messages.success(request, f"{piatto.nome} aggiunto — premi \"Invia in cucina\" quando hai finito.")
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
                    RigaOrdine.objects.filter(id=riga_id, ordine=ordine).delete()
                    messages.success(request, "Piatto rimosso (quantità azzerata).")
            except (TypeError, ValueError):
                pass
        elif azione == "invia_cucina":
            # Rete di sicurezza: raccoglie anche le note appena scritte dal
            # cameriere e non ancora salvate singolarmente, così non si perde
            # mai nulla anche se si dimentica di confermarle.
            for chiave, valore in request.POST.items():
                if chiave.startswith("nota_riga_"):
                    try:
                        riga_id = int(chiave.replace("nota_riga_", ""))
                    except ValueError:
                        continue
                    RigaOrdine.objects.filter(id=riga_id, ordine=ordine).update(
                        note=valore.strip()
                    )

            righe_da_inviare = list(
                ordine.righe.filter(stato=RigaOrdine.STATO_BOZZA).select_related("piatto__categoria")
            )
            adesso_invio = timezone.now()
            for riga in righe_da_inviare:
                if riga.piatto.categoria.richiede_cucina:
                    # Anche il primo giro resta "Previsto": parte davvero solo
                    # quando il cameriere dà il via libera dalla pagina del
                    # tavolo. La cucina lo vede comunque subito, per potersi
                    # organizzare in anticipo.
                    riga.stato = RigaOrdine.STATO_PREVISTO
                else:
                    riga.stato = RigaOrdine.STATO_PRONTO
                    riga.inviata_il = adesso_invio
                riga.save()
            if righe_da_inviare:
                messages.success(
                    request,
                    f"Ordine inviato! ({len(righe_da_inviare)} voci) — dai il via libera "
                    "alla cucina quando siete pronti a far partire ogni giro.",
                )
            else:
                messages.info(request, "Non c'era nulla da inviare.")
        elif azione == "via_libera_giro":
            portata = request.POST.get("portata")
            adesso = timezone.now()
            aggiornate = RigaOrdine.objects.filter(
                ordine=ordine, portata=portata, stato=RigaOrdine.STATO_PREVISTO
            ).update(stato=RigaOrdine.STATO_IN_ATTESA, inviata_il=adesso)
            if aggiornate:
                messages.success(request, f"Via libera dato al giro {portata}: ora è in cucina.")
        elif azione == "giro_servito":
            portata = request.POST.get("portata")
            RigaOrdine.objects.filter(
                ordine=ordine, portata=portata, stato=RigaOrdine.STATO_PRONTO
            ).update(stato=RigaOrdine.STATO_SERVITO)
            messages.success(request, f"Giro {portata} segnato come servito.")
        elif azione == "storna":
            riga_id = request.POST.get("riga_id")
            riga = RigaOrdine.objects.filter(id=riga_id, ordine=ordine).select_related("piatto").first()
            if riga is not None:
                nome_piatto = riga.piatto.nome
                era_in_cucina = riga.stato == RigaOrdine.STATO_IN_ATTESA
                riga.delete()
                if era_in_cucina:
                    messages.warning(
                        request,
                        f"{nome_piatto} stornato dal conto — era già in preparazione: "
                        "avvisa la cucina di persona!",
                    )
                else:
                    messages.success(request, f"{nome_piatto} stornato dal conto.")
        elif azione == "consegnato":
            riga_id = request.POST.get("riga_id")
            RigaOrdine.objects.filter(
                id=riga_id, ordine=ordine, stato=RigaOrdine.STATO_PRONTO
            ).update(stato=RigaOrdine.STATO_SERVITO)
            messages.success(request, "Segnato come consegnato.")
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
            in_sospeso = ordine.righe.exclude(stato=RigaOrdine.STATO_SERVITO).count()
            forzato = request.POST.get("forza") == "1"
            if in_sospeso and not forzato:
                messages.error(
                    request,
                    f"Attenzione: ci sono ancora {in_sospeso} voci non servite. "
                    "Controlla il tavolo e premi di nuovo per chiudere comunque.",
                )
                return redirect("ordini:gestisci_tavolo", tavolo_id=tavolo.id)
            totale = ordine.totale
            ordine.chiudi()
            messages.success(
                request, f"Conto del tavolo {tavolo.numero} chiuso. Totale: €{totale}"
            )
            return redirect("ordini:sala")
        return redirect("ordini:gestisci_tavolo", tavolo_id=tavolo.id)

    form = AggiungiPiattoForm()
    tutte_le_righe = list(
        ordine.righe.select_related("piatto__categoria", "inviato_da").order_by(
            "portata", "creata_il"
        )
    )

    righe_bozza = [r for r in tutte_le_righe if r.stato == RigaOrdine.STATO_BOZZA]

    righe_cucina = [
        r
        for r in tutte_le_righe
        if r.stato != RigaOrdine.STATO_BOZZA and r.piatto.categoria.richiede_cucina
    ]
    giri_map = {}
    for riga in righe_cucina:
        giri_map.setdefault(riga.portata, []).append(riga)

    giri = []
    for numero in sorted(giri_map.keys()):
        righe_giro = giri_map[numero]
        stati = {r.stato for r in righe_giro}
        if RigaOrdine.STATO_PREVISTO in stati:
            stato_giro = "previsto"
        elif RigaOrdine.STATO_IN_ATTESA in stati:
            stato_giro = "in_cucina"
        elif RigaOrdine.STATO_PRONTO in stati:
            stato_giro = "pronto"
        else:
            stato_giro = "servito"
        giri.append({"numero": numero, "stato_giro": stato_giro, "righe": righe_giro})

    giri_pronti = sum(1 for g in giri if g["stato_giro"] == "pronto")

    da_consegnare = [
        r
        for r in tutte_le_righe
        if r.stato == RigaOrdine.STATO_PRONTO and not r.piatto.categoria.richiede_cucina
    ]

    return render(
        request,
        "ordini/gestisci_tavolo.html",
        {
            "tavolo": tavolo,
            "ordine": ordine,
            "form": form,
            "impostazioni": impostazioni,
            "righe_bozza": righe_bozza,
            "giri": giri,
            "giri_pronti": giri_pronti,
            "da_consegnare": da_consegnare,
            "voci_in_sospeso": sum(
                1 for r in tutte_le_righe if r.stato != RigaOrdine.STATO_SERVITO
            ),
            "chiave_notifica_tavolo": f"tavolo_{tavolo.id}",
        },
    )


@login_required
def cucina(request):
    """Vista per la cucina: cosa preparare, raggruppato per tavolo e per giro
    (solo per le categorie che richiedono cucina: vini/bibite/caffè non
    compaiono mai qui). Include anche i giri "Previsti" — inviati dal
    cameriere ma non ancora avviati col via libera — per permettere di
    organizzarsi in anticipo, mostrati però senza cronometro e senza pulsante,
    dato che non si può ancora agire su di loro. Un solo pulsante 'Pronto' per
    l'intero giro attivo (non per singolo piatto): una volta segnato, il giro
    sparisce da qui — da lì in poi tocca al cameriere, che lo vede pronto
    sulla pagina del tavolo e lo consegna."""
    if request.method == "POST":
        ordine_id = request.POST.get("ordine_id")
        portata = request.POST.get("portata")
        RigaOrdine.objects.filter(
            ordine_id=ordine_id, portata=portata, stato=RigaOrdine.STATO_IN_ATTESA
        ).update(stato=RigaOrdine.STATO_PRONTO)
        return redirect("ordini:cucina")

    righe = (
        RigaOrdine.objects.filter(
            ordine__stato=Ordine.STATO_APERTO,
            stato__in=[RigaOrdine.STATO_PREVISTO, RigaOrdine.STATO_IN_ATTESA],
            piatto__categoria__richiede_cucina=True,
        )
        .select_related("ordine__tavolo", "piatto__categoria", "inviato_da")
        .order_by("ordine__aperto_il", "portata", "creata_il")
    )

    adesso = timezone.now()
    soglia = ImpostazioniMenu.ottieni().soglia_ritardo_cucina_minuti or SOGLIA_ATTESA_MINUTI
    tavoli_raggruppati = {}
    for riga in righe:
        if riga.stato == RigaOrdine.STATO_IN_ATTESA:
            # Il tempo di attesa parte da quando è arrivato il via libera, non
            # da quando il cameriere ha composto la comanda.
            riferimento = riga.inviata_il or riga.creata_il
            riga.minuti_attesa = int((adesso - riferimento).total_seconds() // 60)
            riga.in_ritardo = riga.minuti_attesa >= soglia
        else:
            riga.minuti_attesa = None
            riga.in_ritardo = False
        tavolo = riga.ordine.tavolo
        tavoli_raggruppati.setdefault(tavolo, []).append(riga)

    return render(
        request,
        "ordini/cucina.html",
        {
            "tavoli_raggruppati": tavoli_raggruppati.items(),
            "totale_in_attesa": len(righe),
            "riepilogo_sala": _riepilogo_tavoli(),
        },
    )


@login_required
def stampa_qr(request):
    """Pagina con i QR code di tutti i tavoli attivi, pronta da stampare."""
    tavoli = Tavolo.objects.filter(attivo=True)
    tavoli_con_url = [
        (
            t,
            request.build_absolute_uri(
                reverse("ordini:ordina_tavolo", kwargs={"numero_tavolo": t.numero})
            ),
        )
        for t in tavoli
    ]
    return render(request, "ordini/stampa_qr.html", {"tavoli_con_url": tavoli_con_url})


@login_required
def mappa_tavoli(request):
    """Mappa visiva della sala: perimetro disegnato a punti dallo staff,
    tavoli posizionabili trascinandoli (dimensione proporzionale alla
    capienza). Cliccando su un tavolo (fuori dalla modalità modifica) si va
    alla sua pagina di gestione, come dalla Sala — se libero, chiede conferma
    prima di aprirlo davvero."""
    if request.method == "POST":
        try:
            dati = json.loads(request.body)
        except (ValueError, TypeError):
            return JsonResponse({"ok": False, "errore": "Dati non validi."}, status=400)

        def _coordinata_valida(valore):
            try:
                numero = float(valore)
            except (TypeError, ValueError):
                return None
            if numero != numero:  # scarta i valori "non numerici" (NaN)
                return None
            return max(0.0, min(100.0, numero))

        for t in dati.get("tavoli", []):
            x = _coordinata_valida(t.get("x"))
            y = _coordinata_valida(t.get("y"))
            if x is None or y is None:
                continue
            try:
                tavolo_id = int(t.get("id"))
            except (TypeError, ValueError):
                continue
            Tavolo.objects.filter(id=tavolo_id).update(pos_x=x, pos_y=y)

        punti_validi = []
        for p in dati.get("perimetro", []):
            if not isinstance(p, dict):
                continue
            x = _coordinata_valida(p.get("x"))
            y = _coordinata_valida(p.get("y"))
            if x is None or y is None:
                continue
            punti_validi.append({"x": round(x, 2), "y": round(y, 2)})

        layout = LayoutSala.ottieni()
        layout.punti = punti_validi
        layout.save()
        return JsonResponse({"ok": True})

    dati = _riepilogo_tavoli()
    tavoli_dati = []
    for i, d in enumerate(dati):
        t = d["tavolo"]
        x, y = t.pos_x, t.pos_y
        if x is None or y is None:
            # posizione di partenza a griglia, finché lo staff non li trascina
            colonne = 4
            x = 15 + (i % colonne) * 25
            y = 20 + (i // colonne) * 25
        tavoli_dati.append(
            {
                "id": t.id,
                "numero": t.numero,
                "capienza": t.capienza,
                "x": x,
                "y": y,
                "stato_sala": d["stato_sala"],
                "pronti": d["pronti"],
                "giro": d["giro"],
                "totale": float(d["ordine"].totale) if d["ordine"] else 0,
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


@login_required
def preconto(request, ordine_id):
    """Preconto stampabile da portare al tavolo, con la possibilità di
    dividerlo tra più persone ("alla romana").

    ATTENZIONE: è un documento di cortesia per far vedere al cliente cosa ha
    consumato, NON uno scontrino fiscale — quello va sempre emesso a parte con
    il registratore di cassa."""
    ordine = get_object_or_404(
        Ordine.objects.select_related("tavolo", "prenotazione"), id=ordine_id
    )
    impostazioni = ImpostazioniMenu.ottieni()

    righe = list(
        ordine.righe.select_related("piatto__categoria").order_by("portata", "creata_il")
    )

    # Righe fatturate a prezzo singolo (carta, vini, bibite...)
    modalita_fissa = impostazioni.modalita_attiva == ImpostazioniMenu.MODALITA_FISSO
    voci_singole = []
    coperti_menu_fisso = 0
    for r in righe:
        if modalita_fissa and r.piatto.tipo_menu == Piatto.TIPO_FISSO:
            coperti_menu_fisso = ordine.numero_coperti
            continue
        voci_singole.append(r)

    totale = ordine.totale
    try:
        dividi_per = int(request.GET.get("dividi", ordine.numero_coperti) or 1)
    except (TypeError, ValueError):
        dividi_per = ordine.numero_coperti
    dividi_per = max(1, min(dividi_per, 50))
    quota = (totale / dividi_per) if dividi_per else totale

    return render(
        request,
        "ordini/preconto.html",
        {
            "ordine": ordine,
            "tavolo": ordine.tavolo,
            "voci_singole": voci_singole,
            "coperti_menu_fisso": coperti_menu_fisso,
            "prezzo_fisso": ordine.prezzo_fisso_effettivo,
            "totale": totale,
            "dividi_per": dividi_per,
            "quota": quota,
            "adesso": timezone.now(),
        },
    )


@login_required
def conti_chiusi(request):
    """Storico dei conti chiusi di oggi, con la possibilità di riaprirne uno
    chiuso per errore (solo se il tavolo non ha già un altro conto aperto)."""
    if request.method == "POST":
        ordine_id = request.POST.get("ordine_id")
        ordine = get_object_or_404(Ordine, id=ordine_id, stato=Ordine.STATO_CHIUSO)
        gia_aperto = Ordine.objects.filter(
            tavolo=ordine.tavolo, stato=Ordine.STATO_APERTO
        ).exists()
        if gia_aperto:
            messages.error(
                request,
                f"Il tavolo {ordine.tavolo.numero} ha già un altro conto aperto: "
                "chiudi prima quello, poi riprova.",
            )
        else:
            ordine.riapri()
            messages.success(request, f"Conto del tavolo {ordine.tavolo.numero} riaperto.")
            return redirect("ordini:gestisci_tavolo", tavolo_id=ordine.tavolo_id)
        return redirect("ordini:conti_chiusi")

    oggi = timezone.localdate()
    ordini = (
        Ordine.objects.filter(stato=Ordine.STATO_CHIUSO, chiuso_il__date=oggi)
        .select_related("tavolo", "prenotazione")
        .prefetch_related("righe__piatto__categoria")
        .order_by("-chiuso_il")
    )
    incasso_giornata = sum((o.totale for o in ordini), start=0)
    return render(
        request,
        "ordini/conti_chiusi.html",
        {"ordini": ordini, "oggi": oggi, "incasso_giornata": incasso_giornata},
    )
