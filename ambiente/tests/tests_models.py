from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ambiente.models import (
    Ambiente,
    AmbienteInvitations,
    Role,
    Participante,
    Notificacao
)


class AmbienteModelsTestCase(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='ambiente_model_admin',
            password='123456'
        )

        self.user = User.objects.create_user(
            username='ambiente_model_user',
            password='123456'
        )

        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Teste Model',
            usuario_administrador=self.admin
        )

    # =====================
    # Ambiente
    # =====================

    def test_ambiente_criacao_padrao(self):
        self.assertEqual(self.ambiente.nome, 'Ambiente Teste Model')
        self.assertEqual(self.ambiente.tema, '#F26800')
        self.assertEqual(self.ambiente.usuario_administrador, self.admin)

    def test_ambiente_tema_valido(self):
        ambiente = Ambiente(
            nome='Tema OK',
            tema='#AABBCC',
            usuario_administrador=self.admin
        )
        ambiente.full_clean()  # não deve levantar erro

    def test_ambiente_tema_invalido(self):
        ambiente = Ambiente(
            nome='Tema Inválido',
            tema='123456',
            usuario_administrador=self.admin
        )
        with self.assertRaises(ValidationError):
            ambiente.full_clean()

    def test_ambiente_str(self):
        self.assertEqual(str(self.ambiente), 'Ambiente Teste Model')

    def test_usuarios_participantes_m2m(self):
        self.ambiente.usuarios_participantes.add(self.user)
        self.assertIn(self.user, self.ambiente.usuarios_participantes.all())

    # =====================
    # AmbienteInvitations
    # =====================

    def test_convite_criacao(self):
        convite = AmbienteInvitations.objects.create(
            ambiente=self.ambiente,
            email='teste@email.com',
            token='token123',
            inviter=self.admin,
            guest=self.user
        )

        self.assertFalse(convite.accepted)
        self.assertEqual(convite.ambiente, self.ambiente)

    def test_convite_str(self):
        convite = AmbienteInvitations.objects.create(
            ambiente=self.ambiente,
            email='teste@email.com',
            token='token456',
            inviter=self.admin,
            guest=self.user
        )

        self.assertIn('Invitation to', str(convite))
        self.assertIn(self.ambiente.nome, str(convite))

    def test_convite_token_unico(self):
        AmbienteInvitations.objects.create(
            ambiente=self.ambiente,
            email='a@email.com',
            token='token-unico',
            inviter=self.admin,
            guest=self.user
        )

        with self.assertRaises(Exception):
            AmbienteInvitations.objects.create(
                ambiente=self.ambiente,
                email='b@email.com',
                token='token-unico',
                inviter=self.admin,
                guest=self.user
            )

    # =====================
    # Role
    # =====================

    def test_role_leitor_padrao(self):
        # O signal já cria as roles, então usamos get_or_create
        role, created = Role.objects.get_or_create(
            nome=Role.LEITOR,
            ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True}
        )

        self.assertTrue(role.pode_visualizar_atividades)
        self.assertFalse(role.pode_criar_atividades)
        self.assertFalse(role.pode_editar_atividades)
        self.assertFalse(role.pode_deletar_atividades)

    def test_role_str(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.ADMINISTRADOR,
            ambiente=self.ambiente,
            defaults={
                'pode_visualizar_atividades': True,
                'pode_criar_atividades': True,
                'pode_editar_atividades': True,
                'pode_deletar_atividades': True
            }
        )

        self.assertIn('Administrador', str(role))
        self.assertIn(self.ambiente.nome, str(role))

    def test_role_unique_por_ambiente(self):
        # As roles já são criadas pelo signal, então verificamos que criar duplicada falha
        # Primeiro deletamos a role existente para garantir que podemos criar uma nova
        Role.objects.filter(nome=Role.CUSTOM, ambiente=self.ambiente).delete()
        
        Role.objects.create(
            nome=Role.CUSTOM,
            ambiente=self.ambiente
        )

        with self.assertRaises(Exception):
            Role.objects.create(
                nome=Role.CUSTOM,
                ambiente=self.ambiente
            )

    # =====================
    # Participante
    # =====================

    def test_participante_criacao(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.LEITOR,
            ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True}
        )

        # Deletar participante existente se houver
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()

        participante = Participante.objects.create(
            usuario=self.user,
            ambiente=self.ambiente,
            role=role
        )

        self.assertEqual(participante.usuario, self.user)
        self.assertEqual(participante.ambiente, self.ambiente)
        self.assertEqual(participante.role, role)

    def test_participante_str_com_role(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.EDITOR,
            ambiente=self.ambiente,
            defaults={
                'pode_visualizar_atividades': True,
                'pode_criar_atividades': True,
                'pode_editar_atividades': True
            }
        )

        # Deletar participante existente se houver
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()

        participante = Participante.objects.create(
            usuario=self.user,
            ambiente=self.ambiente,
            role=role
        )

        self.assertIn(self.user.username, str(participante))
        self.assertIn('Editor', str(participante))

    def test_participante_str_sem_role(self):
        # Deletar participante existente se houver
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        
        participante = Participante.objects.create(
            usuario=self.user,
            ambiente=self.ambiente
        )

        self.assertIn('Sem role', str(participante))

    def test_participante_unique_usuario_ambiente(self):
        # Deletar participante existente se houver
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        
        Participante.objects.create(
            usuario=self.user,
            ambiente=self.ambiente
        )

        with self.assertRaises(Exception):
            Participante.objects.create(
                usuario=self.user,
                ambiente=self.ambiente
            )

    # =====================
    # Notificacao
    # =====================

    def test_notificacao_criacao(self):
        notif = Notificacao.objects.create(
            usuario=self.user,
            tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE,
            titulo='Nova atividade',
            mensagem='Você foi alocado',
            ambiente=self.ambiente
        )

        self.assertFalse(notif.lida)
        self.assertEqual(notif.usuario, self.user)

    def test_notificacao_str(self):
        notif = Notificacao.objects.create(
            usuario=self.user,
            tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE,
            titulo='Teste',
            mensagem='Mensagem'
        )

        self.assertIn(self.user.username, str(notif))
        self.assertIn('Teste', str(notif))

    def test_notificacao_ordering(self):
        notif1 = Notificacao.objects.create(
            usuario=self.user,
            tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE,
            titulo='Antiga',
            mensagem='Mensagem'
        )

        notif2 = Notificacao.objects.create(
            usuario=self.user,
            tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE,
            titulo='Nova',
            mensagem='Mensagem'
        )

        notificacoes = list(Notificacao.objects.all())
        self.assertEqual(notificacoes[0], notif2)
        self.assertEqual(notificacoes[1], notif1)
