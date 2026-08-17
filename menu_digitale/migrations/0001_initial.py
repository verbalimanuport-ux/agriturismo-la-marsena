from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Categoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, verbose_name="Nome categoria")),
                ("ordine", models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")),
            ],
            options={
                "verbose_name": "Categoria",
                "verbose_name_plural": "Categorie",
                "ordering": ["ordine", "nome"],
            },
        ),
        migrations.CreateModel(
            name="Piatto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=150, verbose_name="Nome piatto")),
                ("descrizione", models.TextField(blank=True, verbose_name="Descrizione")),
                ("prezzo", models.DecimalField(decimal_places=2, max_digits=6, verbose_name="Prezzo (EUR)")),
                ("allergeni", models.CharField(blank=True, max_length=200, verbose_name="Allergeni")),
                ("immagine", models.ImageField(blank=True, null=True, upload_to="piatti/", verbose_name="Foto piatto")),
                ("disponibile", models.BooleanField(default=True, verbose_name="Disponibile")),
                ("ordine", models.PositiveIntegerField(default=0, verbose_name="Ordine di visualizzazione")),
                ("categoria", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="piatti", to="menu_digitale.categoria", verbose_name="Categoria")),
            ],
            options={
                "verbose_name": "Piatto",
                "verbose_name_plural": "Piatti",
                "ordering": ["categoria__ordine", "ordine", "nome"],
            },
        ),
    ]
