from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0015_rigaordine_tipo_menu_applicato"),
        ("menu_digitale", "0013_popola_piattomenu"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rigaordine",
            name="tipo_menu_applicato",
        ),
    ]
