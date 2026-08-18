from django.db import models


class Categoria(models.Model):
    """Es. Antipasti, Primi, Secondi, Dolci, Vini... L'ordine di visualizzazione
    è liberamente modificabile dallo staff. La categoria è solo un raggruppamento:
    la scelta menù fisso/carta/sempre visibile si fa sul singolo Piatto, non qui
    (una stessa categoria "Primi" può contenere sia piatti del menù fisso sia
    piatti disponibili solo alla carta)."""

    nome = models.CharField(max_length=100, verbose_name="Nome categoria")
    ordine = models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")
    richiede_cucina = models.BooleanField(
        default=True,
        verbose_name="Richiede cucina",
        help_text=(
            "Spegnilo per categorie come Vini/Bibite/Caffè: i piatti dentro non "
            "passeranno mai dalla vista Cucina, ma da una sezione 'Da consegnare' "
            "direttamente sulla pagina del tavolo."
        ),
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"
        ordering = ["ordine", "nome"]

    def __str__(self):
        return self.nome


class ImpostazioniMenu(models.Model):
    """Riga unica che dice cosa vedono i clienti in questo momento."""

    MODALITA_FISSO = "fisso"
    MODALITA_CARTA = "carta"
    MODALITA_ENTRAMBI = "entrambi"
    MODALITA_CHOICES = [
        (MODALITA_FISSO, "Solo menù fisso"),
        (MODALITA_CARTA, "Solo carta"),
        (MODALITA_ENTRAMBI, "Entrambi visibili"),
    ]

    modalita_attiva = models.CharField(
        max_length=10,
        choices=MODALITA_CHOICES,
        default=MODALITA_FISSO,
        verbose_name="Cosa mostrare ai clienti ora",
    )
    prezzo_menu_fisso_a_persona = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Prezzo menù fisso a persona (EUR)",
        help_text="Usato per calcolare il conto quando il tavolo ordina dal menù fisso.",
    )
    ordini_qr_abilitati = models.BooleanField(
        default=False,
        verbose_name="Permetti ordini dal QR",
        help_text=(
            "Se spento (consigliato per iniziare), chi scansiona il QR del tavolo vede "
            "solo il menù/la carta, senza poter ordinare. Il conto lo gestisce solo lo staff."
        ),
    )

    class Meta:
        verbose_name = "Impostazioni menù"
        verbose_name_plural = "Impostazioni menù"

    def __str__(self):
        return f"Modalità attuale: {self.get_modalita_attiva_display()}"

    @classmethod
    def ottieni(cls):
        obj, _creato = cls.objects.get_or_create(pk=1)
        return obj


class Piatto(models.Model):
    """Un piatto (o vino/bevanda). La scelta se fa parte del menù fisso,
    della carta, o se è sempre visibile, si fa qui: due piatti della stessa
    Categoria (es. entrambi "Primi") possono avere un Tipo di menù diverso."""

    TIPO_FISSO = "fisso"
    TIPO_CARTA = "carta"
    TIPO_SEMPRE = "sempre"
    TIPO_CHOICES = [
        (TIPO_FISSO, "Menù fisso"),
        (TIPO_CARTA, "Carta (à la carte)"),
        (TIPO_SEMPRE, "Sempre visibile (es. vini/bevande)"),
    ]

    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="piatti", verbose_name="Categoria"
    )
    nome = models.CharField(max_length=150, verbose_name="Nome piatto")
    descrizione = models.TextField(blank=True, verbose_name="Descrizione")
    prezzo = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Prezzo (EUR)")
    tipo_menu = models.CharField(
        max_length=10, choices=TIPO_CHOICES, default=TIPO_CARTA, verbose_name="Tipo di menù"
    )
    allergeni = models.CharField(max_length=200, blank=True, verbose_name="Allergeni")
    immagine = models.ImageField(
        upload_to="piatti/", blank=True, null=True, verbose_name="Foto piatto"
    )
    disponibile = models.BooleanField(default=True, verbose_name="Disponibile")
    ordine = models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")

    class Meta:
        verbose_name = "Piatto"
        verbose_name_plural = "Piatti"
        ordering = ["categoria__ordine", "ordine", "nome"]

    def __str__(self):
        return f"{self.nome} - EUR {self.prezzo}"

    @classmethod
    def attivi(cls):
        """Restituisce i piatti disponibili da mostrare ora: quelli del tipo
        di menù attualmente attivo (fisso o carta), più quelli sempre
        visibili (es. vini/bevande). Se l'impostazione è 'entrambi', li
        restituisce tutti."""
        impostazioni = ImpostazioniMenu.ottieni()
        qs = cls.objects.filter(disponibile=True)
        if impostazioni.modalita_attiva == ImpostazioniMenu.MODALITA_ENTRAMBI:
            return qs
        return qs.filter(
            models.Q(tipo_menu=impostazioni.modalita_attiva) | models.Q(tipo_menu=cls.TIPO_SEMPRE)
        )
