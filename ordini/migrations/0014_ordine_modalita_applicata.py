import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0013_rigaordine_servita_il"),
        ("menu_digitale", "0011_finalizza_menu_multipli"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordine",
            name="modalita_applicata",
            field=models.CharField(
                blank=True,
                choices=[
                    ("fisso", "Solo menù fisso"),
                    ("carta", "Solo carta"),
                    ("entrambi", "Entrambi visibili"),
                ],
                help_text=(
                    "Congelata all'apertura del tavolo, come il prezzo: se lo staff cambia "
                    "il menù attivo a metà servizio, i conti già aperti non cambiano modalità."
                ),
                max_length=10,
                null=True,
                verbose_name="Modalità applicata",
            ),
        ),
        migrations.AddField(
            model_name="ordine",
            name="menu_applicato",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Il menù che era attivo quando il tavolo è stato aperto — usato per "
                    "generare le portate del fisso anche se nel frattempo cambia il menù attivo."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="menu_digitale.menu",
                verbose_name="Menù applicato",
            ),
        ),
    ]
