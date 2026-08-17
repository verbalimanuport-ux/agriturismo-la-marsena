import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PrenotazioneForm
from .models import Prenotazione, Tavolo

logger = logging.getLogger(__name__)


def prenota(request):
    """Form pubblico di prenotazione: nessun login richiesto (prenotazione 'guest')."""
    if request.method == "POST":
        form = PrenotazioneForm(request.POST)
        if form.is_valid():
            prenotazione = form.save()
            _invia_notifiche_email(prenotazione)
            return redirect("prenotazioni:conferma")
    else:
        form = PrenotazioneForm()
    return render(request, "prenotazioni/prenota.html", {"form": form})


def _invia_notifiche_email(prenotazione):
    """Invia una mail di conferma al cliente (se ha lasciato un'email) e un
    avviso interno allo staff. Se l'invio fallisce (es. mail non ancora
    configurata) non blocca la prenotazione: l'errore viene solo registrato."""
    data_str = prenotazione.data.strftime("%d/%m/%Y")
    ora_str = prenotazione.ora.strftime("%H:%M")

    if prenotazione.email:
        try:
            send_mail(
                subject="Richiesta di prenotazione ricevuta",
                message=(
                    f"Ciao {prenotazione.nome},\n\n"
                    f"Abbiamo ricevuto la tua richiesta di prenotazione per il {data_str} "
                    f"alle {ora_str}, per {prenotazione.numero_coperti} persone.\n\n"
                    "Ti ricontatteremo a breve per confermarla.\n\n"
                    "A presto!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[prenotazione.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Errore nell'invio dell'email di conferma al cliente")

    if settings.EMAIL_STAFF_NOTIFICHE:
        try:
            send_mail(
                subject=f"Nuova prenotazione: {prenotazione.nome} - {data_str} {ora_str}",
                message=(
                    "Nuova richiesta di prenotazione ricevuta:\n\n"
                    f"Nome: {prenotazione.nome}\n"
                    f"Data: {data_str}\n"
                    f"Ora: {ora_str}\n"
                    f"Persone: {prenotazione.numero_coperti}\n"
                    f"Telefono: {prenotazione.telefono or '-'}\n"
                    f"Email: {prenotazione.email or '-'}\n"
                    f"Note: {prenotazione.note or '-'}\n"
                    "Interesse lezione a cavallo: "
                    f"{'Sì' if prenotazione.interesse_lezione_cavallo else 'No'}\n\n"
                    "Gestiscila dal pannello: /admin/"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_STAFF_NOTIFICHE],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Errore nell'invio dell'email di avviso interno")


def conferma(request):
    return render(request, "prenotazioni/conferma.html")


@login_required
def dashboard(request):
    """Vista rapida per lo staff: prenotazioni di oggi e prossime, con la
    possibilità di confermarle o annullarle direttamente da qui."""
    if request.method == "POST":
        prenotazione_id = request.POST.get("prenotazione_id")
        azione = request.POST.get("azione")
        pren = get_object_or_404(Prenotazione, id=prenotazione_id)
        if azione == "conferma":
            pren.stato = Prenotazione.STATO_CONFERMATA
            pren.save()
        elif azione == "annulla":
            pren.stato = Prenotazione.STATO_ANNULLATA
            pren.save()
        elif azione == "assegna_tavolo":
            from ordini.models import Ordine  # import locale per evitare dipendenze incrociate a livello di modulo

            tavolo_id = request.POST.get("tavolo_id")
            tavolo = get_object_or_404(Tavolo, id=tavolo_id, attivo=True)
            ordine = Ordine.per_tavolo_aperto(tavolo)
            ordine.numero_coperti = pren.numero_coperti
            ordine.prenotazione = pren
            ordine.save()
            pren.tavolo = tavolo
            pren.stato = Prenotazione.STATO_ARRIVATA
            pren.save()
            messages.success(
                request, f"Tavolo {tavolo.numero} assegnato a {pren.nome} — coperti impostati automaticamente."
            )
            return redirect("ordini:gestisci_tavolo", tavolo_id=tavolo.id)
        return redirect("prenotazioni:dashboard")

    oggi = timezone.localdate()
    prenotazioni_oggi = (
        Prenotazione.objects.select_related("tavolo")
        .filter(data=oggi)
        .exclude(stato=Prenotazione.STATO_ANNULLATA)
    )
    prossime = (
        Prenotazione.objects.select_related("tavolo")
        .filter(data__gt=oggi)
        .exclude(stato=Prenotazione.STATO_ANNULLATA)[:30]
    )
    tavoli_attivi = Tavolo.objects.filter(attivo=True)
    return render(
        request,
        "prenotazioni/dashboard.html",
        {
            "prenotazioni_oggi": prenotazioni_oggi,
            "prossime": prossime,
            "oggi": oggi,
            "tavoli_attivi": tavoli_attivi,
        },
    )
