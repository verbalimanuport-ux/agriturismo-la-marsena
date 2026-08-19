from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0016_remove_tipo_menu_applicato"),
    ]

    operations = [
        migrations.AddField(
            model_name="rigaordine",
            name="extra_a_pagamento",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Aggiunto dal pulsante 'Extra (a pagamento)': si paga sempre a parte, "
                    "anche se il resto del tavolo è a menù fisso (es. una seconda Panna "
                    "Cotta oltre a quella già inclusa)."
                ),
                verbose_name="Extra a pagamento",
            ),
        ),
    ]
