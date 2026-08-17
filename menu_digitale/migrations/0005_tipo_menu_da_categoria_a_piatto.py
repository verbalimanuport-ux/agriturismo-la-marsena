from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0004_categoria_tipo_menu_sempre"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="categoria",
            name="tipo_menu",
        ),
        migrations.AddField(
            model_name="piatto",
            name="tipo_menu",
            field=models.CharField(
                choices=[
                    ("fisso", "Menù fisso"),
                    ("carta", "Carta (à la carte)"),
                    ("sempre", "Sempre visibile (es. vini/bevande)"),
                ],
                default="carta",
                max_length=10,
                verbose_name="Tipo di menù",
            ),
        ),
    ]
