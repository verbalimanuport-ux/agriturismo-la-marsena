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
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "interesse_lezione_cavallo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_sito_web(self):
        valore = self.cleaned_data.get("sito_web")
        if valore:
            raise forms.ValidationError("Errore nella compilazione del modulo.")
        return valore

    def clean(self):
        cleaned_data = super().clean()
        telefono = cleaned_data.get("telefono")
        email = cleaned_data.get("email")
        if not telefono and not email:
            raise forms.ValidationError(
                "Inserisci almeno un numero di telefono o un indirizzo email per poterti ricontattare."
            )
        return cleaned_data
