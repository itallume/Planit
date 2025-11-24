
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from atividade.models import Atividade, Cliente, Endereco, Referencia


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['descricao', 'valor', 'valor_recebido', 'data_prevista', 'status', 'is_paga', 'ambiente', 'cliente']
        widgets = {
            'data_prevista': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'sobre']
        widgets = {
            'sobre': forms.Textarea(attrs={'rows': 3}),
        }


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['rua', 'cidade', 'estado', 'cep', 'complemento']


class ReferenciaForm(forms.ModelForm):
    class Meta:
        model = Referencia
        fields = ['tipo', 'nome_arquivo', 'arquivo']


# Formsets
EnderecoFormSet = inlineformset_factory(Cliente, Endereco, form=EnderecoForm, extra=0,can_delete=True)
ReferenciaFormSet = inlineformset_factory(Atividade, Referencia, form=ReferenciaForm, extra=0, can_delete=True)