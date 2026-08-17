from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prenotazioni", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prenotazione",
            name="stato",
            field=models.CharField(
                choices=[
                    ("in_attesa", "In attesa di conferma"),
                    ("confermata", "Confermata"),
                    ("arrivata", "Arrivata"),
                    ("annullata", "Annullata"),
                ],
                default="in_attesa",
                max_length=20,
                verbose_name="Stato",
            ),
        ),
    ]
