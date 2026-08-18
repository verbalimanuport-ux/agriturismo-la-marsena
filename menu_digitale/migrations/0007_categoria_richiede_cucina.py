from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0006_impostazionimenu_ordini_qr_abilitati"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoria",
            name="richiede_cucina",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Spegnilo per categorie come Vini/Bibite/Caffè: i piatti dentro non "
                    "passeranno mai dalla vista Cucina, ma da una sezione 'Da consegnare' "
                    "direttamente sulla pagina del tavolo."
                ),
                verbose_name="Richiede cucina",
            ),
        ),
    ]
