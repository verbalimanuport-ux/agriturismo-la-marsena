from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0003_ordine_numero_coperti"),
    ]

    operations = [
        migrations.AddField(
            model_name="rigaordine",
            name="portata",
            field=models.PositiveIntegerField(
                default=1,
                help_text=(
                    "Piatti con lo stesso numero escono insieme dalla cucina. Calcolato "
                    "automaticamente dall'ordine della categoria, ma modificabile a mano "
                    "(es. un secondo che deve uscire insieme agli antipasti)."
                ),
                verbose_name="Giro d'uscita",
            ),
        ),
    ]
