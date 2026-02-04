
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from atividade.models import Atividade, Cliente, Endereco, Referencia
from ambiente.models import Participante


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['descricao', 'valor', 'valor_recebido', 'data_prevista', 'hora_prevista', 'status', 'is_paga', 'cliente']
        widgets = {
            'data_prevista': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora_prevista': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'cliente': forms.HiddenInput(),
            'status': forms.RadioSelect(),
        }
        labels = {
            'status': 'Status da atividade',
            'is_paga': 'Atividade paga',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantir que os formatos de data e hora sejam compatíveis com HTML5 inputs
        self.fields['data_prevista'].input_formats = ['%Y-%m-%d']
        self.fields['hora_prevista'].input_formats = ['%H:%M', '%H:%M:%S']
        
        # Tornar descrição obrigatória
        self.fields['descricao'].required = True
        
        # Remover atributo 'required' de todos os campos (validação apenas no backend)
        for field_name, field in self.fields.items():
            field.widget.attrs.pop('required', None)
            if hasattr(field.widget, 'use_required_attribute'):
                field.widget.use_required_attribute = lambda x: False
    
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor < 0:
            raise forms.ValidationError('O valor não pode ser negativo.')
        return valor
    
    def clean_valor_recebido(self):
        valor_recebido = self.cleaned_data.get('valor_recebido')
        if valor_recebido is not None and valor_recebido < 0:
            raise forms.ValidationError('O valor recebido não pode ser negativo.')
        return valor_recebido
    
    def clean(self):
        cleaned_data = super().clean()
        valor = cleaned_data.get('valor')
        valor_recebido = cleaned_data.get('valor_recebido')
        
        if valor is not None and valor_recebido is not None:
            if valor_recebido > valor:
                raise forms.ValidationError('O valor recebido não pode ser maior que o valor total.')
        
        return cleaned_data


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'sobre']
        widgets = {
            'sobre': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos opcionais quando usado em conjunto com atividade
        for field_name in self.fields:
            self.fields[field_name].required = False
            # Remover atributo 'required' do HTML (validação apenas no backend)
            self.fields[field_name].widget.attrs.pop('required', None)
            if hasattr(self.fields[field_name].widget, 'use_required_attribute'):
                self.fields[field_name].widget.use_required_attribute = lambda x: False
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        
        # Se estamos editando uma instância existente, verificar se o email mudou
        if self.instance and self.instance.pk:
            # Se o email não mudou, não validar unicidade
            if email == self.instance.email:
                return email
        
        # Verificar se email já existe
        if Cliente.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('Cliente com este Email já existe.')
        
        return email

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['rua', 'numero', 'cidade', 'estado', 'cep', 'complemento']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover atributo 'required' de todos os campos (validação apenas no backend)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.pop('required', None)
            if hasattr(self.fields[field_name].widget, 'use_required_attribute'):
                self.fields[field_name].widget.use_required_attribute = lambda x: False


class ReferenciaForm(forms.ModelForm):
    class Meta:
        model = Referencia
        fields = ['nome_arquivo', 'arquivo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover atributo 'required' de todos os campos (validação apenas no backend)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.pop('required', None)
            if hasattr(self.fields[field_name].widget, 'use_required_attribute'):
                self.fields[field_name].widget.use_required_attribute = lambda x: False
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            extensao = arquivo.name.split('.')[-1].lower()
            extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
            if extensao not in extensoes_permitidas:
                raise forms.ValidationError(
                    f'Tipo de arquivo não permitido. Use apenas: {", ".join(extensoes_permitidas).upper()}'
                )
        return arquivo


# Formsets
EnderecoFormSet = inlineformset_factory(Cliente, Endereco, form=EnderecoForm, extra=0,can_delete=True)
ReferenciaFormSet = inlineformset_factory(Atividade, Referencia, form=ReferenciaForm, extra=0, can_delete=True)