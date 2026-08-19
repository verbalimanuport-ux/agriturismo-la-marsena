from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from menu_digitale.models import ImpostazioniMenu, Piatto
from prenotazioni.models import Prenotazione, Tavolo

SOGLIA_APPENA_SERVITO = timedelta(minutes=4)


class Ordine(models.Model):
    """Il 'conto' di un tavolo per il servizio in corso. Ci finiscono dentro
    le righe aggiunte sia dal cliente (QR code) sia dallo staff (tablet/telefono)."""

    STATO_APERTO = "aperto"
    STATO_CHIUSO = "chiuso"
    STATO_CHOICES = [
        (STATO_APERTO, "Aperto"),
        (STATO_CHIUSO, "Chiuso"),
    ]

    tavolo = models.ForeignKey(
        Tavolo, on_delete=models.CASCADE, related_name="ordini", verbose_name="Tavolo"
    )
    prenotazione = models.ForeignKey(
        Prenotazione,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordini",
        verbose_name="Prenotazione collegata",
        help_text="Se questo servizio nasce dall'assegnazione di una prenotazione.",
    )
    numero_coperti = models.PositiveIntegerField(
        default=1,
        verbose_name="Numero coperti",
        help_text="Persone al tavolo: usato per calcolare il conto del menù fisso.",
    )
    prezzo_menu_fisso_applicato = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Prezzo menù fisso applicato",
        help_text=(
            "Congelato all'apertura del tavolo: se il prezzo del menù fisso viene "
            "cambiato a metà servizio, i conti già aperti non cambiano."
        ),
    )
    stato = models.CharField(
        max_length=10, choices=STATO_CHOICES, default=STATO_APERTO, verbose_name="Stato"
    )
    aperto_il = models.DateTimeField(auto_now_add=True, verbose_name="Aperto il")
    chiuso_il = models.DateTimeField(null=True, blank=True, verbose_name="Chiuso il")
    volte_riaperto = models.PositiveIntegerField(
        default=0,
        verbose_name="Volte riaperto",
        help_text="Quante volte questo conto è stato riaperto dopo una chiusura.",
    )

    class Meta:
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"
        ordering = ["-aperto_il"]

    def __str__(self):
        return f"Ordine tavolo {self.tavolo.numero} ({self.get_stato_display()})"

    @classmethod
    def per_tavolo_aperto(cls, tavolo):
        """Ottiene il conto aperto di un tavolo, creandolo se non esiste ancora.
        Alla creazione congela il prezzo del menù fisso in vigore in quel
        momento, così un cambio di prezzo a metà servizio non altera i conti
        già aperti."""
        ordine = cls.objects.filter(tavolo=tavolo, stato=cls.STATO_APERTO).first()
        if ordine is not None:
            return ordine
        impostazioni = ImpostazioniMenu.ottieni()
        ordine, _creato = cls.objects.get_or_create(
            tavolo=tavolo,
            stato=cls.STATO_APERTO,
            defaults={"prezzo_menu_fisso_applicato": impostazioni.prezzo_menu_fisso_a_persona},
        )
        return ordine

    @property
    def prezzo_fisso_effettivo(self):
        """Il prezzo a persona da usare per questo conto: quello congelato
        all'apertura, o quello attuale se il conto è precedente a questa
        funzione (conti vecchi, campo ancora vuoto)."""
        if self.prezzo_menu_fisso_applicato is not None:
            return self.prezzo_menu_fisso_applicato
        return ImpostazioniMenu.ottieni().prezzo_menu_fisso_a_persona

    @property
    def totale(self):
        impostazioni = ImpostazioniMenu.ottieni()
        righe = list(self.righe.all())

        if impostazioni.modalita_attiva != ImpostazioniMenu.MODALITA_FISSO:
            # In "Carta" o "Entrambi" tutto si fattura a prezzo singolo,
            # anche i piatti etichettati "menù fisso" (es. quando una volta
            # ogni tanto si decide che tutto il menù è à la carte).
            return sum((r.subtotale for r in righe), start=0)

        # Modalità "Solo menù fisso": i piatti fissi entrano nel calcolo a
        # persona, tutto il resto (carta/sempre visibile) a prezzo singolo.
        totale_a_prezzo_singolo = sum(
            (r.subtotale for r in righe if r.piatto.tipo_menu != Piatto.TIPO_FISSO),
            start=0,
        )
        ha_piatti_fissi = any(r.piatto.tipo_menu == Piatto.TIPO_FISSO for r in righe)
        totale_fisso = 0
        if ha_piatti_fissi:
            totale_fisso = self.numero_coperti * self.prezzo_fisso_effettivo
        return totale_fisso + totale_a_prezzo_singolo

    def chiudi(self):
        self.stato = self.STATO_CHIUSO
        self.chiuso_il = timezone.now()
        self.save()
        if self.prenotazione_id and self.prenotazione.stato == Prenotazione.STATO_ARRIVATA:
            self.prenotazione.stato = Prenotazione.STATO_COMPLETATA
            self.prenotazione.save()

    def riapri(self):
        """Rimette il conto in stato aperto — serve quando un tavolo viene
        chiuso per errore. Tiene traccia di quante volte è successo, così
        resta visibile nello storico che quel conto è stato riaperto."""
        self.stato = self.STATO_APERTO
        self.chiuso_il = None
        self.volte_riaperto = (self.volte_riaperto or 0) + 1
        self.save()
        if self.prenotazione_id and self.prenotazione.stato == Prenotazione.STATO_COMPLETATA:
            self.prenotazione.stato = Prenotazione.STATO_ARRIVATA
            self.prenotazione.save()

    @property
    def stato_servizio(self):
        """Per la Sala/Mappa: 'completo' quando tutte le righe sono state
        servite/consegnate e non c'è più nulla in sospeso (in attesa di essere
        inviato, in cucina, pronto). Se non c'è ancora nessuna riga, resta
        semplicemente 'aperto' (tavolo occupato, non ha ancora ordinato)."""
        righe = list(self.righe.all())
        if not righe:
            return "aperto"
        if any(r.stato != RigaOrdine.STATO_SERVITO for r in righe):
            return "aperto"
        return "completo"

    @property
    def stato_sala(self):
        """Stato sintetico a 6 valori per colorare il tavolo in Sala/Cucina/
        Mappa (il settimo colore, 'libero', si applica quando non c'è nessun
        ordine aperto — non serve calcolarlo qui, lo decide chi chiama)."""
        righe = list(self.righe.all())
        if not righe:
            return "in_attesa_ordini"
        if any(r.stato == RigaOrdine.STATO_PRONTO for r in righe):
            return "pronto"
        if all(r.stato == RigaOrdine.STATO_SERVITO for r in righe):
            return "completo"
        adesso = timezone.now()
        appena_servite = any(
            r.stato == RigaOrdine.STATO_SERVITO
            and r.servita_il
            and (adesso - r.servita_il) < SOGLIA_APPENA_SERVITO
            for r in righe
        )
        if appena_servite:
            # Qualcosa è stato consegnato da pochi minuti, e non c'è altro di
            # più urgente in questo momento: un colore dedicato, temporaneo,
            # per confermare "consegna riuscita" invece di sparire nel nulla.
            return "appena_servito"
        if any(r.stato in (RigaOrdine.STATO_PREVISTO, RigaOrdine.STATO_IN_ATTESA) for r in righe):
            return "in_cucina"
        return "in_attesa_ordini"  # tutto ancora in bozza, non ancora inviato

    @property
    def giro_in_evidenza(self):
        """Il giro (tra quelli di cucina) più urgente da mostrare accanto al
        colore del tavolo in Sala/Mappa: il numero più basso non ancora
        completamente servito, con lo stato più avanzato tra i piatti che lo
        compongono (dentro un giro, ogni piatto diverso procede per conto
        suo — qui mostriamo solo un riepilogo generale, il dettaglio
        piatto per piatto sta in Cucina e sulla pagina del tavolo).
        None se non c'è nulla in sospeso lato cucina."""
        righe_cucina = [r for r in self.righe.all() if r.piatto.categoria.richiede_cucina]
        non_serviti = [r for r in righe_cucina if r.stato != RigaOrdine.STATO_SERVITO]
        if not non_serviti:
            return None
        numero = min(r.portata for r in non_serviti)
        stati_giro = {r.stato for r in non_serviti if r.portata == numero}
        if RigaOrdine.STATO_PRONTO in stati_giro:
            stato = "pronto"
        elif RigaOrdine.STATO_IN_ATTESA in stati_giro:
            stato = "in_cucina"
        elif RigaOrdine.STATO_PREVISTO in stati_giro:
            stato = "previsto"
        else:
            stato = "bozza"
        return {"numero": numero, "stato": stato}


