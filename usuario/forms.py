

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        max_length=254, 
        label='Email',
        help_text='Informe um endereço de email válido.', 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2', )
        labels = {
            'username': 'Nome de usuário',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['username'].widget.attrs.update({'placeholder': 'Seu nome de usuário'})
        self.fields['username'].error_messages = {
            'unique': 'Um usuário com este nome já existe.',
            'required': 'Este campo é obrigatório.',
        }
        
        self.fields['password1'].label = 'Senha'
        self.fields['password1'].help_text = None
        self.fields['password1'].widget.attrs.update({'placeholder': 'Digite sua senha'})
        
        self.fields['password2'].label = 'Confirmar senha'
        self.fields['password2'].help_text = None
        self.fields['password2'].widget.attrs.update({'placeholder': 'Digite a senha novamente'})
        self.fields['password2'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Um usuário com este email já existe.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Um usuário com este nome já existe.')
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        return password2

class SignInForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        label='Nome de usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome de usuário'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'})
    )
