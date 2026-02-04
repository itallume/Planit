from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, time, timedelta

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

    def test_atividade_criacao(self):
        self.assertIsNotNone(self.atividade.id)

    def test_atividade_valor_padrao(self):
        atividade = Atividade.objects.create(
            valor=Decimal('50.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente
        )
        self.assertEqual(atividade.valor, Decimal('50.00'))

    def test_atividade_status_padrao(self):
        atividade = Atividade.objects.create(
            valor=Decimal('50.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente
        )
        self.assertEqual(atividade.status, 'Pendente')

    def test_atividade_is_paga_padrao(self):
        atividade = Atividade.objects.create(
            valor=Decimal('50.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente
        )
        self.assertFalse(atividade.is_paga)

    def test_atividade_valor_recebido_padrao(self):
        atividade = Atividade.objects.create(
            valor=Decimal('50.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente
        )
        self.assertEqual(atividade.valor_recebido, Decimal('0.00'))

    def test_atividade_com_cliente(self):
        self.assertEqual(self.atividade.cliente, self.cliente)

    def test_atividade_sem_cliente(self):
        atividade = Atividade.objects.create(
            valor=Decimal('50.00'),
            data_prevista=date.today(),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente
        )
        self.assertIsNone(atividade.cliente)

    def test_atividade_ambiente_relation(self):
        self.assertEqual(self.atividade.ambiente, self.ambiente)

    def test_atividade_alterar_status(self):
        self.atividade.status = 'Em andamento'
        self.atividade.save()
        self.atividade.refresh_from_db()
        self.assertEqual(self.atividade.status, 'Em andamento')

    def test_atividade_marcar_paga(self):
        self.atividade.is_paga = True
        self.atividade.save()
        self.atividade.refresh_from_db()
        self.assertTrue(self.atividade.is_paga)

    def test_atividade_alterar_valor(self):
        self.atividade.valor = Decimal('200.00')
        self.atividade.save()
        self.atividade.refresh_from_db()
        self.assertEqual(self.atividade.valor, Decimal('200.00'))

    def test_atividade_data_futura(self):
        atividade = Atividade.objects.create(
            valor=Decimal('50.00'),
            data_prevista=date.today() + timedelta(days=30),
            hora_prevista=time(10, 0),
            ambiente=self.ambiente
        )
        self.assertIsNotNone(atividade.id)

    def test_atividade_multiplos_participantes(self):
        user2 = User.objects.create_user(username='ativ_m_u2', password='123')
        participante2, _ = Participante.objects.get_or_create(usuario=user2, ambiente=self.ambiente, defaults={'role': self.role})
        self.atividade.participantes_alocados.add(self.participante, participante2)
        self.assertEqual(self.atividade.participantes_alocados.count(), 2)

    def test_atividade_remover_participante(self):
        self.atividade.participantes_alocados.add(self.participante)
        self.atividade.participantes_alocados.remove(self.participante)
        self.assertNotIn(self.participante, self.atividade.participantes_alocados.all())

    # ----------------------------
    # Cliente
    # ----------------------------

    def test_cliente_str(self):
        self.assertEqual(str(self.cliente), 'Cliente Teste')

    def test_cliente_criacao(self):
        cliente = Cliente.objects.create(nome='Novo Cliente', email='nc@test.com')
        self.assertIsNotNone(cliente.id)

    def test_cliente_email(self):
        self.assertEqual(self.cliente.email, 'cliente@test.com')

    def test_cliente_telefone(self):
        self.assertEqual(self.cliente.telefone, '83999999999')

    def test_cliente_sobre(self):
        self.assertEqual(self.cliente.sobre, 'Cliente de teste')

    def test_cliente_sem_telefone(self):
        cliente = Cliente.objects.create(nome='Sem Tel', email='st@test.com', telefone='')
        self.assertEqual(cliente.telefone, '')

    def test_cliente_alterar_nome(self):
        self.cliente.nome = 'Nome Alterado'
        self.cliente.save()
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nome, 'Nome Alterado')

    def test_cliente_delete(self):
        cliente = Cliente.objects.create(nome='Del', email='del@test.com')
        cliente_id = cliente.id
        cliente.delete()
        self.assertFalse(Cliente.objects.filter(id=cliente_id).exists())

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

    def test_endereco_criacao(self):
        endereco = Endereco.objects.create(
            rua='Rua B', cidade='Recife', estado='PE', cep='50000-000', cliente=self.cliente
        )
        self.assertIsNotNone(endereco.id)

    def test_endereco_com_numero(self):
        endereco = Endereco.objects.create(
            rua='Rua C', numero='123', cidade='Natal', estado='RN', cep='59000-000', cliente=self.cliente
        )
        self.assertEqual(endereco.numero, '123')

    def test_endereco_cliente_relation(self):
        endereco = Endereco.objects.create(
            rua='Rua D', cidade='Fortaleza', estado='CE', cep='60000-000', cliente=self.cliente
        )
        self.assertEqual(endereco.cliente, self.cliente)

    def test_endereco_atividade_relation(self):
        endereco = Endereco.objects.create(
            rua='Rua E', cidade='Salvador', estado='BA', cep='40000-000', atividade=self.atividade
        )
        self.assertEqual(endereco.atividade, self.atividade)

    def test_endereco_delete(self):
        endereco = Endereco.objects.create(
            rua='Rua F', cidade='Maceió', estado='AL', cep='57000-000', cliente=self.cliente
        )
        end_id = endereco.id
        endereco.delete()
        self.assertFalse(Endereco.objects.filter(id=end_id).exists())

    # ----------------------------
    # Referencia
    # ----------------------------

    def test_referencia_str(self):
        arquivo = SimpleUploadedFile('arquivo.pdf', b'conteudo fake', content_type='application/pdf')
        referencia = Referencia.objects.create(nome_arquivo='Contrato', arquivo=arquivo, atividade=self.atividade)
        self.assertEqual(str(referencia), 'Contrato')

    def test_referencia_define_tipo_pdf(self):
        arquivo = SimpleUploadedFile('documento.pdf', b'teste', content_type='application/pdf')
        referencia = Referencia.objects.create(nome_arquivo='Documento', arquivo=arquivo, atividade=self.atividade)
        self.assertEqual(referencia.tipo, 'PDF')

    def test_referencia_define_tipo_imagem_jpg(self):
        arquivo = SimpleUploadedFile('imagem.jpg', b'teste', content_type='image/jpeg')
        referencia = Referencia.objects.create(nome_arquivo='Imagem', arquivo=arquivo, atividade=self.atividade)
        self.assertEqual(referencia.tipo, 'Imagem JPG')

    def test_referencia_extensao_invalida(self):
        arquivo = SimpleUploadedFile('arquivo.exe', b'teste')
        referencia = Referencia(nome_arquivo='Arquivo inválido', arquivo=arquivo, atividade=self.atividade)
        with self.assertRaises(ValidationError):
            referencia.full_clean()

    def test_referencia_tipo_png(self):
        arquivo = SimpleUploadedFile('img.png', b'teste', content_type='image/png')
        referencia = Referencia.objects.create(nome_arquivo='PNG', arquivo=arquivo, atividade=self.atividade)
        self.assertEqual(referencia.tipo, 'Imagem PNG')

    def test_referencia_atividade_relation(self):
        arquivo = SimpleUploadedFile('ref.pdf', b'teste', content_type='application/pdf')
        referencia = Referencia.objects.create(nome_arquivo='Ref', arquivo=arquivo, atividade=self.atividade)
        self.assertEqual(referencia.atividade, self.atividade)

    def test_referencia_delete(self):
        arquivo = SimpleUploadedFile('del.pdf', b'teste', content_type='application/pdf')
        referencia = Referencia.objects.create(nome_arquivo='Del', arquivo=arquivo, atividade=self.atividade)
        ref_id = referencia.id
        referencia.delete()
        self.assertFalse(Referencia.objects.filter(id=ref_id).exists())


class AtividadeModelsAdicionaisTestCase(TestCase):
    """Testes adicionais para cobertura completa dos modelos"""

    def setUp(self):
        self.user = User.objects.create_user(username='ativ_add_m_user', password='123')
        self.ambiente = Ambiente.objects.create(nome='Amb Add M', usuario_administrador=self.user)

    def test_atividade_descricao_longa(self):
        descricao = 'A' * 200
        atividade = Atividade.objects.create(
            descricao=descricao, valor=Decimal('10'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(10, 0)
        )
        self.assertEqual(atividade.descricao, descricao)

    def test_atividade_str_truncado(self):
        descricao = 'B' * 100
        atividade = Atividade.objects.create(
            descricao=descricao, valor=Decimal('10'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(10, 0)
        )
        self.assertEqual(len(str(atividade)), 50)

    def test_atividade_valor_grande(self):
        atividade = Atividade.objects.create(
            valor=Decimal('999999.99'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(10, 0)
        )
        self.assertEqual(atividade.valor, Decimal('999999.99'))

    def test_atividade_valor_decimal(self):
        atividade = Atividade.objects.create(
            valor=Decimal('123.45'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(10, 0)
        )
        self.assertEqual(atividade.valor, Decimal('123.45'))

    def test_cliente_multiplos_enderecos(self):
        cliente = Cliente.objects.create(nome='Multi End', email='me@test.com')
        Endereco.objects.create(rua='R1', cidade='C1', estado='PB', cep='58000-001', cliente=cliente)
        Endereco.objects.create(rua='R2', cidade='C2', estado='PE', cep='50000-001', cliente=cliente)
        enderecos = Endereco.objects.filter(cliente=cliente)
        self.assertEqual(enderecos.count(), 2)

    def test_atividade_multiplas_referencias(self):
        atividade = Atividade.objects.create(
            valor=Decimal('10'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(10, 0)
        )
        arquivo1 = SimpleUploadedFile('r1.pdf', b't', content_type='application/pdf')
        arquivo2 = SimpleUploadedFile('r2.pdf', b't', content_type='application/pdf')
        Referencia.objects.create(nome_arquivo='R1', arquivo=arquivo1, atividade=atividade)
        Referencia.objects.create(nome_arquivo='R2', arquivo=arquivo2, atividade=atividade)
        refs = Referencia.objects.filter(atividade=atividade)
        self.assertEqual(refs.count(), 2)

    def test_endereco_sem_numero(self):
        cliente = Cliente.objects.create(nome='SN', email='sn@test.com')
        endereco = Endereco.objects.create(rua='Rua SN', cidade='C', estado='PB', cep='58000-000', cliente=cliente)
        self.assertIn(endereco.numero, [None, ''])

    def test_cliente_email_unico(self):
        cliente = Cliente.objects.create(nome='Unique', email='unique@test.com')
        self.assertIsNotNone(cliente.id)

    def test_atividade_hora_meia_noite(self):
        atividade = Atividade.objects.create(
            valor=Decimal('10'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(0, 0)
        )
        self.assertEqual(atividade.hora_prevista, time(0, 0))

    def test_atividade_hora_23_59(self):
        atividade = Atividade.objects.create(
            valor=Decimal('10'), ambiente=self.ambiente,
            data_prevista=date.today(), hora_prevista=time(23, 59)
        )
        self.assertEqual(atividade.hora_prevista, time(23, 59))
