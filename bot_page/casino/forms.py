from django import forms


class BetForm(forms.Form):
    percent_to_win = forms.IntegerField(label="""Procent na wygraną: <span class='text-success' id='percent_label'>50%</span><br>
                                                 Nagroda w wyniku wygranej: <span class='text-success' id='multiplier_label'>0</span>""",
                                        widget=forms.NumberInput(attrs={"class": "form-control mb-2", "type": "range", "min": "1", "max": "90"}),
                                        min_value=1, max_value=90)
    bet_money = forms.FloatField(label="Liczba obstawionych monet",
                                 widget=forms.NumberInput(attrs={"class": "form-control mb-2"}), min_value=0)


class JackpotForm(forms.Form):
    tickets = forms.IntegerField(label="Liczba biletów",
                                 widget=forms.NumberInput(attrs={"class": "form-control mb-2"}), min_value=0)
