from django.db import migrations


def popola_nuovo_collegamento(apps, schema_editor):
    PiattoMenu = apps.get_model("menu_digitale", "PiattoMenu")
    Categoria = apps.get_model("menu_digitale", "Categoria")
    Menu = apps.get_model("menu_digitale", "Menu")

    # Ogni vecchio collegamento piatto+menu (a prescindere dal tipo che
    # aveva) diventa una semplice presenza nel nuovo elenco "piatti" del menu.
    for collegamento in PiattoMenu.objects.select_related("piatto", "menu").all():
        collegamento.menu.piatti.add(collegamento.piatto)

    # Le categorie che avevano ALMENO un piatto marcato "sempre" (vini,
    # bibite, caffè...) diventano "sempre a parte" anche nel nuovo sistema.
    id_categorie_sempre = set(
        PiattoMenu.objects.filter(tipo_menu="sempre")
        .select_related("piatto")
        .values_list("piatto__categoria_id", flat=True)
    )
    Categoria.objects.filter(id__in=id_categorie_sempre).update(sempre_a_parte=True)


def nessuna_azione_indietro(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0015_semplifica_piatti_menu"),
    ]

    operations = [
        migrations.RunPython(popola_nuovo_collegamento, nessuna_azione_indietro),
    ]
