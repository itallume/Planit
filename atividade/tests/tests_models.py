from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, time

from atividade.models import Atividade, Referencia, Cliente, Endereco
from ambiente.models import Ambiente, Participante, Role


class AtividadeModelsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='atividade_model_user',
            email='user1@test.com',
            password='123'
        )

        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Teste Atividade Model',
            tema='#ffffff',
            usuario_administrador=self.user
        )

        # Usar get_or_create pois o signal já cria as roles automaticamente
        self.role, _ = Role.objects.get_or_create(
            ambiente=self.ambiente,
            nome=Role.LEITOR,
            defaults={'pode_visualizar_atividades': True}
        )

        self.participante, _ = Participante.objects.get_or_create(
            usuario=self.user,
            ambiente=self.ambiente,
            defaults={'role': self.role}
        )

        self.cliente = Cliente.objects.create(
            nome='Cliente Teste',
            email='cliente@test.com',
            telefone='83999999999',
            sobre='Cliente de teste'
        )

        self.atividade = Atividade.objects.create(
            valor=Decimal('100.00'),
            is_paga=False,
            valor_recebido=Decimal('0.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente,
            descricao='Descrição da atividade de teste',
            cliente=self.cliente
        )

    # ----------------------------
    # Atividade
    # ----------------------------

    def test_atividade_str(self):
        self.assertEqual(str(self.atividade), self.atividade.descricao[:50])

    def test_atividade_valor_nao_pode_ser_negativo(self):
        atividade = Atividade(
            valor=Decimal('-1'),
            valor_recebido=Decimal('0'),
            data_prevista=date.today(),
            hora_prevista=time(9, 0),
            ambiente=self.ambiente
        )
        with self.assertRaises(ValidationError):
            atividade.full_clean()

    def test_relacionamento_participantes(self):
        self.atividade.participantes_alocados.add(self.participante)
        self.assertIn(self.participante, self.atividade.participantes_alocados.all())

    # ----------------------------
    # Cliente
    # ----------------------------

    def test_cliente_str(self):
        self.assertEqual(str(self.cliente), 'Cliente Teste')

    # ----------------------------
    # Endereco
    # ----------------------------

    def test_endereco_str(self):
        endereco = Endereco.objects.create(
            rua='Rua A',
            cidade='João Pessoa',
            estado='PB',
            cep='58000-000',
            cliente=self.cliente,
            atividade=self.atividade
        )
        self.assertEqual(str(endereco), 'Rua A, João Pessoa')

    # ----------------------------
    # Referencia
    # ----------------------------

    def test_referencia_str(self):
        arquivo = SimpleUploadedFile(
            'arquivo.pdf',
            b'conteudo fake',
            content_type='application/pdf'
        )

        referencia = Referencia.objects.create(
            nome_arquivo='Contrato',
            arquivo=arquivo,
            atividade=self.atividade
        )

        self.assertEqual(str(referencia), 'Contrato')

    def test_referencia_define_tipo_pdf(self):
        arquivo = SimpleUploadedFile(
            'documento.pdf',
            b'teste',
            content_type='application/pdf'
        )

        referencia = Referencia.objects.create(
            nome_arquivo='Documento',
            arquivo=arquivo,
            atividade=self.atividade
        )

        self.assertEqual(referencia.tipo, 'PDF')

    def test_referencia_define_tipo_imagem_jpg(self):
        arquivo = SimpleUploadedFile(
            'imagem.jpg',
            b'teste',
            content_type='image/jpeg'
        )

        referencia = Referencia.objects.create(
            nome_arquivo='Imagem',
            arquivo=arquivo,
            atividade=self.atividade
        )

        self.assertEqual(referencia.tipo, 'Imagem JPG')

    def test_referencia_extensao_invalida(self):
        arquivo = SimpleUploadedFile(
            'arquivo.exe',
            b'teste'
        )

        referencia = Referencia(
            nome_arquivo='Arquivo inválido',
            arquivo=arquivo,
            atividade=self.atividade
        )

        with self.assertRaises(ValidationError):
            referencia.full_clean()
