import json

from django.db import models


class Tavolo(models.Model):
    """Un tavolo della sala. Numero, capienza e zona sono sempre modificabili
    dallo staff dal pannello di gestione, senza bisogno di toccare il codice.
    pos_x/pos_y sono la posizione sulla mappa della sala (percentuale 0-100
    rispetto all'area disegnata), impostata trascinando il tavolo sulla mappa."""

    numero = models.CharField(max_length=10, unique=True, verbose_name="Numero tavolo")
    capienza = models.PositiveIntegerField(verbose_name="Capienza (posti)")
    zona = models.CharField(max_length=100, blank=True, verbose_name="Zona / sala")
    attivo = models.BooleanField(default=True, verbose_name="Attivo (utilizzabile)")
    pos_x = models.FloatField(
        null=True, blank=True, verbose_name="Posizione X sulla mappa (%)"
    )
    pos_y = models.FloatField(
        null=True, blank=True, verbose_name="Posizione Y sulla mappa (%)"
    )
    ruotato = models.BooleanField(
        default=False,
        verbose_name="Ruotato (verticale invece di orizzontale)",
        help_text="Utile per un tavolo grande che deve stare posizionato di traverso rispetto agli altri.",
    )

    class Meta:
        verbose_name = "Tavolo"
        verbose_name_plural = "Tavoli"
        ordering = ["numero"]

    def __str__(self):
        return f"Tavolo {self.numero} ({self.capienza} posti)"


class LayoutSala(models.Model):
    """Riga unica: la forma (perimetro) della sala disegnata dallo staff,
    come elenco di punti (poligono libero, non necessariamente un rettangolo).
    Salvato come testo JSON: [{"x": 10, "y": 10}, {"x": 90, "y": 10}, ...]
    (coordinate in percentuale, da 0 a 100)."""

    perimetro_json = models.TextField(default="[]", blank=True, verbose_name="Perimetro (JSON)")

    class Meta:
        verbose_name = "Layout sala"
        verbose_name_plural = "Layout sala"

    def __str__(self):
        return f"Layout sala ({len(self.punti)} punti)"

    @property
    def punti(self):
        try:
            return json.loads(self.perimetro_json)
        except (ValueError, TypeError):
            return []

    @punti.setter
    def punti(self, valore):
        self.perimetro_json = json.dumps(valore)

    @classmethod
    def ottieni(cls):
        obj, _creato = cls.objects.get_or_create(pk=1)
        return obj


class Prenotazione(models.Model):
    STATO_IN_ATTESA = "in_attesa"
    STATO_CONFERMATA = "confermata"
    STATO_ARRIVATA = "arrivata"
    STATO_COMPLETATA = "completata"
    STATO_ANNULLATA = "annullata"
    STATO_CHOICES = [
        (STATO_IN_ATTESA, "In attesa di conferma"),
        (STATO_CONFERMATA, "Confermata"),
        (STATO_ARRIVATA, "Arrivata"),
        (STATO_COMPLETATA, "Completata"),
        (STATO_ANNULLATA, "Annullata"),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome e cognome")
    telefono = models.CharField(max_length=30, blank=True, verbose_name="Telefono")
    email = models.EmailField(blank=True, verbose_name="Email")
    data = models.DateField(verbose_name="Data")
    ora = models.TimeField(verbose_name="Ora")
    numero_coperti = models.PositiveIntegerField(verbose_name="Numero persone")
    numero_bambini = models.PositiveIntegerField(
        default=0,
        verbose_name="Di cui bambini",
        help_text="Utile alla sala per organizzarsi, a prescindere da quale menù sarà attivo quel giorno.",
    )
    numero_seggioloni = models.PositiveIntegerField(
        default=0,
        verbose_name="Seggioloni richiesti",
    )
    bambini_menu_dedicato = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Bambini al menù dedicato?",
        help_text=(
            "Da decidere alla telefonata di conferma (solo se quel giorno il menù bambini "
            "è attivo): sì, no, o non ancora deciso."
        ),
    )
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
