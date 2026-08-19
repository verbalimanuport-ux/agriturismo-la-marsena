from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ordini", "0011_rigaordine_step"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rigaordine",
            name="step",
        ),
    ]
