from django import forms
from .models import Ambiente

class AmbienteForm(forms.ModelForm):
    class Meta:
        model = Ambiente
        fields = ['nome', 'tema']
        widgets = {
            'tema': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control-color'
            }),
        }
        labels = {
            'nome': 'Nome do Ambiente',
            'tema': 'Cor do Tema',
        }