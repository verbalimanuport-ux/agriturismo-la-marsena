from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0009_ordine_volte_riaperto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rigaordine",
            name="stato",
            field=models.CharField(
                choices=[
                    ("bozza", "Da inviare"),
                    ("previsto", "Previsto (in attesa del via libera)"),
                    ("in_attesa", "In cucina"),
                    ("pronto", "Pronto"),
                    ("servito", "Servito"),
                ],
                default="bozza",
                max_length=20,
                verbose_name="Stato preparazione",
            ),
        ),
    ]