class RigaOrdine(models.Model):
    ORIGINE_CLIENTE = "cliente"
    ORIGINE_STAFF = "staff"
    ORIGINE_CHOICES = [
        (ORIGINE_CLIENTE, "Cliente (QR)"),
        (ORIGINE_STAFF, "Staff"),
    ]

    STATO_BOZZA = "bozza"
    STATO_PREVISTO = "previsto"
    STATO_IN_ATTESA = "in_attesa"
    STATO_PRONTO = "pronto"
    STATO_SERVITO = "servito"
    STATO_CHOICES = [
        (STATO_BOZZA, "Da inviare"),
        (STATO_PREVISTO, "Previsto (in attesa del via libera)"),
        (STATO_IN_ATTESA, "In cucina"),
        (STATO_PRONTO, "Pronto"),
        (STATO_SERVITO, "Servito"),
    ]

    ordine = models.ForeignKey(
        Ordine, on_delete=models.CASCADE, related_name="righe", verbose_name="Ordine"
    )
    piatto = models.ForeignKey(Piatto, on_delete=models.PROTECT, verbose_name="Piatto/bevanda")
    quantita = models.PositiveIntegerField(default=1, verbose_name="Quantità")
    prezzo_unitario = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Prezzo unitario",
        help_text="Preso automaticamente dal prezzo del piatto al momento dell'ordine.",
    )
    origine = models.CharField(
        max_length=10, choices=ORIGINE_CHOICES, default=ORIGINE_STAFF, verbose_name="Aggiunto da"
    )
    inviato_da = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cameriere",
        help_text="Chi ha inviato l'ordine in cucina (vuoto se aggiunto dal cliente via QR).",
    )
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default=STATO_BOZZA,
        verbose_name="Stato preparazione",
    )
    portata = models.PositiveIntegerField(
        default=1,
        verbose_name="Giro d'uscita",
        help_text=(
            "Piatti con lo stesso numero escono insieme dalla cucina. Calcolato "
            "automaticamente dall'ordine della categoria, ma modificabile a mano "
            "(es. un secondo che deve uscire insieme agli antipasti). È solo "
            "un'etichetta di orientamento: il via libera e il pronto restano "
            "sempre per singolo piatto, non per l'intero giro."
        ),
    )
    note = models.CharField(max_length=200, blank=True, verbose_name="Note")
    creata_il = models.DateTimeField(auto_now_add=True, verbose_name="Aggiunta il")
    inviata_il = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inviata in cucina il",
        help_text="Da qui parte il conteggio del tempo di attesa mostrato alla cucina.",
    )
    servita_il = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Servita il",
        help_text="Usato per mostrare per qualche minuto il colore 'appena servito' in Sala.",
    )

    class Meta:
        verbose_name = "Riga ordine"
        verbose_name_plural = "Righe ordine"
        ordering = ["creata_il"]

    def __str__(self):
        return f"{self.quantita}x {self.piatto.nome}"

    @property
    def subtotale(self):
        return self.quantita * self.prezzo_unitario

    def save(self, *args, **kwargs):
        if not self.prezzo_unitario:
            self.prezzo_unitario = self.piatto.prezzo
        super().save(*args, **kwargs)
