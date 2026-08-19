from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0014_rimuovi_vecchi_campi_menu"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoria",
            name="sempre_a_parte",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Spegnilo... anzi accendilo per categorie come Vini/Bibite/Caffè: anche in "
                    "un menù fisso, i piatti di questa categoria si pagano sempre a parte "
                    "invece di essere inclusi nel prezzo a persona."
                ),
                verbose_name="Sempre a prezzo singolo (anche nel menù fisso)",
            ),
        ),
        migrations.AddField(
            model_name="menu",
            name="piatti",
            field=models.ManyToManyField(
                blank=True,
                help_text="Spunta i piatti che vuoi far comparire in questa edizione.",
                related_name="menus",
                to="menu_digitale.piatto",
                verbose_name="Piatti in questo menù",
            ),
        ),
    ]
