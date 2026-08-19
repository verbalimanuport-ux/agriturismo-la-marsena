from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0010_rigaordine_stato_previsto"),
    ]

    operations = [
        migrations.AddField(
            model_name="rigaordine",
            name="step",
            field=models.PositiveIntegerField(
                default=1,
                help_text=(
                    "Per menù degustazione: quando lo stesso giro ha più portate in "
                    "sequenza per la stessa persona (es. due secondi diversi), usa "
                    "step differenti (1, 2, 3...) per chiamarli in cucina uno alla "
                    "volta. Lascia 1 per i giri normali, senza sequenza — il caso di "
                    "quasi tutti i piatti."
                ),
                verbose_name="Sotto-passo del giro",
            ),
        ),
    ]
