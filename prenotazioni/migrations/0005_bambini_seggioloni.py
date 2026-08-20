from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prenotazioni", "0004_prenotazione_stato_completata"),
    ]

    operations = [
        migrations.AddField(
            model_name="prenotazione",
            name="numero_bambini",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Utile alla sala per organizzarsi, a prescindere da quale menù sarà attivo quel giorno.",
                verbose_name="Di cui bambini",
            ),
        ),
        migrations.AddField(
            model_name="prenotazione",
            name="numero_seggioloni",
            field=models.PositiveIntegerField(default=0, verbose_name="Seggioloni richiesti"),
        ),
        migrations.AddField(
            model_name="prenotazione",
            name="bambini_menu_dedicato",
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text=(
                    "Da decidere alla telefonata di conferma (solo se quel giorno il menù "
                    "bambini è attivo): sì, no, o non ancora deciso."
                ),
                null=True,
                verbose_name="Bambini al menù dedicato?",
            ),
        ),
    ]
