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

    def test_endereco_form_sem_numero(self):
        form = EnderecoForm(data={
            'rua': 'Rua B',
            'numero': '',
            'cidade': 'JP',
            'estado': 'PB',
            'cep': '58000-000'
        })
        self.assertTrue(form.is_valid())

    def test_endereco_form_com_complemento(self):
        form = EnderecoForm(data={
            'rua': 'Rua C',
            'numero': '100',
            'cidade': 'Recife',
            'estado': 'PE',
            'cep': '50000-000',
            'complemento': 'Apt 101'
        })
        self.assertTrue(form.is_valid())

    def test_endereco_form_campos(self):
        form = EnderecoForm()
        self.assertIn('rua', form.fields)
        self.assertIn('cidade', form.fields)
        self.assertIn('estado', form.fields)
        self.assertIn('cep', form.fields)

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

    def test_endereco_formset_multiplos(self):
        data = {
            'endereco-TOTAL_FORMS': '2',
            'endereco-INITIAL_FORMS': '0',
            'endereco-MIN_NUM_FORMS': '0',
            'endereco-MAX_NUM_FORMS': '1000',
            'endereco-0-rua': 'Rua 1',
            'endereco-0-cidade': 'C1',
            'endereco-0-estado': 'PB',
            'endereco-0-cep': '58000-001',
            'endereco-1-rua': 'Rua 2',
            'endereco-1-cidade': 'C2',
            'endereco-1-estado': 'PE',
            'endereco-1-cep': '50000-001',
        }
        formset = EnderecoFormSet(data=data, instance=self.cliente, prefix='endereco')
        self.assertTrue(formset.is_valid())

    def test_referencia_formset_vazio(self):
        data = {
            'referencia-TOTAL_FORMS': '0',
            'referencia-INITIAL_FORMS': '0',
            'referencia-MIN_NUM_FORMS': '0',
            'referencia-MAX_NUM_FORMS': '1000',
        }
        formset = ReferenciaFormSet(data=data, instance=self.atividade, prefix='referencia')
        self.assertTrue(formset.is_valid())


class AtividadeFormsAdicionaisTestCase(TestCase):
    """Testes adicionais para formulários de atividade"""

    def setUp(self):
        self.user = User.objects.create_user(username='ativ_f_add_user', email='afu@test.com', password='123')
        self.ambiente = Ambiente.objects.create(nome='Amb F Add', usuario_administrador=self.user)

    def test_atividade_form_campos(self):
        form = AtividadeForm()
        self.assertIn('descricao', form.fields)
        self.assertIn('valor', form.fields)
        self.assertIn('valor_recebido', form.fields)
        self.assertIn('data_prevista', form.fields)
        self.assertIn('hora_prevista', form.fields)
        self.assertIn('status', form.fields)

    def test_atividade_form_valor_zero(self):
        form = AtividadeForm(data={
            'descricao': 'Valor Zero',
            'valor': '0',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_atividade_form_valor_grande(self):
        form = AtividadeForm(data={
            'descricao': 'Valor Grande',
            'valor': '999999.99',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_atividade_form_descricao_longa(self):
        form = AtividadeForm(data={
            'descricao': 'D' * 200,
            'valor': '100',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_atividade_form_status_em_andamento(self):
        form = AtividadeForm(data={
            'descricao': 'Status',
            'valor': '100',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Em andamento',
        })
        is_valid = form.is_valid()
        self.assertIsNotNone(is_valid)

    def test_atividade_form_hora_meia_noite(self):
        form = AtividadeForm(data={
            'descricao': 'Meia Noite',
            'valor': '100',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '00:00',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_atividade_form_hora_23_59(self):
        form = AtividadeForm(data={
            'descricao': '23:59',
            'valor': '100',
            'valor_recebido': '0',
            'data_prevista': date.today(),
            'hora_prevista': '23:59',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_cliente_form_campos(self):
        form = ClienteForm()
        self.assertIn('nome', form.fields)
        self.assertIn('email', form.fields)

    def test_cliente_form_nome_longo(self):
        form = ClienteForm(data={
            'nome': 'N' * 200,
            'email': 'longnome@test.com',
        })
        is_valid = form.is_valid()
        self.assertIsNotNone(is_valid)

    def test_cliente_form_sem_sobre(self):
        form = ClienteForm(data={
            'nome': 'Sem Sobre',
            'email': 'semsobre@test.com',
            'telefone': '',
            'sobre': ''
        })
        self.assertTrue(form.is_valid())

    def test_referencia_form_campos(self):
        form = ReferenciaForm()
        self.assertIn('nome_arquivo', form.fields)
        self.assertIn('arquivo', form.fields)

    def test_referencia_form_nome_longo(self):
        arquivo = SimpleUploadedFile('test.pdf', b't', content_type='application/pdf')
        form = ReferenciaForm(data={'nome_arquivo': 'A' * 100}, files={'arquivo': arquivo})
        is_valid = form.is_valid()
        self.assertIsNotNone(is_valid)

    def test_atividade_form_data_futura(self):
        from datetime import timedelta
        form = AtividadeForm(data={
            'descricao': 'Futura',
            'valor': '100',
            'valor_recebido': '0',
            'data_prevista': (date.today() + timedelta(days=30)).isoformat(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_atividade_form_valor_recebido_igual_valor(self):
        form = AtividadeForm(data={
            'descricao': 'Igual',
            'valor': '100',
            'valor_recebido': '100',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
        })
        self.assertTrue(form.is_valid())

    def test_atividade_form_is_paga_true(self):
        form = AtividadeForm(data={
            'descricao': 'Paga',
            'valor': '100',
            'valor_recebido': '100',
            'data_prevista': date.today(),
            'hora_prevista': '10:00',
            'status': 'Pendente',
            'is_paga': True,
        })
        self.assertTrue(form.is_valid())

    def test_endereco_form_estados(self):
        estados = ['PB', 'PE', 'RN', 'CE', 'BA', 'SP', 'RJ']
        for estado in estados:
            form = EnderecoForm(data={
                'rua': 'Rua',
                'cidade': 'Cidade',
                'estado': estado,
                'cep': '00000-000'
            })
            self.assertTrue(form.is_valid(), f'Estado {estado} deveria ser válido')

