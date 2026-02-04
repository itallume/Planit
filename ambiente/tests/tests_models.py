from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        ambiente.full_clean()

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

    def test_ambiente_nome_vazio_invalido(self):
        ambiente = Ambiente(nome='', usuario_administrador=self.admin)
        with self.assertRaises(ValidationError):
            ambiente.full_clean()

    def test_ambiente_tema_hex_curto(self):
        ambiente = Ambiente(nome='Test', tema='#FFF', usuario_administrador=self.admin)
        with self.assertRaises(ValidationError):
            ambiente.full_clean()

    def test_ambiente_tem_id(self):
        self.assertIsNotNone(self.ambiente.id)

    def test_ambiente_multiplos_participantes(self):
        user2 = User.objects.create_user(username='amb_m_user2', password='123')
        user3 = User.objects.create_user(username='amb_m_user3', password='123')
        self.ambiente.usuarios_participantes.add(self.user, user2, user3)
        self.assertEqual(self.ambiente.usuarios_participantes.count(), 3)

    def test_ambiente_remover_participante(self):
        self.ambiente.usuarios_participantes.add(self.user)
        self.ambiente.usuarios_participantes.remove(self.user)
        self.assertNotIn(self.user, self.ambiente.usuarios_participantes.all())

    def test_ambiente_tema_valido_lower(self):
        ambiente = Ambiente(nome='T', tema='#aabbcc', usuario_administrador=self.admin)
        ambiente.full_clean()

    def test_ambiente_tema_valido_upper(self):
        ambiente = Ambiente(nome='T2', tema='#AABBCC', usuario_administrador=self.admin)
        ambiente.full_clean()

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

    def test_convite_aceitar(self):
        convite = AmbienteInvitations.objects.create(
            ambiente=self.ambiente, email='t@t.com', token='tk1', inviter=self.admin, guest=self.user
        )
        convite.accepted = True
        convite.save()
        self.assertTrue(convite.accepted)

    def test_convite_email(self):
        convite = AmbienteInvitations.objects.create(
            ambiente=self.ambiente, email='email@test.com', token='tk2', inviter=self.admin, guest=self.user
        )
        self.assertEqual(convite.email, 'email@test.com')

    def test_convite_guest_relation(self):
        convite = AmbienteInvitations.objects.create(
            ambiente=self.ambiente, email='g@t.com', token='tk3', inviter=self.admin, guest=self.user
        )
        self.assertEqual(convite.guest, self.user)

    def test_convite_inviter_relation(self):
        convite = AmbienteInvitations.objects.create(
            ambiente=self.ambiente, email='i@t.com', token='tk4', inviter=self.admin, guest=self.user
        )
        self.assertEqual(convite.inviter, self.admin)

    # =====================
    # Role
    # =====================

    def test_role_leitor_padrao(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.LEITOR, ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True}
        )
        self.assertTrue(role.pode_visualizar_atividades)
        self.assertFalse(role.pode_criar_atividades)

    def test_role_str(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.ADMINISTRADOR, ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True, 'pode_criar_atividades': True, 'pode_editar_atividades': True, 'pode_deletar_atividades': True}
        )
        self.assertIn('Administrador', str(role))

    def test_role_unique_por_ambiente(self):
        Role.objects.filter(nome=Role.CUSTOM, ambiente=self.ambiente).delete()
        Role.objects.create(nome=Role.CUSTOM, ambiente=self.ambiente)
        with self.assertRaises(Exception):
            Role.objects.create(nome=Role.CUSTOM, ambiente=self.ambiente)

    def test_role_editor_permissoes(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.EDITOR, ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True, 'pode_criar_atividades': True, 'pode_editar_atividades': True}
        )
        self.assertTrue(role.pode_editar_atividades)

    def test_role_admin_todas_permissoes(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.ADMINISTRADOR, ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True, 'pode_criar_atividades': True, 'pode_editar_atividades': True, 'pode_deletar_atividades': True}
        )
        self.assertTrue(role.pode_deletar_atividades)

    def test_role_ambiente_relation(self):
        role, _ = Role.objects.get_or_create(nome=Role.LEITOR, ambiente=self.ambiente, defaults={})
        self.assertEqual(role.ambiente, self.ambiente)

    # =====================
    # Participante
    # =====================

    def test_participante_criacao(self):
        role, _ = Role.objects.get_or_create(nome=Role.LEITOR, ambiente=self.ambiente, defaults={'pode_visualizar_atividades': True})
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        participante = Participante.objects.create(usuario=self.user, ambiente=self.ambiente, role=role)
        self.assertEqual(participante.usuario, self.user)
        self.assertEqual(participante.ambiente, self.ambiente)
        self.assertEqual(participante.role, role)

    def test_participante_str_com_role(self):
        role, _ = Role.objects.get_or_create(
            nome=Role.EDITOR, ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True, 'pode_criar_atividades': True, 'pode_editar_atividades': True}
        )
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        participante = Participante.objects.create(usuario=self.user, ambiente=self.ambiente, role=role
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

    def test_notificacao_marcar_lida(self):
        notif = Notificacao.objects.create(usuario=self.user, tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE, titulo='T', mensagem='M')
        notif.lida = True
        notif.save()
        notif.refresh_from_db()
        self.assertTrue(notif.lida)

    def test_notificacao_ambiente_relation(self):
        notif = Notificacao.objects.create(usuario=self.user, tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE, titulo='T', mensagem='M', ambiente=self.ambiente)
        self.assertEqual(notif.ambiente, self.ambiente)

    def test_notificacao_tipo_alocacao(self):
        notif = Notificacao.objects.create(usuario=self.user, tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE, titulo='Alocacao', mensagem='M')
        self.assertEqual(notif.tipo, Notificacao.TIPO_ALOCACAO_ATIVIDADE)


class AmbienteModelsAdicionaisTestCase(TestCase):
    """Testes adicionais para cobertura completa dos modelos do ambiente"""

    def setUp(self):
        self.admin = User.objects.create_user(username='amb_models_add_admin', password='123456')
        self.user = User.objects.create_user(username='amb_models_add_user', password='123456')
        self.ambiente = Ambiente.objects.create(nome='Ambiente Add', usuario_administrador=self.admin)

    def test_ambiente_criacao_simples(self):
        ambiente = Ambiente.objects.create(nome='Simples', usuario_administrador=self.admin)
        self.assertIsNotNone(ambiente.id)

    def test_ambiente_alterar_nome(self):
        self.ambiente.nome = 'Novo Nome'
        self.ambiente.save()
        self.ambiente.refresh_from_db()
        self.assertEqual(self.ambiente.nome, 'Novo Nome')

    def test_ambiente_alterar_tema(self):
        self.ambiente.tema = '#123456'
        self.ambiente.save()
        self.ambiente.refresh_from_db()
        self.assertEqual(self.ambiente.tema, '#123456')

    def test_ambiente_deletar(self):
        amb = Ambiente.objects.create(nome='Para Del', usuario_administrador=self.admin)
        amb_id = amb.id
        amb.delete()
        self.assertFalse(Ambiente.objects.filter(id=amb_id).exists())

    def test_role_criado_automaticamente(self):
        amb = Ambiente.objects.create(nome='Auto Roles', usuario_administrador=self.admin)
        roles = Role.objects.filter(ambiente=amb)
        self.assertGreaterEqual(roles.count(), 1)

    def test_participante_sem_role(self):
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        p = Participante.objects.create(usuario=self.user, ambiente=self.ambiente)
        self.assertIsNone(p.role)

    def test_participante_mudar_role(self):
        role1, _ = Role.objects.get_or_create(nome=Role.LEITOR, ambiente=self.ambiente, defaults={})
        role2, _ = Role.objects.get_or_create(nome=Role.EDITOR, ambiente=self.ambiente, defaults={})
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        p = Participante.objects.create(usuario=self.user, ambiente=self.ambiente, role=role1)
        p.role = role2
        p.save()
        p.refresh_from_db()
        self.assertEqual(p.role, role2)

    def test_convite_multiplos(self):
        user2 = User.objects.create_user(username='amb_models_add_u2', password='123')
        user3 = User.objects.create_user(username='amb_models_add_u3', password='123')
        AmbienteInvitations.objects.create(ambiente=self.ambiente, email='a@a.com', token='t1', inviter=self.admin, guest=user2)
        AmbienteInvitations.objects.create(ambiente=self.ambiente, email='b@b.com', token='t2', inviter=self.admin, guest=user3)
        convites = AmbienteInvitations.objects.filter(ambiente=self.ambiente)
        self.assertGreaterEqual(convites.count(), 2)

    def test_notificacao_delete(self):
        notif = Notificacao.objects.create(usuario=self.admin, tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE, titulo='T', mensagem='M')
        notif_id = notif.id
        notif.delete()
        self.assertFalse(Notificacao.objects.filter(id=notif_id).exists())

    def test_notificacao_multiplas(self):
        Notificacao.objects.create(usuario=self.admin, tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE, titulo='T1', mensagem='M1')
        Notificacao.objects.create(usuario=self.admin, tipo=Notificacao.TIPO_ALOCACAO_ATIVIDADE, titulo='T2', mensagem='M2')
        count = Notificacao.objects.filter(usuario=self.admin).count()
        self.assertGreaterEqual(count, 2)

    def test_ambiente_admin_relation(self):
        self.assertEqual(self.ambiente.usuario_administrador, self.admin)

    def test_role_pode_criar_false_default(self):
        role, _ = Role.objects.get_or_create(nome=Role.LEITOR, ambiente=self.ambiente, defaults={})
        self.assertFalse(role.pode_criar_atividades)

    def test_role_pode_deletar_false_default(self):
        role, _ = Role.objects.get_or_create(nome=Role.LEITOR, ambiente=self.ambiente, defaults={})
        self.assertFalse(role.pode_deletar_atividades)

    def test_participante_relation_ambiente(self):
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        p = Participante.objects.create(usuario=self.user, ambiente=self.ambiente)
        self.assertEqual(p.ambiente, self.ambiente)

    def test_participante_relation_usuario(self):
        Participante.objects.filter(usuario=self.user, ambiente=self.ambiente).delete()
        p = Participante.objects.create(usuario=self.user, ambiente=self.ambiente)
        self.assertEqual(p.usuario, self.user)

    def test_convite_deletar(self):
        user2 = User.objects.create_user(username='amb_models_add_u4', password='123')
        c = AmbienteInvitations.objects.create(ambiente=self.ambiente, email='d@d.com', token='td', inviter=self.admin, guest=user2)
        c_id = c.id
        c.delete()
        self.assertFalse(AmbienteInvitations.objects.filter(id=c_id).exists())
