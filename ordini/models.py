from django.conf import settings
from django.db import models
from django.utils import timezone

from menu_digitale.models import ImpostazioniMenu, Piatto
from prenotazioni.models import Prenotazione, Tavolo


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
    stato = models.CharField(
        max_length=10, choices=STATO_CHOICES, default=STATO_APERTO, verbose_name="Stato"
    )
    aperto_il = models.DateTimeField(auto_now_add=True, verbose_name="Aperto il")
    chiuso_il = models.DateTimeField(null=True, blank=True, verbose_name="Chiuso il")

    class Meta:
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"
        ordering = ["-aperto_il"]

    def __str__(self):
        return f"Ordine tavolo {self.tavolo.numero} ({self.get_stato_display()})"

    @classmethod
    def per_tavolo_aperto(cls, tavolo):
        """Ottiene il conto aperto di un tavolo, creandolo se non esiste ancora."""
        ordine, _creato = cls.objects.get_or_create(tavolo=tavolo, stato=cls.STATO_APERTO)
        return ordine

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
            totale_fisso = self.numero_coperti * impostazioni.prezzo_menu_fisso_a_persona
        return totale_fisso + totale_a_prezzo_singolo

    def chiudi(self):
        self.stato = self.STATO_CHIUSO
        self.chiuso_il = timezone.now()
        self.save()

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


class RigaOrdine(models.Model):
    ORIGINE_CLIENTE = "cliente"
    ORIGINE_STAFF = "staff"
    ORIGINE_CHOICES = [
        (ORIGINE_CLIENTE, "Cliente (QR)"),
        (ORIGINE_STAFF, "Staff"),
    ]

    STATO_BOZZA = "bozza"
    STATO_IN_ATTESA = "in_attesa"
    STATO_PRONTO = "pronto"
    STATO_SERVITO = "servito"
    STATO_CHOICES = [
        (STATO_BOZZA, "Da inviare"),
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
            "(es. un secondo che deve uscire insieme agli antipasti)."
        ),
    )
    note = models.CharField(max_length=200, blank=True, verbose_name="Note")
    creata_il = models.DateTimeField(auto_now_add=True, verbose_name="Aggiunta il")

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
