from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ambiente.models import Ambiente


class ListAmbientesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')
        self.url = reverse('lista_ambientes')
        # Create test ambientes
        for i in range(7):
            Ambiente.objects.create(
                nome=f'Ambiente {i}',
                tema=f'Tema {i}',
                usuario_administrador=self.user
            )

    def test_list_ambientes_status_code(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_ambientes_template_used(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'ambiente/home.html')

    def test_list_ambientes_context(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertTrue('ambientes' in response.context)
        self.assertTrue('form' in response.context)

    def test_list_ambientes_shows_all_user_ambientes(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        ambientes = response.context['ambientes']
        self.assertEqual(len(ambientes), 7)

    def test_list_ambientes_redirect_without_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/entrar/', response.url)


class DetalheAmbienteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')
        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Test',
            tema='Azul',
            usuario_administrador=self.user
        )
        self.url = reverse('detalhe_ambiente', args=[self.ambiente.id])

    def test_detalhe_ambiente_status_code(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_detalhe_ambiente_template_used(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'ambiente/detalhe.html')

    def test_detalhe_ambiente_context(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['ambiente'], self.ambiente)
        self.assertTrue('atividades' in response.context)

    def test_detalhe_ambiente_not_found(self):
        self.client.login(username='paulo', password='senha123')
        with self.assertRaises(Ambiente.DoesNotExist):
            self.client.get(reverse('detalhe_ambiente', args=[9999]))


class CriarAmbienteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')
        self.url = reverse('criar_ambiente')

    def test_criar_ambiente_get_redirect(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 302)

    def test_criar_ambiente_post_valid(self):
        self.client.login(username='paulo', password='senha123')
        data = {'nome': 'Novo Ambiente', 'tema': 'Verde'}
        response = self.client.post(self.url, data)
        self.assertTrue(Ambiente.objects.filter(nome='Novo Ambiente').exists())
        ambiente = Ambiente.objects.get(nome='Novo Ambiente')
        self.assertEqual(ambiente.usuario_administrador, self.user)

    def test_criar_ambiente_post_invalid(self):
        self.client.login(username='paulo', password='senha123')
        data = {'nome': '', 'tema': 'Verde'}  # Nome vazio
        response = self.client.post(self.url, data)
        self.assertTemplateUsed(response, 'ambiente/home.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_criar_ambiente_redirect_without_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class EditarAmbienteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')
        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Original',
            tema='Azul',
            usuario_administrador=self.user
        )
        self.url = reverse('editar_ambiente', args=[self.ambiente.id])

    def test_editar_ambiente_get(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ambiente/home.html')

    def test_editar_ambiente_post_valid(self):
        self.client.login(username='paulo', password='senha123')
        data = {'nome': 'Ambiente Atualizado', 'tema': 'Vermelho'}
        response = self.client.post(self.url, data)
        self.ambiente.refresh_from_db()
        self.assertEqual(self.ambiente.nome, 'Ambiente Atualizado')
        self.assertEqual(self.ambiente.tema, 'Vermelho')

    def test_editar_ambiente_post_invalid(self):
        self.client.login(username='paulo', password='senha123')
        data = {'nome': '', 'tema': 'Verde'}  # Nome vazio
        response = self.client.post(self.url, data)
        self.assertTemplateUsed(response, 'ambiente/home.html')
        self.assertFalse(response.context['form_editar'].is_valid())


class DeletarAmbienteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')
        self.ambiente = Ambiente.objects.create(
            nome='Ambiente para Deletar',
            tema='Azul',
            usuario_administrador=self.user
        )
        self.url = reverse('deletar_ambiente', args=[self.ambiente.id])

    def test_deletar_ambiente_post(self):
        self.client.login(username='paulo', password='senha123')
        ambiente_id = self.ambiente.id
        response = self.client.post(self.url)
        self.assertFalse(Ambiente.objects.filter(id=ambiente_id).exists())

    def test_deletar_ambiente_get_redirect(self):
        self.client.login(username='paulo', password='senha123')
        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 302)
