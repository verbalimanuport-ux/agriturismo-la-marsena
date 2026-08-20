from django.db import migrations, models


def converti_entrambi_in_carta(apps, schema_editor):
    Menu = apps.get_model("menu_digitale", "Menu")
    Menu.objects.filter(modalita_attiva="entrambi").update(modalita_attiva="carta")


def nessuna_azione_indietro(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0017_rimuovi_piattomenu"),
    ]

    operations = [
        migrations.RunPython(converti_entrambi_in_carta, nessuna_azione_indietro),
        migrations.AlterField(
            model_name="menu",
            name="modalita_attiva",
            field=models.CharField(
                choices=[("fisso", "Solo menù fisso"), ("carta", "Solo carta")],
                default="fisso",
                help_text="Decide come vengono trattati TUTTI i piatti che metti in questo menù.",
                max_length=10,
                verbose_name="Modalità",
            ),
        ),
        migrations.AddField(
            model_name="categoria",
            name="ruolo",
            field=models.CharField(
                choices=[
                    ("portata", "Portata (nel menù principale)"),
                    ("vini", "Vini"),
                    ("dolci", "Dolci"),
                    ("bevande", "Bevande (incl. caffè e digestivi)"),
                ],
                default="portata",
                help_text=(
                    "Decide DOVE compare questa categoria nel menù pubblico: 'Portata' resta "
                    "nella pagina principale, le altre tre finiscono ciascuna nella propria "
                    "pagina dedicata (raggiungibile con un pulsante). Puoi avere più categorie "
                    "con lo stesso ruolo (es. 'Vini Rossi', 'Vini Bianchi', 'Vini Bollicine' "
                    "tutte con ruolo Vini): compariranno insieme, ciascuna con il proprio titolo."
                ),
                max_length=10,
                verbose_name="Ruolo nel menù",
            ),
        ),
        migrations.AddField(
            model_name="menu",
            name="menu_bambini_attivo",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Ha effetto solo quando la modalità è 'Solo menù fisso' (acceso di "
                    "default: spegnilo per questa edizione se non vuoi offrirlo)."
                ),
                verbose_name="Menù bambini attivo",
            ),
        ),
        migrations.AddField(
            model_name="menu",
            name="prezzo_menu_bambini_a_persona",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=6, verbose_name="Prezzo menù bambini a persona (EUR)"
            ),
        ),
        migrations.AddField(
            model_name="menu",
            name="piatti_bambini",
            field=models.ManyToManyField(
                blank=True,
                help_text="I piatti dedicati al menù bambini di questa edizione (un percorso a parte).",
                related_name="menus_bambini",
                to="menu_digitale.piatto",
                verbose_name="Piatti del menù bambini",
            ),
        ),
    ]
