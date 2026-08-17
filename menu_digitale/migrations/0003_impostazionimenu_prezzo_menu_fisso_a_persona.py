from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0002_categoria_tipo_menu_impostazionimenu"),
    ]

    operations = [
        migrations.AddField(
            model_name="impostazionimenu",
            name="prezzo_menu_fisso_a_persona",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Usato per calcolare il conto quando il tavolo ordina dal menù fisso.",
                max_digits=6,
                verbose_name="Prezzo menù fisso a persona (EUR)",
            ),
        ),
    ]
