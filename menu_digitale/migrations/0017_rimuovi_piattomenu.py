from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0016_popola_nuovo_collegamento"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="piatto",
            name="menus",
        ),
        migrations.RemoveField(
            model_name="piattomenu",
            name="menu",
        ),
        migrations.RemoveField(
            model_name="piattomenu",
            name="piatto",
        ),
        migrations.DeleteModel(
            name="PiattoMenu",
        ),
    ]
