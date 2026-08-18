from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0008_prezzo_congelato_e_inviata_il"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordine",
            name="volte_riaperto",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Quante volte questo conto è stato riaperto dopo una chiusura.",
                verbose_name="Volte riaperto",
            ),
        ),
    ]
