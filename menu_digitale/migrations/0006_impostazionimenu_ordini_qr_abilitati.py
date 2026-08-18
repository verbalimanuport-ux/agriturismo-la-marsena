from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0005_tipo_menu_da_categoria_a_piatto"),
    ]

    operations = [
        migrations.AddField(
            model_name="impostazionimenu",
            name="ordini_qr_abilitati",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Se spento (consigliato per iniziare), chi scansiona il QR del tavolo "
                    "vede solo il menù/la carta, senza poter ordinare. Il conto lo gestisce "
                    "solo lo staff."
                ),
                verbose_name="Permetti ordini dal QR",
            ),
        ),
    ]
