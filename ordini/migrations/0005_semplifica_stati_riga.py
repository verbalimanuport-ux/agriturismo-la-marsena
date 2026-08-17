from django.db import migrations, models


def converti_in_preparazione_in_attesa(apps, schema_editor):
    RigaOrdine = apps.get_model("ordini", "RigaOrdine")
    RigaOrdine.objects.filter(stato="in_preparazione").update(stato="in_attesa")


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0004_rigaordine_portata"),
    ]

    operations = [
        migrations.RunPython(converti_in_preparazione_in_attesa, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="rigaordine",
            name="stato",
            field=models.CharField(
                choices=[
                    ("in_attesa", "In cucina"),
                    ("pronto", "Pronto"),
                    ("servito", "Servito"),
                ],
                default="in_attesa",
                max_length=20,
                verbose_name="Stato preparazione",
            ),
        ),
    ]
