from django import forms

class ContactForm(forms.Form):
    select = forms.ChoiceField(widget=forms.Select)
    hidden = forms.CharField(widget=forms.HiddenInput)