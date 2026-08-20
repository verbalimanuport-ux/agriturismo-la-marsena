from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prenotazioni", "0005_bambini_seggioloni"),
    ]

    operations = [
        migrations.AddField(
            model_name="tavolo",
            name="ruotato",
            field=models.BooleanField(
                default=False,
                help_text="Utile per un tavolo grande che deve stare posizionato di traverso rispetto agli altri.",
                verbose_name="Ruotato (verticale invece di orizzontale)",
            ),
        ),
    ]
