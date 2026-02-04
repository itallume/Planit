from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError
from decimal import Decimal
from datetime import date, time

from atividade.forms import (
    AtividadeForm,
    ClienteForm,
    EnderecoForm,
    ReferenciaForm,
    EnderecoFormSet,
    ReferenciaFormSet,
)
from atividade.models import Atividade, Cliente, Endereco, Referencia
from ambiente.models import Ambiente
from django.contrib.auth.models import User


class AtividadeFormsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='atividade_forms_user',
            email='user@test.com',
            password='123'
        )

        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Teste Forms',
            tema='#000000',
            usuario_administrador=self.user
        )

        self.cliente = Cliente.objects.create(
            nome='Cliente Teste',
            email='cliente@test.com',
            telefone='83999999999',
            sobre='Sobre'
        )

        self.atividade = Atividade.objects.create(
            descricao='Atividade Teste',
            valor=Decimal('100.00'),
            valor_recebido=Decimal('0.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            status='Pendente',
            is_paga=False,
            ambiente=self.ambiente,
            cliente=self.cliente
        )

    # -------------------------
    # AtividadeForm
    # -------------------------

    def test_atividade_form_valido(self):
        form = AtividadeForm(data={
            'descricao': 'Nova atividade',
            'valor': '100.00',
            'valor_recebido': '50.00',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
            'is_paga': False,
            'cliente': self.cliente.id
        })
        self.assertTrue(form.is_valid())

    def test_valor_nao_pode_ser_negativo(self):
        form = AtividadeForm(data={
            'descricao': 'Teste',
            'valor': '-1',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
            'is_paga': False
        })
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)

    def test_valor_recebido_nao_pode_ser_negativo(self):
        form = AtividadeForm(data={
            'descricao': 'Teste',
            'valor': '100',
            'valor_recebido': '-10',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
            'is_paga': False
        })
        self.assertFalse(form.is_valid())
        self.assertIn('valor_recebido', form.errors)

    def test_valor_recebido_nao_pode_ser_maior_que_valor(self):
        form = AtividadeForm(data={
            'descricao': 'Teste',
            'valor': '100',
            'valor_recebido': '150',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
            'is_paga': False
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    # -------------------------
    # ClienteForm
    # -------------------------

    def test_cliente_form_email_unico(self):
        form = ClienteForm(data={
            'nome': 'Outro',
            'email': 'cliente@test.com',
            'telefone': '000',
            'sobre': 'Teste'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_cliente_form_edicao_mesmo_email(self):
        form = ClienteForm(
            data={
                'nome': 'Cliente Teste',
                'email': 'cliente@test.com',
                'telefone': '999',
                'sobre': 'Atualizado'
            },
            instance=self.cliente
        )
        self.assertTrue(form.is_valid())

    def test_cliente_form_email_vazio(self):
        form = ClienteForm(data={
            'nome': 'Sem email',
            'email': '',
            'telefone': '',
            'sobre': ''
        })
        self.assertTrue(form.is_valid())

    # -------------------------
    # ReferenciaForm
    # -------------------------

    def test_referencia_form_extensao_valida(self):
        arquivo = SimpleUploadedFile(
            'arquivo.pdf',
            b'teste',
            content_type='application/pdf'
        )

        form = ReferenciaForm(
            data={'nome_arquivo': 'Arquivo'},
            files={'arquivo': arquivo}
        )
        self.assertTrue(form.is_valid())

    def test_referencia_form_extensao_invalida(self):
        arquivo = SimpleUploadedFile(
            'arquivo.exe',
            b'teste'
        )

        form = ReferenciaForm(
            data={'nome_arquivo': 'Arquivo'},
            files={'arquivo': arquivo}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('arquivo', form.errors)

    # -------------------------
    # EnderecoForm
    # -------------------------

    def test_endereco_form_valido(self):
        form = EnderecoForm(data={
            'rua': 'Rua A',
            'numero': '10',
            'cidade': 'JP',
            'estado': 'PB',
            'cep': '58000-000',
            'complemento': ''
        })
        self.assertTrue(form.is_valid())

    # -------------------------
    # Formsets
    # -------------------------

    def test_endereco_formset(self):
        data = {
            'endereco-TOTAL_FORMS': '1',
            'endereco-INITIAL_FORMS': '0',
            'endereco-MIN_NUM_FORMS': '0',
            'endereco-MAX_NUM_FORMS': '1000',
            'endereco-0-rua': 'Rua A',
            'endereco-0-numero': '1',
            'endereco-0-cidade': 'JP',
            'endereco-0-estado': 'PB',
            'endereco-0-cep': '58000',
            'endereco-0-complemento': '',
        }

        formset = EnderecoFormSet(data=data, instance=self.cliente, prefix='endereco')
        self.assertTrue(formset.is_valid())

    def test_referencia_formset(self):
        arquivo = SimpleUploadedFile(
            'arquivo.png',
            b'teste',
            content_type='image/png'
        )

        data = {
            'referencia-TOTAL_FORMS': '1',
            'referencia-INITIAL_FORMS': '0',
            'referencia-MIN_NUM_FORMS': '0',
            'referencia-MAX_NUM_FORMS': '1000',
            'referencia-0-nome_arquivo': 'Imagem',
        }

        files = {
            'referencia-0-arquivo': arquivo
        }

        formset = ReferenciaFormSet(
            data=data,
            files=files,
            instance=self.atividade,
            prefix='referencia'
        )

        self.assertTrue(formset.is_valid())
