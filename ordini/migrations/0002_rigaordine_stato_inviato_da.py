from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ordini", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rigaordine",
            name="stato",
            field=models.CharField(
                choices=[
                    ("in_attesa", "In attesa"),
                    ("in_preparazione", "In preparazione"),
                    ("pronto", "Pronto"),
                    ("servito", "Servito"),
                ],
                default="in_attesa",
                max_length=20,
                verbose_name="Stato preparazione",
            ),
        ),
        migrations.AddField(
            model_name="rigaordine",
            name="inviato_da",
            field=models.ForeignKey(
                blank=True,
                help_text="Chi ha inviato l'ordine in cucina (vuoto se aggiunto dal cliente via QR).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Cameriere",
            ),
        ),
    ]
