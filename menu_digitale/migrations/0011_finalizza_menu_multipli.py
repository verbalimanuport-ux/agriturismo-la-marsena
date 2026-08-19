import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0010_crea_menu_di_partenza"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categoria",
            name="menu",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="categorie",
                to="menu_digitale.menu",
                verbose_name="Menù",
            ),
        ),
        migrations.AlterModelOptions(
            name="categoria",
            options={"ordering": ["menu", "ordine", "nome"], "verbose_name": "Categoria", "verbose_name_plural": "Categorie"},
        ),
        migrations.RemoveField(
            model_name="impostazionimenu",
            name="modalita_attiva",
        ),
        migrations.RemoveField(
            model_name="impostazionimenu",
            name="prezzo_menu_fisso_a_persona",
        ),
        migrations.AddField(
            model_name="impostazionimenu",
            name="coperto_attivo",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Nel menù fisso il coperto non si aggiunge mai come voce a parte (si "
                    "considera già incluso nel prezzo). Nella carta e in 'Entrambi visibili', "
                    "se acceso, si aggiunge come voce separata nel conto."
                ),
                verbose_name="Applica il coperto",
            ),
        ),
        migrations.AddField(
            model_name="impostazionimenu",
            name="prezzo_coperto",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Unico per tutti i menù, non cambia da un'edizione all'altra.",
                max_digits=6,
                verbose_name="Coperto a persona (EUR)",
            ),
        ),
        migrations.AlterModelOptions(
            name="impostazionimenu",
            options={"verbose_name": "Impostazioni generali", "verbose_name_plural": "Impostazioni generali"},
        ),
    ]
