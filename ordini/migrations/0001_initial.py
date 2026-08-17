from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("prenotazioni", "0001_initial"),
        ("menu_digitale", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ordine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stato", models.CharField(choices=[("aperto", "Aperto"), ("chiuso", "Chiuso")], default="aperto", max_length=10, verbose_name="Stato")),
                ("aperto_il", models.DateTimeField(auto_now_add=True, verbose_name="Aperto il")),
                ("chiuso_il", models.DateTimeField(blank=True, null=True, verbose_name="Chiuso il")),
                ("tavolo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ordini", to="prenotazioni.tavolo", verbose_name="Tavolo")),
            ],
            options={
                "verbose_name": "Ordine",
                "verbose_name_plural": "Ordini",
                "ordering": ["-aperto_il"],
            },
        ),
        migrations.CreateModel(
            name="RigaOrdine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantita", models.PositiveIntegerField(default=1, verbose_name="Quantità")),
                ("prezzo_unitario", models.DecimalField(decimal_places=2, help_text="Preso automaticamente dal prezzo del piatto al momento dell'ordine.", max_digits=6, verbose_name="Prezzo unitario")),
                ("origine", models.CharField(choices=[("cliente", "Cliente (QR)"), ("staff", "Staff")], default="staff", max_length=10, verbose_name="Aggiunto da")),
                ("note", models.CharField(blank=True, max_length=200, verbose_name="Note")),
                ("creata_il", models.DateTimeField(auto_now_add=True, verbose_name="Aggiunta il")),
                ("ordine", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="righe", to="ordini.ordine", verbose_name="Ordine")),
                ("piatto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="menu_digitale.piatto", verbose_name="Piatto/bevanda")),
            ],
            options={
                "verbose_name": "Riga ordine",
                "verbose_name_plural": "Righe ordine",
                "ordering": ["creata_il"],
            },
        ),
    ]
