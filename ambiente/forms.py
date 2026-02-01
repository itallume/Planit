from django import forms
from .models import Ambiente, AmbienteInvitations
from django.contrib.auth.models import User


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

class SendInvitationForm(forms.Form):
    email = forms.EmailField(label='Email do Convidado', max_length=254)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        invited_emails = AmbienteInvitations.objects.values_list('email', flat=True)
        if email in invited_emails:
            raise forms.ValidationError('Este email já foi convidado.')
        if Ambiente.objects.filter(usuarios_participantes__email=email).exists():
            raise forms.ValidationError('Este email já pertence a um participante do ambiente.')
        if Ambiente.objects.filter(usuario_administrador__email=email).exists():
            raise forms.ValidationError('Este email já pertence ao administrador do ambiente.')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email não está registrado no sistema.')
        if not email:
            raise forms.ValidationError('Por favor, insira um email válido.')

        return email