from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0007_categoria_richiede_cucina"),
    ]

    operations = [
        migrations.AddField(
            model_name="impostazionimenu",
            name="soglia_ritardo_cucina_minuti",
            field=models.PositiveIntegerField(
                default=15,
                help_text=(
                    "In Cucina, un piatto in attesa da più di questi minuti viene "
                    "evidenziato in rosso. Alzalo se durante il servizio l'allarme "
                    "scatta troppo spesso."
                ),
                verbose_name="Dopo quanti minuti un piatto è 'in ritardo'",
            ),
        ),
    ]
