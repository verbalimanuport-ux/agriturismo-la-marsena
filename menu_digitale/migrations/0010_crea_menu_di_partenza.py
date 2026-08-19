from django.db import migrations


def crea_menu_di_partenza(apps, schema_editor):
    Menu = apps.get_model("menu_digitale", "Menu")
    Categoria = apps.get_model("menu_digitale", "Categoria")
    ImpostazioniMenu = apps.get_model("menu_digitale", "ImpostazioniMenu")

    # Recupera la modalità/prezzo che c'erano prima (se esistevano), così il
    # menù di partenza si comporta esattamente come il menù "unico" di prima.
    vecchie_impostazioni = ImpostazioniMenu.objects.first()
    modalita = getattr(vecchie_impostazioni, "modalita_attiva", "fisso") if vecchie_impostazioni else "fisso"
    prezzo = (
        getattr(vecchie_impostazioni, "prezzo_menu_fisso_a_persona", 0) if vecchie_impostazioni else 0
    )

    menu_partenza = Menu.objects.create(
        nome="Menù Principale",
        attivo=True,
        modalita_attiva=modalita,
        prezzo_menu_fisso_a_persona=prezzo,
    )
    Categoria.objects.filter(menu__isnull=True).update(menu=menu_partenza)


def svuota_menu_di_partenza(apps, schema_editor):
    # Non annulliamo: se si torna indietro, il campo verrà comunque rimosso
    # dalla migrazione precedente. Nessuna azione necessaria qui.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0009_menu_categoria_menu"),
    ]

    operations = [
        migrations.RunPython(crea_menu_di_partenza, svuota_menu_di_partenza),
    ]
