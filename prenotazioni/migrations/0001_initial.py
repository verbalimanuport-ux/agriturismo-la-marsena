from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tavolo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero", models.CharField(max_length=10, unique=True, verbose_name="Numero tavolo")),
                ("capienza", models.PositiveIntegerField(verbose_name="Capienza (posti)")),
                ("zona", models.CharField(blank=True, max_length=100, verbose_name="Zona / sala")),
                ("attivo", models.BooleanField(default=True, verbose_name="Attivo (utilizzabile)")),
            ],
            options={
                "verbose_name": "Tavolo",
                "verbose_name_plural": "Tavoli",
                "ordering": ["numero"],
            },
        ),
        migrations.CreateModel(
            name="Prenotazione",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, verbose_name="Nome e cognome")),
                ("telefono", models.CharField(blank=True, max_length=30, verbose_name="Telefono")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                ("data", models.DateField(verbose_name="Data")),
                ("ora", models.TimeField(verbose_name="Ora")),
                ("numero_coperti", models.PositiveIntegerField(verbose_name="Numero persone")),
                ("note", models.TextField(blank=True, verbose_name="Note (allergie, richieste...)")),
                ("interesse_lezione_cavallo", models.BooleanField(default=False, verbose_name='Interessato a "battesimo della sella" (lezione a cavallo)')),
                ("stato", models.CharField(choices=[("in_attesa", "In attesa di conferma"), ("confermata", "Confermata"), ("annullata", "Annullata")], default="in_attesa", max_length=20, verbose_name="Stato")),
                ("creata_il", models.DateTimeField(auto_now_add=True, verbose_name="Ricevuta il")),
                ("tavolo", models.ForeignKey(blank=True, help_text="Da assegnare/modificare dallo staff.", null=True, on_delete=django.db.models.deletion.SET_NULL, to="prenotazioni.tavolo", verbose_name="Tavolo assegnato")),
            ],
            options={
                "verbose_name": "Prenotazione",
                "verbose_name_plural": "Prenotazioni",
                "ordering": ["data", "ora"],
            },
        ),
    ]
