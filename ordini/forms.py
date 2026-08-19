from django import forms

from menu_digitale.models import Piatto


class AggiungiPiattoForm(forms.Form):
    piatto = forms.ModelChoiceField(
        queryset=Piatto.objects.none(),
        label="Piatto / bevanda",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantita = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Quantità",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    note = forms.CharField(
        required=False,
        label="Note",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "es. senza cipolla"}),
    )

    def __init__(self, *args, solo_extra=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Tutti i piatti spuntati per il menù attualmente attivo.
        if solo_extra:
            # Usato per il cliente da QR quando è attivo il menù fisso: le
            # portate del menù sono automatiche, il cliente ordina solo gli
            # extra (es. bevande) delle categorie "sempre a parte".
            piatti_qs = Piatto.attivi(solo_sempre_a_parte=True).select_related("categoria")
        else:
            piatti_qs = Piatto.attivi().select_related("categoria")
        self.fields["piatto"].queryset = piatti_qs
