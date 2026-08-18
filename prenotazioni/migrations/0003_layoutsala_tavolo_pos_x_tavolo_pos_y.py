from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prenotazioni", "0002_prenotazione_stato_arrivata"),
    ]

    operations = [
        migrations.AddField(
            model_name="tavolo",
            name="pos_x",
            field=models.FloatField(blank=True, null=True, verbose_name="Posizione X sulla mappa (%)"),
        ),
        migrations.AddField(
            model_name="tavolo",
            name="pos_y",
            field=models.FloatField(blank=True, null=True, verbose_name="Posizione Y sulla mappa (%)"),
        ),
        migrations.CreateModel(
            name="LayoutSala",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("perimetro_json", models.TextField(blank=True, default="[]", verbose_name="Perimetro (JSON)")),
            ],
            options={
                "verbose_name": "Layout sala",
                "verbose_name_plural": "Layout sala",
            },
        ),
    ]
