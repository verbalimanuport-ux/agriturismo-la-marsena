from django.db import models


class Tavolo(models.Model):
    """Un tavolo della sala. Numero, capienza e zona sono sempre modificabili
    dallo staff dal pannello di gestione, senza bisogno di toccare il codice."""

    numero = models.CharField(max_length=10, unique=True, verbose_name="Numero tavolo")
    capienza = models.PositiveIntegerField(verbose_name="Capienza (posti)")
    zona = models.CharField(max_length=100, blank=True, verbose_name="Zona / sala")
    attivo = models.BooleanField(default=True, verbose_name="Attivo (utilizzabile)")

    class Meta:
        verbose_name = "Tavolo"
        verbose_name_plural = "Tavoli"
        ordering = ["numero"]

    def __str__(self):
        return f"Tavolo {self.numero} ({self.capienza} posti)"


class Prenotazione(models.Model):
    STATO_IN_ATTESA = "in_attesa"
    STATO_CONFERMATA = "confermata"
    STATO_ARRIVATA = "arrivata"
    STATO_ANNULLATA = "annullata"
    STATO_CHOICES = [
        (STATO_IN_ATTESA, "In attesa di conferma"),
        (STATO_CONFERMATA, "Confermata"),
        (STATO_ARRIVATA, "Arrivata"),
        (STATO_ANNULLATA, "Annullata"),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome e cognome")
    telefono = models.CharField(max_length=30, blank=True, verbose_name="Telefono")
    email = models.EmailField(blank=True, verbose_name="Email")
    data = models.DateField(verbose_name="Data")
    ora = models.TimeField(verbose_name="Ora")
    numero_coperti = models.PositiveIntegerField(verbose_name="Numero persone")
    note = models.TextField(blank=True, verbose_name="Note (allergie, richieste...)")
    interesse_lezione_cavallo = models.BooleanField(
        default=False,
        verbose_name='Interessato a "battesimo della sella" (lezione a cavallo)',
    )
    tavolo = models.ForeignKey(
        Tavolo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tavolo assegnato",
        help_text="Da assegnare/modificare dallo staff.",
    )
    stato = models.CharField(
        max_length=20, choices=STATO_CHOICES, default=STATO_IN_ATTESA, verbose_name="Stato"
    )
    creata_il = models.DateTimeField(auto_now_add=True, verbose_name="Ricevuta il")

    class Meta:
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"
        ordering = ["data", "ora"]

    def __str__(self):
        return f"{self.nome} - {self.data} {self.ora} ({self.numero_coperti} persone)"
