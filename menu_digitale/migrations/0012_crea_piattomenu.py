import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0011_finalizza_menu_multipli"),
    ]

    operations = [
        migrations.CreateModel(
            name="PiattoMenu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tipo_menu",
                    models.CharField(
                        choices=[
                            ("fisso", "Menù fisso"),
                            ("carta", "Carta (à la carte)"),
                            ("sempre", "Sempre visibile (es. vini/bevande)"),
                        ],
                        default="carta",
                        max_length=10,
                        verbose_name="Tipo in questo menù",
                    ),
                ),
                (
                    "menu",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="presenze_piatti",
                        to="menu_digitale.menu",
                        verbose_name="Menù",
                    ),
                ),
                (
                    "piatto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="presenze",
                        to="menu_digitale.piatto",
                        verbose_name="Piatto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Presenza piatto nel menù",
                "verbose_name_plural": "Presenze piatti nei menù",
            },
        ),
        migrations.AddConstraint(
            model_name="piattomenu",
            constraint=models.UniqueConstraint(fields=("piatto", "menu"), name="unico_piatto_per_menu"),
        ),
    ]
