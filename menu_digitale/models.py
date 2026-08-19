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
    """Es. Antipasti, Primi, Secondi, Dolci, Vini... CONDIVISA tra tutti i
    menù: la struttura (che categorie esistono) è sempre la stessa, non
    serve ricrearla per ogni nuova edizione — cambiano solo i piatti dentro.
    Se un'edizione non ha piatti in una categoria, semplicemente quella
    categoria non compare per quell'edizione."""

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
        ordering = ["ordine", "nome"]

    def __str__(self):
        return self.nome


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
    """Un piatto (o vino/bevanda). Nome, descrizione, prezzo, foto sono
    UNICI — non cambiano mai da un menù all'altro, anche se lo stesso piatto
    compare in più edizioni. In QUALI menù compare, e con che "tipo"
    (fisso/carta/sempre) in ciascuno, si decide nella tabella PiattoMenu qui
    sotto: lo stesso piatto può essere 'fisso' in un'edizione e 'carta' in
    un'altra, restando un unico piatto con un unico prezzo."""

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
    allergeni = models.CharField(max_length=200, blank=True, verbose_name="Allergeni")
    immagine = models.ImageField(
        upload_to="piatti/", blank=True, null=True, verbose_name="Foto piatto"
    )
    disponibile = models.BooleanField(default=True, verbose_name="Disponibile")
    ordine = models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")
    menus = models.ManyToManyField(
        Menu,
        through="PiattoMenu",
        related_name="piatti",
        verbose_name="Presente nei menù",
        blank=True,
    )

    class Meta:
        verbose_name = "Piatto"
        verbose_name_plural = "Piatti"
        ordering = ["categoria__ordine", "ordine", "nome"]

    def __str__(self):
        return f"{self.nome} - EUR {self.prezzo}"

    @classmethod
    def attivi(cls, solo_tipo=None):
        """Restituisce (come QuerySet vero, utilizzabile in form/Prefetch)
        i piatti disponibili da mostrare ora, del Menù ATTIVO: quelli del
        tipo di menù attualmente attivo (fisso o carta), più quelli sempre
        visibili (es. vini/bevande) — salvo che si chieda esplicitamente
        solo un tipo con `solo_tipo`. Se la modalità del menù attivo è
        'entrambi', li restituisce tutti (a meno di `solo_tipo`). Se non
        c'è nessun menù attivo, non restituisce nulla."""
        menu_attivo = Menu.ottieni_attivo()
        if menu_attivo is None:
            return cls.objects.none()
        collegamenti = PiattoMenu.objects.filter(menu=menu_attivo, piatto__disponibile=True)
        if solo_tipo:
            collegamenti = collegamenti.filter(tipo_menu=solo_tipo)
        elif menu_attivo.modalita_attiva != Menu.MODALITA_ENTRAMBI:
            collegamenti = collegamenti.filter(
                models.Q(tipo_menu=menu_attivo.modalita_attiva) | models.Q(tipo_menu=cls.TIPO_SEMPRE)
            )
        id_piatti = collegamenti.values_list("piatto_id", flat=True)
        return cls.objects.filter(id__in=id_piatti, disponibile=True)


class PiattoMenu(models.Model):
    """Collega un Piatto a un Menù, con il "tipo" (fisso/carta/sempre) che
    ha SOLO in quella specifica edizione — lo stesso piatto può essere
    'fisso' nel Menù Principale e 'carta' nel Menù d'Inverno."""

    piatto = models.ForeignKey(
        Piatto, on_delete=models.CASCADE, related_name="presenze", verbose_name="Piatto"
    )
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="presenze_piatti", verbose_name="Menù"
    )
    tipo_menu = models.CharField(
        max_length=10,
        choices=Piatto.TIPO_CHOICES,
        default=Piatto.TIPO_CARTA,
        verbose_name="Tipo in questo menù",
    )

    class Meta:
        verbose_name = "Presenza piatto nel menù"
        verbose_name_plural = "Presenze piatti nei menù"
        constraints = [
            models.UniqueConstraint(fields=["piatto", "menu"], name="unico_piatto_per_menu")
        ]

    def __str__(self):
        return f"{self.piatto.nome} in {self.menu.nome} ({self.get_tipo_menu_display()})"


def categorie_con_piatti_per_menu(menu):
    """Le categorie che hanno almeno un piatto attivo in QUESTO menù,
    ciascuna con l'elenco dei suoi piatti (attributo `piatti_attivi`).
    Ogni piatto porta con sé il proprio `tipo_menu` PER QUESTA EDIZIONE
    (attributo Python dinamico, non salvato sul piatto — dipende dal menù,
    non è un campo fisso). Usata sia dal menù pubblico sia dalla pagina
    QR in sola consultazione, per non ripetere la stessa logica due volte."""
    if menu is None:
        return []
    collegamenti = PiattoMenu.objects.filter(
        menu=menu, piatto__disponibile=True
    ).select_related("piatto__categoria")
    if menu.modalita_attiva != Menu.MODALITA_ENTRAMBI:
        collegamenti = collegamenti.filter(
            models.Q(tipo_menu=menu.modalita_attiva) | models.Q(tipo_menu=Piatto.TIPO_SEMPRE)
        )
    mappa = {}
    for link in collegamenti:
        piatto = link.piatto
        piatto.tipo_menu = link.tipo_menu
        voce = mappa.setdefault(piatto.categoria_id, {"categoria": piatto.categoria, "piatti": []})
        voce["piatti"].append(piatto)
    categorie = []
    for voce in mappa.values():
        voce["categoria"].piatti_attivi = sorted(voce["piatti"], key=lambda p: (p.ordine, p.nome))
        categorie.append(voce["categoria"])
    categorie.sort(key=lambda c: (c.ordine, c.nome))
    return categorie
