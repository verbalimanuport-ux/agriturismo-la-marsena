from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0013_popola_piattomenu"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="categoria",
            name="menu",
        ),
        migrations.AlterModelOptions(
            name="categoria",
            options={"ordering": ["ordine", "nome"], "verbose_name": "Categoria", "verbose_name_plural": "Categorie"},
        ),
        migrations.RemoveField(
            model_name="piatto",
            name="tipo_menu",
        ),
        migrations.AddField(
            model_name="piatto",
            name="menus",
            field=models.ManyToManyField(
                blank=True,
                related_name="piatti",
                through="menu_digitale.PiattoMenu",
                to="menu_digitale.menu",
                verbose_name="Presente nei menù",
            ),
        ),
    ]
