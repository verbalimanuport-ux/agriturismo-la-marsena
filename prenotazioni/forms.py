from django import forms

from .models import Prenotazione


class PrenotazioneForm(forms.ModelForm):
    # Campo "trappola" anti-spam: invisibile alle persone, ma i robot spesso lo compilano.
    # Se arriva compilato, scartiamo la richiesta.
    sito_web = forms.CharField(
        required=False, widget=forms.HiddenInput(), label="", help_text=""
    )

    class Meta:
        model = Prenotazione
        fields = [
            "nome",
            "telefono",
            "email",
            "data",
            "ora",
            "numero_coperti",
            "numero_bambini",
            "numero_seggioloni",
            "note",
            "interesse_lezione_cavallo",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "data": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "ora": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "numero_coperti": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "numero_bambini": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "numero_seggioloni": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "interesse_lezione_cavallo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Il telefono è sempre obbligatorio: è lo strumento principale con cui
        # lo staff richiama per confermare, specialmente per chi non lascia
        # un'email. L'email resta facoltativa (un "di più" comodo se c'è).
        self.fields["telefono"].required = True

    def clean_sito_web(self):
        valore = self.cleaned_data.get("sito_web")
        if valore:
            raise forms.ValidationError("Errore nella compilazione del modulo.")
        return valore
