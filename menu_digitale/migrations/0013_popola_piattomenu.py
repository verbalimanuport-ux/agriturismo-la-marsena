from django.db import migrations


def popola_piattomenu_e_unisci_categorie(apps, schema_editor):
    Categoria = apps.get_model("menu_digitale", "Categoria")
    Piatto = apps.get_model("menu_digitale", "Piatto")
    PiattoMenu = apps.get_model("menu_digitale", "PiattoMenu")
    RigaOrdine = apps.get_model("ordini", "RigaOrdine")

    # PRIMA: per ogni piatto, registra in quale menù compariva (tramite la
    # sua categoria) e con che tipo — usando i dati COSÌ COME SONO ORA,
    # prima di toccare/rimuovere qualsiasi cosa.
    for piatto in Piatto.objects.select_related("categoria", "categoria__menu").all():
        menu_di_provenienza = piatto.categoria.menu
        if menu_di_provenienza is None:
            continue
        PiattoMenu.objects.get_or_create(
            piatto=piatto,
            menu=menu_di_provenienza,
            defaults={"tipo_menu": piatto.tipo_menu},
        )

    # Salva anche il tipo di ogni riga d'ordine GIÀ ESISTENTE (test fatti
    # finora), prima che il campo Piatto.tipo_menu sparisca — altrimenti i
    # conti già aperti perderebbero l'informazione "questo era fisso/carta".
    for riga in RigaOrdine.objects.select_related("piatto").all():
        RigaOrdine.objects.filter(pk=riga.pk).update(tipo_menu_applicato=riga.piatto.tipo_menu)

    # POI: le categorie ora sono condivise, quindi se esistevano più
    # categorie con lo stesso nome (una per ogni vecchio menù), le uniamo in
    # una sola — spostando tutti i piatti sulla superstite (la più vecchia).
    viste = {}
    for categoria in Categoria.objects.order_by("id"):
        chiave = categoria.nome.strip().lower()
        if chiave not in viste:
            viste[chiave] = categoria
            continue
        superstite = viste[chiave]
        Piatto.objects.filter(categoria=categoria).update(categoria=superstite)
        categoria.delete()


def nessuna_azione_indietro(apps, schema_editor):
    # Non c'è un modo sensato di tornare indietro (le categorie unite non si
    # possono "ri-separare" sapendo da quale menù venivano). Se serve fare
    # rollback, si riparte da un backup del database.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menu_digitale", "0012_crea_piattomenu"),
        ("ordini", "0015_rigaordine_tipo_menu_applicato"),
    ]

    operations = [
        migrations.RunPython(popola_piattomenu_e_unisci_categorie, nessuna_azione_indietro),
    ]
