from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0007_rigaordine_stato_bozza"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordine",
            name="prezzo_menu_fisso_applicato",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text=(
                    "Congelato all'apertura del tavolo: se il prezzo del menù fisso viene "
                    "cambiato a metà servizio, i conti già aperti non cambiano."
                ),
                max_digits=6,
                null=True,
                verbose_name="Prezzo menù fisso applicato",
            ),
        ),
        migrations.AddField(
            model_name="rigaordine",
            name="inviata_il",
            field=models.DateTimeField(
                blank=True,
                help_text="Da qui parte il conteggio del tempo di attesa mostrato alla cucina.",
                null=True,
                verbose_name="Inviata in cucina il",
            ),
        ),
    ]
