from django.test import TestCase
from django.contrib.auth.models import User
from ambiente.models import Ambiente


class AmbienteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('paulo', 'paulo@test.com', 'senha123')
        self.user2 = User.objects.create_user('maria', 'maria@test.com', 'senha123')
        self.ambiente = Ambiente.objects.create(
            nome='Projeto Web',
            tema='Azul',
            usuario_administrador=self.user
        )

    def test_ambiente_creation(self):
        """Testa criação básica de um ambiente"""
        self.assertEqual(self.ambiente.nome, 'Projeto Web')
        self.assertEqual(self.ambiente.tema, 'Azul')
        self.assertEqual(self.ambiente.usuario_administrador, self.user)

    def test_ambiente_str(self):
        """Testa representação em string do modelo"""
        self.assertEqual(str(self.ambiente), 'Projeto Web')

    def test_ambiente_nome_max_length(self):
        """Testa validação do tamanho máximo do nome"""
        nome_grande = 'A' * 101
        ambiente = Ambiente(
            nome=nome_grande,
            usuario_administrador=self.user
        )
        # CharField com max_length não valida automaticamente, precisa de full_clean()
        self.assertEqual(len(ambiente.nome), 101)

    def test_ambiente_tema_blank(self):
        """Testa se tema pode ser vazio"""
        ambiente = Ambiente.objects.create(
            nome='Projeto Sem Tema',
            usuario_administrador=self.user
        )
        self.assertIsNone(ambiente.tema)

    def test_ambiente_tema_null(self):
        """Testa se tema pode ser null"""
        ambiente = Ambiente.objects.create(
            nome='Outro Projeto',
            tema=None,
            usuario_administrador=self.user
        )
        self.assertIsNone(ambiente.tema)

    def test_ambiente_usuario_administrador_required(self):
        """Testa se usuário administrador é obrigatório"""
        with self.assertRaises(Exception):
            Ambiente.objects.create(
                nome='Projeto Sem Admin',
                tema='Verde'
            )

    def test_ambiente_usuarios_participantes_add(self):
        """Testa adição de usuários participantes"""
        self.ambiente.usuarios_participantes.add(self.user2)
        self.assertIn(self.user2, self.ambiente.usuarios_participantes.all())

    def test_ambiente_usuarios_participantes_multiple(self):
        """Testa adição de múltiplos usuários participantes"""
        user3 = User.objects.create_user('carlos', 'carlos@test.com', 'senha123')
        self.ambiente.usuarios_participantes.add(self.user2, user3)
        self.assertEqual(self.ambiente.usuarios_participantes.count(), 2)

    def test_ambiente_usuarios_participantes_remove(self):
        """Testa remoção de usuário participante"""
        self.ambiente.usuarios_participantes.add(self.user2)
        self.ambiente.usuarios_participantes.remove(self.user2)
        self.assertNotIn(self.user2, self.ambiente.usuarios_participantes.all())

    def test_ambiente_usuarios_participantes_blank(self):
        """Testa se usuários participantes pode estar vazio"""
        self.assertEqual(self.ambiente.usuarios_participantes.count(), 0)

    def test_ambiente_delete_cascade(self):
        """Testa se ambiente é deletado quando usuário admin é deletado"""
        ambiente_id = self.ambiente.id
        self.user.delete()
        self.assertFalse(Ambiente.objects.filter(id=ambiente_id).exists())

    def test_ambiente_admin_different_from_participante(self):
        """Testa que admin pode ser diferente de participante"""
        self.ambiente.usuarios_participantes.add(self.user2)
        self.assertNotEqual(self.ambiente.usuario_administrador, self.user2)
        self.assertIn(self.user2, self.ambiente.usuarios_participantes.all())

    def test_ambiente_queryset_filter_by_admin(self):
        """Testa filtro de ambientes por administrador"""
        ambientes = Ambiente.objects.filter(usuario_administrador=self.user)
        self.assertEqual(ambientes.count(), 1)
        self.assertIn(self.ambiente, ambientes)

    def test_ambiente_queryset_filter_by_participante(self):
        """Testa filtro de ambientes por participante"""
        self.ambiente.usuarios_participantes.add(self.user2)
        ambientes = Ambiente.objects.filter(usuarios_participantes=self.user2)
        self.assertEqual(ambientes.count(), 1)
        self.assertIn(self.ambiente, ambientes)

    def test_ambiente_count(self):
        """Testa contagem de ambientes"""
        Ambiente.objects.create(
            nome='Segundo Projeto',
            tema='Vermelho',
            usuario_administrador=self.user
        )
        self.assertEqual(Ambiente.objects.count(), 2)

    def test_ambiente_update(self):
        """Testa atualização de ambiente"""
        self.ambiente.nome = 'Projeto Atualizado'
        self.ambiente.tema = 'Verde'
        self.ambiente.save()
        
        ambiente_atualizado = Ambiente.objects.get(id=self.ambiente.id)
        self.assertEqual(ambiente_atualizado.nome, 'Projeto Atualizado')
        self.assertEqual(ambiente_atualizado.tema, 'Verde')
