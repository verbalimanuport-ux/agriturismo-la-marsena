from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoria",
            name="tipo_menu",
            field=models.CharField(
                choices=[("fisso", "Menù fisso"), ("carta", "Carta (à la carte)")],
                default="carta",
                max_length=10,
                verbose_name="Tipo di menù",
            ),
        ),
        migrations.CreateModel(
            name="ImpostazioniMenu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "modalita_attiva",
                    models.CharField(
                        choices=[
                            ("fisso", "Solo menù fisso"),
                            ("carta", "Solo carta"),
                            ("entrambi", "Entrambi visibili"),
                        ],
                        default="fisso",
                        max_length=10,
                        verbose_name="Cosa mostrare ai clienti ora",
                    ),
                ),
            ],
            options={
                "verbose_name": "Impostazioni menù",
                "verbose_name_plural": "Impostazioni menù",
            },
        ),
    ]
