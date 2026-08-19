from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0012_remove_rigaordine_step"),
    ]

    operations = [
        migrations.AddField(
            model_name="rigaordine",
            name="servita_il",
            field=models.DateTimeField(
                blank=True,
                help_text="Usato per mostrare per qualche minuto il colore 'appena servito' in Sala.",
                null=True,
                verbose_name="Servita il",
            ),
        ),
    ]
