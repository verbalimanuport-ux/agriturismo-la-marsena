from django.db import models


class Menu(models.Model):
    """Un'edizione del menù (es. 'Menù di Agosto', 'Cena a tema Halloween').
    Resta sempre nel sistema, riutilizzabile quando torna di stagione — non
    scade e non si cancella mai da sola. Solo UN Menù alla volta è "Attivo":
    è quello usato per il servizio reale (cucina, QR, ordini). Le date sono
    solo un'informazione per i clienti sulla pagina pubblica — non attivano
    né disattivano nulla in automatico, lo decide sempre lo staff a mano."""

    MODALITA_FISSO = "fisso"
    MODALITA_CARTA = "carta"
    MODALITA_ENTRAMBI = "entrambi"
    MODALITA_CHOICES = [
        (MODALITA_FISSO, "Solo menù fisso"),
        (MODALITA_CARTA, "Solo carta"),
        (MODALITA_ENTRAMBI, "Entrambi visibili"),
    ]

    nome = models.CharField(max_length=150, verbose_name="Nome del menù")
    descrizione = models.TextField(
        blank=True,
        verbose_name="Descrizione",
        help_text="Testo mostrato ai clienti nella pagina pubblica dei menù.",
    )
    data_inizio = models.DateField(null=True, blank=True, verbose_name="Data inizio prevista")
    data_fine = models.DateField(null=True, blank=True, verbose_name="Data fine prevista")
    attivo = models.BooleanField(
        default=False,
        verbose_name="Attivo (in uso ora per il servizio)",
        help_text=(
            "Solo un menù alla volta può essere attivo: attivandone uno, "
            "quello che era attivo prima si spegne da solo."
        ),
    )
    modalita_attiva = models.CharField(
        max_length=10,
        choices=MODALITA_CHOICES,
        default=MODALITA_FISSO,
        verbose_name="Modalità",
    )
    prezzo_menu_fisso_a_persona = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Prezzo menù fisso a persona (EUR)",
        help_text="Usato per calcolare il conto quando il tavolo ordina dal menù fisso.",
    )

    class Meta:
        verbose_name = "Menù"
        verbose_name_plural = "Menù"
        ordering = ["-attivo", "-data_inizio", "nome"]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.attivo:
            # Esclusivo: attivarne uno spegne automaticamente tutti gli altri,
            # così non si rischia mai di avere due menù "vivi" insieme.
            Menu.objects.exclude(pk=self.pk).filter(attivo=True).update(attivo=False)

    @classmethod
    def ottieni_attivo(cls):
        return cls.objects.filter(attivo=True).first()


class Categoria(models.Model):
    """Es. Antipasti, Primi, Secondi, Dolci, Vini... appartiene sempre a un
    Menù specifico. L'ordine di visualizzazione è liberamente modificabile
    dallo staff. La categoria è solo un raggruppamento: la scelta menù
    fisso/carta/sempre visibile si fa sul singolo Piatto, non qui (una stessa
    categoria "Primi" può contenere sia piatti del menù fisso sia piatti
    disponibili solo alla carta)."""

    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="categorie", verbose_name="Menù"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome categoria")
    ordine = models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")
    richiede_cucina = models.BooleanField(
        default=True,
        verbose_name="Richiede cucina",
        help_text=(
            "Spegnilo per categorie come Vini/Bibite/Caffè: i piatti dentro non "
            "passeranno mai dalla vista Cucina, ma da una sezione 'In attesa BAR' "
            "direttamente sulla pagina del tavolo."
        ),
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"
        ordering = ["menu", "ordine", "nome"]

    def __str__(self):
        return f"{self.nome} ({self.menu.nome})"


class ImpostazioniMenu(models.Model):
    """Riga unica per le impostazioni GENERALI del locale, valide per tutti i
    menù (non per una singola edizione: quelle sono su Menu)."""

    ordini_qr_abilitati = models.BooleanField(
        default=False,
        verbose_name="Permetti ordini dal QR",
        help_text=(
            "Se spento (consigliato per iniziare), chi scansiona il QR del tavolo vede "
            "solo il menù/la carta, senza poter ordinare. Il conto lo gestisce solo lo staff."
        ),
    )
    soglia_ritardo_cucina_minuti = models.PositiveIntegerField(
        default=15,
        verbose_name="Dopo quanti minuti un piatto è 'in ritardo'",
        help_text=(
            "In Cucina, un piatto in attesa da più di questi minuti viene evidenziato "
            "in rosso. Alzalo se durante il servizio l'allarme scatta troppo spesso."
        ),
    )
    coperto_attivo = models.BooleanField(
        default=False,
        verbose_name="Applica il coperto",
        help_text=(
            "Nel menù fisso il coperto non si aggiunge mai come voce a parte (si "
            "considera già incluso nel prezzo). Nella carta e in 'Entrambi visibili', "
            "se acceso, si aggiunge come voce separata nel conto."
        ),
    )
    prezzo_coperto = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Coperto a persona (EUR)",
        help_text="Unico per tutti i menù, non cambia da un'edizione all'altra.",
    )

    class Meta:
        verbose_name = "Impostazioni generali"
        verbose_name_plural = "Impostazioni generali"

    def __str__(self):
        return "Impostazioni generali del locale"

    @classmethod
    def ottieni(cls):
        obj, _creato = cls.objects.get_or_create(pk=1)
        return obj


class Piatto(models.Model):
    """Un piatto (o vino/bevanda), sempre dentro una Categoria (e quindi
    dentro un Menù). La scelta se fa parte del menù fisso, della carta, o se
    è sempre visibile, si fa qui: due piatti della stessa Categoria (es.
    entrambi "Primi") possono avere un Tipo di menù diverso."""

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
        """Restituisce i piatti disponibili da mostrare ora, del Menù
        ATTIVO: quelli del tipo di menù attualmente attivo (fisso o carta),
        più quelli sempre visibili (es. vini/bevande). Se la modalità del
        menù attivo è 'entrambi', li restituisce tutti. Se non c'è nessun
        menù attivo, non restituisce nulla."""
        menu_attivo = Menu.ottieni_attivo()
        if menu_attivo is None:
            return cls.objects.none()
        qs = cls.objects.filter(disponibile=True, categoria__menu=menu_attivo)
        if menu_attivo.modalita_attiva == Menu.MODALITA_ENTRAMBI:
            return qs
        return qs.filter(
            models.Q(tipo_menu=menu_attivo.modalita_attiva) | models.Q(tipo_menu=cls.TIPO_SEMPRE)
        )
