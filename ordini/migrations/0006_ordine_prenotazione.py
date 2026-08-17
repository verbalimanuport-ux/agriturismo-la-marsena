from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("prenotazioni", "0002_prenotazione_stato_arrivata"),
        ("ordini", "0005_semplifica_stati_riga"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordine",
            name="prenotazione",
            field=models.ForeignKey(
                blank=True,
                help_text="Se questo servizio nasce dall'assegnazione di una prenotazione.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ordini",
                to="prenotazioni.prenotazione",
                verbose_name="Prenotazione collegata",
            ),
        ),
    ]
