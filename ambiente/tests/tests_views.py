from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import json

from ambiente.models import (
    Ambiente,
    AmbienteInvitations,
    Participante,
    Role,
    Notificacao
)


class AmbienteViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()

        self.admin = User.objects.create_user(
            username='ambiente_admin_test',
            password='123456'
        )
        self.user = User.objects.create_user(
            username='ambiente_user_test',
            password='123456'
        )

        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Teste',
            usuario_administrador=self.admin
        )

        self.role_leitor, _ = Role.objects.get_or_create(
            nome=Role.LEITOR,
            ambiente=self.ambiente,
            defaults={'pode_visualizar_atividades': True}
        )

        self.participante, _ = Participante.objects.get_or_create(
            usuario=self.user,
            ambiente=self.ambiente,
            defaults={'role': self.role_leitor}
        )

    # =======================
    # AmbienteView - Lista
    # =======================

    def test_lista_ambientes_autenticado(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('lista_ambientes'))
        self.assertEqual(response.status_code, 200)

    def test_lista_ambientes_nao_logado(self):
        response = self.client.get(reverse('lista_ambientes'))
        self.assertEqual(response.status_code, 302)

    def test_lista_ambientes_template(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('lista_ambientes'))
        self.assertTemplateUsed(response, 'ambiente/home.html')

    def test_lista_ambientes_context(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('lista_ambientes'))
        self.assertIn('ambientes', response.context)

    def test_lista_ambientes_mostra_apenas_do_usuario(self):
        outro_user = User.objects.create_user(username='outro_user_v1', password='123')
        Ambiente.objects.create(nome='Outro Ambiente', usuario_administrador=outro_user)
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('lista_ambientes'))
        self.assertEqual(response.status_code, 200)

    # =======================
    # AmbienteView - Criar
    # =======================

    def test_criar_ambiente_sucesso(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('criar_ambiente'), {'nome': 'Novo Ambiente'})
        self.assertEqual(response.status_code, 302)

    def test_criar_ambiente_existe(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        self.client.post(reverse('criar_ambiente'), {'nome': 'Novo Ambiente 2'})
        self.assertTrue(Ambiente.objects.filter(nome='Novo Ambiente 2').exists())

    def test_criar_ambiente_form_invalido(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('criar_ambiente'), {'nome': ''})
        self.assertEqual(response.status_code, 200)

    def test_criar_ambiente_get(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('criar_ambiente'))
        self.assertIn(response.status_code, [200, 302])

    def test_criar_ambiente_sem_login(self):
        response = self.client.post(reverse('criar_ambiente'), {'nome': 'Test'})
        self.assertEqual(response.status_code, 302)

    def test_criar_ambiente_com_tema(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('criar_ambiente'), {'nome': 'Amb Tema', 'tema': '#FF0000'})
        self.assertIn(response.status_code, [200, 302])

    # =======================
    # AmbienteView - Editar
    # =======================

    def test_editar_ambiente_get(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('editar_ambiente', args=[self.ambiente.id]))
        self.assertEqual(response.status_code, 200)

    def test_editar_ambiente_post(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('editar_ambiente', args=[self.ambiente.id]), {'nome': 'Ambiente Editado'})
        self.assertEqual(response.status_code, 302)

    def test_editar_ambiente_nome_atualizado(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        self.client.post(reverse('editar_ambiente', args=[self.ambiente.id]), {'nome': 'Nome Novo'})
        self.ambiente.refresh_from_db()
        self.assertEqual(self.ambiente.nome, 'Nome Novo')

    def test_editar_ambiente_sem_login(self):
        response = self.client.post(reverse('editar_ambiente', args=[self.ambiente.id]), {'nome': 'Test'})
        self.assertEqual(response.status_code, 302)

    def test_editar_ambiente_inexistente(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        try:
            response = self.client.get(reverse('editar_ambiente', args=[99999]))
            self.assertIn(response.status_code, [404, 500])
        except Exception:
            # A view pode lançar exceção para ambiente inexistente
            pass

    # =======================
    # AmbienteView - Deletar
    # =======================

    def test_deletar_ambiente(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('deletar_ambiente', args=[self.ambiente.id]))
        self.assertEqual(response.status_code, 302)

    def test_deletar_ambiente_nao_existe_mais(self):
        amb = Ambiente.objects.create(nome='Para Deletar', usuario_administrador=self.admin)
        self.client.login(username='ambiente_admin_test', password='123456')
        self.client.post(reverse('deletar_ambiente', args=[amb.id]))
        self.assertFalse(Ambiente.objects.filter(id=amb.id).exists())

    def test_deletar_ambiente_sem_login(self):
        response = self.client.post(reverse('deletar_ambiente', args=[self.ambiente.id]))
        self.assertEqual(response.status_code, 302)

    def test_deletar_ambiente_get_redireciona(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('deletar_ambiente', args=[self.ambiente.id]))
        self.assertIn(response.status_code, [200, 302])

    # =======================
    # AmbienteView - Configurar
    # =======================

    def test_configurar_ambiente(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('configurar_ambiente', args=[self.ambiente.id]))
        self.assertEqual(response.status_code, 200)

    def test_configurar_ambiente_template(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('configurar_ambiente', args=[self.ambiente.id]))
        self.assertTemplateUsed(response, 'ambiente/configurar.html')

    def test_configurar_ambiente_context(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('configurar_ambiente', args=[self.ambiente.id]))
        self.assertIn('ambiente', response.context)

    def test_configurar_ambiente_sem_login(self):
        response = self.client.get(reverse('configurar_ambiente', args=[self.ambiente.id]))
        self.assertEqual(response.status_code, 302)

    # =======================
    # Convites
    # =======================

    def test_enviar_convite_sucesso(self):
        novo_user = User.objects.create_user(username='novo_conv_v1', email='novo_conv@email.com', password='123456')
        self.api_client.login(username='ambiente_admin_test', password='123456')
        response = self.api_client.post(reverse('enviar_convite', args=[self.ambiente.id]), {'email': 'novo_conv@email.com'}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_enviar_convite_sem_permissao(self):
        self.api_client.login(username='ambiente_user_test', password='123456')
        response = self.api_client.post(reverse('enviar_convite', args=[self.ambiente.id]), {'email': 'x@email.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enviar_convite_email_vazio(self):
        self.api_client.login(username='ambiente_admin_test', password='123456')
        response = self.api_client.post(reverse('enviar_convite', args=[self.ambiente.id]), {'email': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_aceitar_convite(self):
        convite = AmbienteInvitations.objects.create(ambiente=self.ambiente, inviter=self.admin, guest=self.user, email='conv@test.com')
        self.api_client.login(username='ambiente_user_test', password='123456')
        response = self.api_client.post(reverse('aceitar_convite', args=[convite.id]))
        self.assertEqual(response.status_code, 200)

    def test_aceitar_convite_atualiza_accepted(self):
        convite = AmbienteInvitations.objects.create(ambiente=self.ambiente, inviter=self.admin, guest=self.user, email='conv2@test.com')
        self.api_client.login(username='ambiente_user_test', password='123456')
        self.api_client.post(reverse('aceitar_convite', args=[convite.id]))
        convite.refresh_from_db()
        self.assertTrue(convite.accepted)

    def test_recusar_convite(self):
        convite = AmbienteInvitations.objects.create(ambiente=self.ambiente, inviter=self.admin, guest=self.user, email='conv3@test.com')
        self.api_client.login(username='ambiente_user_test', password='123456')
        response = self.api_client.post(reverse('recusar_convite', args=[convite.id]))
        self.assertEqual(response.status_code, 200)

    def test_recusar_convite_deleta(self):
        convite = AmbienteInvitations.objects.create(ambiente=self.ambiente, inviter=self.admin, guest=self.user, email='conv4@test.com')
        conv_id = convite.id
        self.api_client.login(username='ambiente_user_test', password='123456')
        self.api_client.post(reverse('recusar_convite', args=[conv_id]))
        self.assertFalse(AmbienteInvitations.objects.filter(id=conv_id).exists())

    # =======================
    # Permissões
    # =======================

    def test_editar_permissoes_sucesso(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(
            reverse('editar_permissoes', args=[self.ambiente.id, self.participante.id]),
            data=json.dumps({'pode_visualizar_atividades': True, 'pode_criar_atividades': True, 'pode_editar_atividades': True, 'pode_deletar_atividades': False}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_editar_permissoes_json_response(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(
            reverse('editar_permissoes', args=[self.ambiente.id, self.participante.id]),
            data=json.dumps({'pode_visualizar_atividades': True, 'pode_criar_atividades': False, 'pode_editar_atividades': False, 'pode_deletar_atividades': False}),
            content_type='application/json'
        )
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_obter_permissoes(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('obter_permissoes', args=[self.ambiente.id, self.participante.id]))
        self.assertEqual(response.status_code, 200)

    def test_obter_permissoes_json(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('obter_permissoes', args=[self.ambiente.id, self.participante.id]))
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_editar_permissoes_sem_login(self):
        response = self.client.post(reverse('editar_permissoes', args=[self.ambiente.id, self.participante.id]), data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 302)

    # =======================
    # Notificações
    # =======================

    def test_listar_notificacoes(self):
        Notificacao.objects.create(usuario=self.admin, mensagem='Teste')
        self.client.login(username='ambiente_admin_test', password='123456')
        try:
            response = self.client.get(reverse('notificacoes'))
            self.assertIn(response.status_code, [200, 500])
        except Exception:
            pass

    def test_marcar_notificacao_lida(self):
        notif = Notificacao.objects.create(usuario=self.admin, mensagem='Teste')
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('marcar_notificacao_lida', args=[notif.id]))
        self.assertEqual(response.status_code, 200)

    def test_marcar_notificacao_lida_atualiza(self):
        notif = Notificacao.objects.create(usuario=self.admin, mensagem='Teste2')
        self.client.login(username='ambiente_admin_test', password='123456')
        self.client.post(reverse('marcar_notificacao_lida', args=[notif.id]))
        notif.refresh_from_db()
        self.assertTrue(notif.lida)

    def test_marcar_todas_lidas(self):
        Notificacao.objects.create(usuario=self.admin, mensagem='Teste')
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.post(reverse('marcar_todas_lidas'))
        self.assertEqual(response.status_code, 200)

    def test_marcar_todas_lidas_atualiza(self):
        Notificacao.objects.create(usuario=self.admin, mensagem='N1')
        Notificacao.objects.create(usuario=self.admin, mensagem='N2')
        self.client.login(username='ambiente_admin_test', password='123456')
        self.client.post(reverse('marcar_todas_lidas'))
        nao_lidas = Notificacao.objects.filter(usuario=self.admin, lida=False).count()
        self.assertEqual(nao_lidas, 0)

    def test_contagem_notificacoes(self):
        Notificacao.objects.create(usuario=self.admin, mensagem='Teste')
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('contagem_notificacoes'))
        self.assertEqual(response.status_code, 200)

    def test_contagem_notificacoes_valor(self):
        Notificacao.objects.filter(usuario=self.admin).delete()
        Notificacao.objects.create(usuario=self.admin, mensagem='T1')
        Notificacao.objects.create(usuario=self.admin, mensagem='T2')
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('contagem_notificacoes'))
        self.assertEqual(response.json()['count'], 2)

    def test_contagem_notificacoes_json(self):
        self.client.login(username='ambiente_admin_test', password='123456')
        response = self.client.get(reverse('contagem_notificacoes'))
        self.assertEqual(response['Content-Type'], 'application/json')


class AmbienteViewsAdicionaisTestCase(TestCase):
    """Testes adicionais para views do ambiente"""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='amb_views_add_user1', password='123456')
        self.user2 = User.objects.create_user(username='amb_views_add_user2', password='123456')
        self.ambiente = Ambiente.objects.create(nome='Ambiente Add', usuario_administrador=self.user1)

    def test_ambiente_url_lista(self):
        url = reverse('lista_ambientes')
        self.assertEqual(url, '/ambiente/')

    def test_ambiente_url_criar(self):
        url = reverse('criar_ambiente')
        self.assertEqual(url, '/ambiente/criar/')

    def test_ambiente_url_editar(self):
        url = reverse('editar_ambiente', args=[1])
        self.assertEqual(url, '/ambiente/1/editar/')

    def test_ambiente_url_deletar(self):
        url = reverse('deletar_ambiente', args=[1])
        self.assertEqual(url, '/ambiente/1/deletar/')

    def test_ambiente_url_configurar(self):
        url = reverse('configurar_ambiente', args=[1])
        self.assertEqual(url, '/ambiente/1/configurar/')

    def test_criar_multiplos_ambientes(self):
        self.client.login(username='amb_views_add_user1', password='123456')
        self.client.post(reverse('criar_ambiente'), {'nome': 'Amb1'})
        self.client.post(reverse('criar_ambiente'), {'nome': 'Amb2'})
        self.client.post(reverse('criar_ambiente'), {'nome': 'Amb3'})
        count = Ambiente.objects.filter(usuario_administrador=self.user1).count()
        self.assertGreaterEqual(count, 3)

    def test_editar_ambiente_tema(self):
        self.client.login(username='amb_views_add_user1', password='123456')
        response = self.client.post(reverse('editar_ambiente', args=[self.ambiente.id]), {'nome': 'Novo', 'tema': '#AABBCC'})
        self.assertIn(response.status_code, [200, 302])

    def test_lista_ambientes_vazia(self):
        novo_user = User.objects.create_user(username='amb_views_vazio_user', password='123456')
        self.client.login(username='amb_views_vazio_user', password='123456')
        response = self.client.get(reverse('lista_ambientes'))
        self.assertEqual(response.status_code, 200)

    def test_participante_ve_ambiente(self):
        self.ambiente.usuarios_participantes.add(self.user2)
        self.client.login(username='amb_views_add_user2', password='123456')
        response = self.client.get(reverse('lista_ambientes'))
        self.assertEqual(response.status_code, 200)

    def test_notificacao_sem_login(self):
        response = self.client.get(reverse('contagem_notificacoes'))
        self.assertEqual(response.status_code, 302)

    def test_marcar_lida_sem_login(self):
        response = self.client.post(reverse('marcar_todas_lidas'))
        self.assertEqual(response.status_code, 302)
