from django.test import TestCase
from django import forms
from django.contrib.auth.models import User
from ambiente.models import Ambiente
from ambiente.forms import AmbienteForm


class AmbienteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')

    def test_ambiente_form_valid(self):
        """Testa se formulário é válido com dados corretos"""
        data = {
            'nome': 'Projeto Web',
            'tema': 'Azul'
        }
        form = AmbienteForm(data=data)
        self.assertTrue(form.is_valid())

    def test_ambiente_form_valid_without_tema(self):
        """Testa se formulário é válido sem tema (campo opcional)"""
        data = {
            'nome': 'Projeto Mobile',
            'tema': ''
        }
        form = AmbienteForm(data=data)
        self.assertTrue(form.is_valid())

    def test_ambiente_form_invalid_empty_nome(self):
        """Testa se formulário é inválido sem nome"""
        data = {
            'nome': '',
            'tema': 'Verde'
        }
        form = AmbienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_ambiente_form_invalid_no_data(self):
        """Testa se formulário é inválido sem nenhum dado"""
        form = AmbienteForm(data={})
        self.assertFalse(form.is_valid())

    def test_ambiente_form_nome_max_length(self):
        """Testa validação do tamanho máximo do nome"""
        data = {
            'nome': 'A' * 101,  # Maior que max_length=100
            'tema': 'Azul'
        }
        form = AmbienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_ambiente_form_tema_max_length(self):
        """Testa validação do tamanho máximo do tema"""
        data = {
            'nome': 'Projeto Teste',
            'tema': 'A' * 101  # Maior que max_length=100
        }
        form = AmbienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('tema', form.errors)

    def test_ambiente_form_save(self):
        """Testa se o form salva corretamente no banco"""
        data = {
            'nome': 'Projeto Salvo',
            'tema': 'Vermelho'
        }
        form = AmbienteForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Precisa passar commit=False para evitar erro de admin ausente
        ambiente = form.save(commit=False)
        ambiente.usuario_administrador = self.user
        ambiente.save()
        
        ambiente_salvo = Ambiente.objects.get(nome='Projeto Salvo')
        self.assertEqual(ambiente_salvo.nome, 'Projeto Salvo')
        self.assertEqual(ambiente_salvo.tema, 'Vermelho')

    def test_ambiente_form_update(self):
        """Testa se o form atualiza um ambiente existente"""
        # Criar ambiente
        ambiente = Ambiente.objects.create(
            nome='Projeto Original',
            tema='Azul',
            usuario_administrador=self.user
        )
        
        # Atualizar via form
        data = {
            'nome': 'Projeto Atualizado',
            'tema': 'Verde'
        }
        form = AmbienteForm(data=data, instance=ambiente)
        self.assertTrue(form.is_valid())
        form.save()
        
        # Verificar atualização
        ambiente_atualizado = Ambiente.objects.get(id=ambiente.id)
        self.assertEqual(ambiente_atualizado.nome, 'Projeto Atualizado')
        self.assertEqual(ambiente_atualizado.tema, 'Verde')

    def test_ambiente_form_fields(self):
        """Testa se apenas os campos corretos estão no form"""
        form = AmbienteForm()
        expected_fields = ['nome', 'tema']
        self.assertEqual(list(form.fields.keys()), expected_fields)

    def test_ambiente_form_nome_field_type(self):
        """Testa se o campo nome é do tipo CharField"""
        form = AmbienteForm()
        self.assertIsInstance(form.fields['nome'], forms.CharField)

    def test_ambiente_form_tema_field_type(self):
        """Testa se o campo tema é do tipo CharField"""
        form = AmbienteForm()
        self.assertIsInstance(form.fields['tema'], forms.CharField)

    def test_ambiente_form_tema_required_false(self):
        """Testa se o campo tema não é obrigatório"""
        form = AmbienteForm()
        self.assertFalse(form.fields['tema'].required)

    def test_ambiente_form_nome_required_true(self):
        """Testa se o campo nome é obrigatório"""
        form = AmbienteForm()
        self.assertTrue(form.fields['nome'].required)

    def test_ambiente_form_instance_prefill(self):
        """Testa se formulário com instance preenche os dados"""
        ambiente = Ambiente.objects.create(
            nome='Projeto Existente',
            tema='Roxo',
            usuario_administrador=self.user
        )
        
        form = AmbienteForm(instance=ambiente)
        self.assertEqual(form.initial['nome'], 'Projeto Existente')
        self.assertEqual(form.initial['tema'], 'Roxo')

    def test_ambiente_form_error_message_nome(self):
        """Testa mensagem de erro quando nome está vazio"""
        form = AmbienteForm(data={'nome': '', 'tema': 'Azul'})
        self.assertFalse(form.is_valid())
        self.assertIn('Este campo é obrigatório', str(form.errors['nome']))

    def test_ambiente_form_whitespace_nome(self):
        """Testa se nome com apenas espaços em branco é inválido"""
        data = {
            'nome': '   ',
            'tema': 'Azul'
        }
        form = AmbienteForm(data=data)
        # Django limpa espaços em branco, então fica vazio e inválido
        self.assertFalse(form.is_valid())

    def test_ambiente_form_special_characters(self):
        """Testa se formulário aceita caracteres especiais"""
        data = {
            'nome': 'Projeto @#$%&',
            'tema': 'Tema !@#$%'
        }
        form = AmbienteForm(data=data)
        self.assertTrue(form.is_valid())

    def test_ambiente_form_unicode_characters(self):
        """Testa se formulário aceita caracteres unicode"""
        data = {
            'nome': 'Projeto São Paulo',
            'tema': 'Tema ñ€中文'
        }
        form = AmbienteForm(data=data)
        self.assertTrue(form.is_valid())
