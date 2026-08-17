from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0002_rigaordine_stato_inviato_da"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordine",
            name="numero_coperti",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Persone al tavolo: usato per calcolare il conto del menù fisso.",
                verbose_name="Numero coperti",
            ),
        ),
    ]
