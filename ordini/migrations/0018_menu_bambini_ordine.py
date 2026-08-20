from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0017_rigaordine_extra_a_pagamento"),
        ("menu_digitale", "0018_ruolo_categoria_menu_bambini"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordine",
            name="numero_bambini",
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    "Quanti dei coperti mangiano dal menù bambini (prezzo dedicato, portate "
                    "dedicate) — visibile solo quando il menù attivo ha il menù bambini acceso."
                ),
                verbose_name="Di cui a menù bambini",
            ),
        ),
        migrations.AddField(
            model_name="ordine",
            name="prezzo_menu_bambini_applicato",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Congelato all'apertura del tavolo, come il prezzo del menù adulti.",
                max_digits=6,
                null=True,
                verbose_name="Prezzo menù bambini applicato",
            ),
        ),
        migrations.AlterField(
            model_name="ordine",
            name="modalita_applicata",
            field=models.CharField(
                blank=True,
                choices=[("fisso", "Solo menù fisso"), ("carta", "Solo carta")],
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
            model_name="rigaordine",
            name="per_bambini",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Generato dal menù bambini dell'edizione attiva: conteggiato al prezzo "
                    "bambini, non a quello adulti."
                ),
                verbose_name="Piatto del menù bambini",
            ),
        ),
    ]
