from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0014_ordine_modalita_applicata"),
    ]

    operations = [
        migrations.AddField(
            model_name="rigaordine",
            name="tipo_menu_applicato",
            field=models.CharField(
                choices=[
                    ("fisso", "Menù fisso"),
                    ("carta", "Carta (à la carte)"),
                    ("sempre", "Sempre visibile (es. vini/bevande)"),
                ],
                default="carta",
                help_text=(
                    "Congelato quando il piatto è stato aggiunto al conto (lo stesso piatto "
                    "può essere 'fisso' in un menù e 'carta' in un altro): se cambia dopo, "
                    "questo conto non cambia."
                ),
                max_length=10,
                verbose_name="Tipo di menù applicato",
            ),
        ),
    ]
