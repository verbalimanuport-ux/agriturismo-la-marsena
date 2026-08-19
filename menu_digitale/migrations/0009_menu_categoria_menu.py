import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0008_soglia_ritardo_cucina"),
    ]

    operations = [
        migrations.CreateModel(
            name="Menu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=150, verbose_name="Nome del menù")),
                (
                    "descrizione",
                    models.TextField(
                        blank=True,
                        help_text="Testo mostrato ai clienti nella pagina pubblica dei menù.",
                        verbose_name="Descrizione",
                    ),
                ),
                ("data_inizio", models.DateField(blank=True, null=True, verbose_name="Data inizio prevista")),
                ("data_fine", models.DateField(blank=True, null=True, verbose_name="Data fine prevista")),
                (
                    "attivo",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Solo un menù alla volta può essere attivo: attivandone uno, "
                            "quello che era attivo prima si spegne da solo."
                        ),
                        verbose_name="Attivo (in uso ora per il servizio)",
                    ),
                ),
                (
                    "modalita_attiva",
                    models.CharField(
                        choices=[
                            ("fisso", "Solo menù fisso"),
                            ("carta", "Solo carta"),
                            ("entrambi", "Entrambi visibili"),
                        ],
                        default="fisso",
                        max_length=10,
                        verbose_name="Modalità",
                    ),
                ),
                (
                    "prezzo_menu_fisso_a_persona",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Usato per calcolare il conto quando il tavolo ordina dal menù fisso.",
                        max_digits=6,
                        verbose_name="Prezzo menù fisso a persona (EUR)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Menù",
                "verbose_name_plural": "Menù",
                "ordering": ["-attivo", "-data_inizio", "nome"],
            },
        ),
        migrations.AddField(
            model_name="categoria",
            name="menu",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="categorie",
                to="menu_digitale.menu",
                verbose_name="Menù",
            ),
        ),
    ]
