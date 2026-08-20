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
    MODALITA_CHOICES = [
        (MODALITA_FISSO, "Solo menù fisso"),
        (MODALITA_CARTA, "Solo carta"),
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
        help_text="Decide come vengono trattati TUTTI i piatti che metti in questo menù.",
    )
    prezzo_menu_fisso_a_persona = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Prezzo menù fisso a persona (EUR)",
        help_text="Usato per calcolare il conto quando il tavolo ordina dal menù fisso.",
    )
    piatti = models.ManyToManyField(
        "Piatto",
        blank=True,
        related_name="menus",
        verbose_name="Piatti in questo menù",
        help_text="Spunta i piatti che vuoi far comparire in questa edizione.",
    )
    menu_bambini_attivo = models.BooleanField(
        default=True,
        verbose_name="Menù bambini attivo",
        help_text=(
            "Ha effetto solo quando la modalità è 'Solo menù fisso' (acceso di default: "
            "spegnilo per questa edizione se non vuoi offrirlo)."
        ),
    )
    prezzo_menu_bambini_a_persona = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Prezzo menù bambini a persona (EUR)",
    )
    piatti_bambini = models.ManyToManyField(
        "Piatto",
        blank=True,
        related_name="menus_bambini",
        verbose_name="Piatti del menù bambini",
        help_text="I piatti dedicati al menù bambini di questa edizione (un percorso a parte).",
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

    @property
    def bambini_disponibile(self):
        """Il menù bambini è davvero utilizzabile solo se attivo E siamo in
        modalità 'Solo menù fisso' (in carta non ha senso: un bambino
        ordina semplicemente quello che vuole dalla carta normale)."""
        return self.menu_bambini_attivo and self.modalita_attiva == self.MODALITA_FISSO


class Categoria(models.Model):
    """Es. Antipasti, Primi, Secondi, Dolci, Vini... CONDIVISA tra tutti i
    menù: la struttura (che categorie esistono) è sempre la stessa, non
    serve ricrearla per ogni nuova edizione — cambiano solo i piatti dentro."""

    RUOLO_PORTATA = "portata"
    RUOLO_VINI = "vini"
    RUOLO_DOLCI = "dolci"
    RUOLO_BEVANDE = "bevande"
    RUOLO_CHOICES = [
        (RUOLO_PORTATA, "Portata (nel menù principale)"),
        (RUOLO_VINI, "Vini"),
        (RUOLO_DOLCI, "Dolci"),
        (RUOLO_BEVANDE, "Bevande (incl. caffè e digestivi)"),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome categoria")
    ordine = models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")
    ruolo = models.CharField(
        max_length=10,
        choices=RUOLO_CHOICES,
        default=RUOLO_PORTATA,
        verbose_name="Ruolo nel menù",
        help_text=(
            "Decide DOVE compare questa categoria nel menù pubblico: 'Portata' resta nella "
            "pagina principale, le altre tre finiscono ciascuna nella propria pagina dedicata "
            "(raggiungibile con un pulsante). Puoi avere più categorie con lo stesso ruolo "
            "(es. 'Vini Rossi', 'Vini Bianchi', 'Vini Bollicine' tutte con ruolo Vini): "
            "compariranno insieme, ciascuna con il proprio titolo."
        ),
    )
    richiede_cucina = models.BooleanField(
        default=True,
        verbose_name="Richiede cucina",
        help_text=(
            "Spegnilo per categorie come Vini/Bibite/Caffè: i piatti dentro non "
            "passeranno mai dalla vista Cucina, ma da una sezione 'In attesa BAR' "
            "direttamente sulla pagina del tavolo."
        ),
    )
    sempre_a_parte = models.BooleanField(
        default=False,
        verbose_name="Sempre a prezzo singolo (anche nel menù fisso)",
        help_text=(
            "Spegnilo... anzi accendilo per categorie come Vini/Bibite/Caffè: anche in un "
            "menù fisso, i piatti di questa categoria si pagano sempre a parte invece di "
            "essere inclusi nel prezzo a persona."
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
            "considera già incluso nel prezzo). Nella carta, se acceso, si aggiunge "
            "come voce separata nel conto."
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
    compare in più edizioni. In QUALI menù compare si decide con una
    semplice spunta (dalla scheda del Menù, o da qui): nessun "tipo" da
    scegliere piatto per piatto — lo eredita in automatico dalla modalità
    del menù in cui lo metti (fisso o carta), tranne per le categorie
    marcate "sempre a parte" (es. Vini), che restano a prezzo singolo in
    ogni caso."""

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

    class Meta:
        verbose_name = "Piatto"
        verbose_name_plural = "Piatti"
        ordering = ["categoria__ordine", "ordine", "nome"]

    def __str__(self):
        return f"{self.nome} - EUR {self.prezzo}"

    @classmethod
    def attivi(cls, solo_sempre_a_parte=False):
        """I piatti disponibili da mostrare ora: quelli spuntati per il Menù
        ATTIVO, PIÙ tutti quelli di categorie "sempre a prezzo singolo"
        (Vini, Bibite, Caffè...) — questi ultimi compaiono SEMPRE, in ogni
        edizione, senza bisogno di spuntarli menù per menù: l'unico modo di
        toglierli è segnarli "Non disponibile" sul singolo piatto. Se
        `solo_sempre_a_parte` è True, restituisce solo questi ultimi (usato
        per far ordinare al cliente da QR solo gli extra, quando il resto
        del menù fisso è già generato in automatico)."""
        if solo_sempre_a_parte:
            return cls.objects.filter(disponibile=True, categoria__sempre_a_parte=True)
        menu_attivo = Menu.ottieni_attivo()
        sempre_a_parte = models.Q(disponibile=True, categoria__sempre_a_parte=True)
        if menu_attivo is None:
            return cls.objects.filter(sempre_a_parte)
        nel_menu = models.Q(disponibile=True, menus=menu_attivo)
        return cls.objects.filter(sempre_a_parte | nel_menu).distinct()


def _piatti_per_menu_e_ruolo(menu, ruolo):
    """Piatti da mostrare per un dato Menù, filtrati alle categorie con
    QUESTO ruolo (Portata/Vini/Dolci/Bevande): quelli spuntati per il menù,
    PIÙ quelli di categorie "sempre a prezzo singolo", che compaiono
    automaticamente in ogni edizione senza bisogno di spuntarli."""
    sempre_a_parte = models.Q(disponibile=True, categoria__sempre_a_parte=True, categoria__ruolo=ruolo)
    if menu is None:
        return Piatto.objects.filter(sempre_a_parte).select_related("categoria")
    nel_menu = models.Q(disponibile=True, menus=menu, categoria__ruolo=ruolo)
    return Piatto.objects.filter(sempre_a_parte | nel_menu).distinct().select_related("categoria")


def _raggruppa_per_categoria(piatti):
    """Da un elenco di piatti, le rispettive categorie ciascuna con
    l'elenco dei suoi piatti nell'attributo `piatti_attivi`."""
    mappa = {}
    for piatto in piatti:
        voce = mappa.setdefault(piatto.categoria_id, {"categoria": piatto.categoria, "piatti": []})
        voce["piatti"].append(piatto)
    categorie = []
    for voce in mappa.values():
        voce["categoria"].piatti_attivi = sorted(voce["piatti"], key=lambda p: (p.ordine, p.nome))
        categorie.append(voce["categoria"])
    categorie.sort(key=lambda c: (c.ordine, c.nome))
    return categorie


def categorie_con_piatti_per_menu(menu):
    """Le categorie PORTATA (il menù principale — antipasti, primi,
    secondi...) con almeno un piatto da mostrare per QUESTO menù. Usata sia
    dal menù pubblico sia dalla pagina QR in sola consultazione, per non
    ripetere la stessa logica due volte."""
    return _raggruppa_per_categoria(_piatti_per_menu_e_ruolo(menu, Categoria.RUOLO_PORTATA))


def categorie_per_ruolo(menu, ruolo):
    """Le categorie di un ruolo specifico (Vini/Dolci/Bevande) per la loro
    pagina pubblica dedicata."""
    return _raggruppa_per_categoria(_piatti_per_menu_e_ruolo(menu, ruolo))


def piatti_bambini_per_menu(menu):
    """I piatti del menù bambini di questa edizione, SOLO se il menù
    bambini è davvero disponibile ora (acceso E modalità fisso) —
    altrimenti lista vuota, così il menù pubblico non deve controllare
    tutte le condizioni ogni volta."""
    if menu is None or not menu.bambini_disponibile:
        return []
    return list(
        menu.piatti_bambini.filter(disponibile=True)
        .select_related("categoria")
        .order_by("categoria__ordine", "ordine", "nome")
    )
