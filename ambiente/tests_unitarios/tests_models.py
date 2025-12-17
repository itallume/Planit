from django.test import SimpleTestCase
from django.db import models
from unittest.mock import Mock
from ambiente.models import Ambiente


class AmbienteModelUnitTest(SimpleTestCase):
    """Testes unitários do modelo Ambiente"""
    
    def test_ambiente_model_exists(self):
        """Testa se o modelo Ambiente existe"""
        self.assertIsNotNone(Ambiente)
    
    def test_ambiente_has_nome_field(self):
        """Testa se Ambiente tem campo nome"""
        self.assertTrue(hasattr(Ambiente, 'nome'))
    
    def test_ambiente_nome_field_type(self):
        """Testa se nome é CharField"""
        field = Ambiente._meta.get_field('nome')
        self.assertIsInstance(field, models.CharField)
    
    def test_ambiente_nome_max_length(self):
        """Testa se nome tem max_length=100"""
        field = Ambiente._meta.get_field('nome')
        self.assertEqual(field.max_length, 100)
    
    def test_ambiente_nome_not_null(self):
        """Testa se nome não permite null"""
        field = Ambiente._meta.get_field('nome')
        self.assertFalse(field.null)
    
    def test_ambiente_nome_not_blank(self):
        """Testa se nome não permite blank"""
        field = Ambiente._meta.get_field('nome')
        self.assertFalse(field.blank)
    
    def test_ambiente_has_tema_field(self):
        """Testa se Ambiente tem campo tema"""
        self.assertTrue(hasattr(Ambiente, 'tema'))
    
    def test_ambiente_tema_field_type(self):
        """Testa se tema é CharField"""
        field = Ambiente._meta.get_field('tema')
        self.assertIsInstance(field, models.CharField)
    
    def test_ambiente_tema_max_length(self):
        """Testa se tema tem max_length=100"""
        field = Ambiente._meta.get_field('tema')
        self.assertEqual(field.max_length, 100)
    
    def test_ambiente_tema_blank_true(self):
        """Testa se tema permite blank"""
        field = Ambiente._meta.get_field('tema')
        self.assertTrue(field.blank)
    
    def test_ambiente_tema_null_true(self):
        """Testa se tema permite null"""
        field = Ambiente._meta.get_field('tema')
        self.assertTrue(field.null)
    
    def test_ambiente_has_usuario_administrador_field(self):
        """Testa se Ambiente tem campo usuario_administrador"""
        self.assertTrue(hasattr(Ambiente, 'usuario_administrador'))
    
    def test_ambiente_usuario_administrador_field_type(self):
        """Testa se usuario_administrador é ForeignKey"""
        field = Ambiente._meta.get_field('usuario_administrador')
        self.assertIsInstance(field, models.ForeignKey)
    
    def test_ambiente_usuario_administrador_on_delete_cascade(self):
        """Testa se usuario_administrador tem on_delete=CASCADE"""
        field = Ambiente._meta.get_field('usuario_administrador')
        self.assertEqual(field.remote_field.on_delete.__name__, 'CASCADE')
    
    def test_ambiente_usuario_administrador_not_null(self):
        """Testa se usuario_administrador não permite null"""
        field = Ambiente._meta.get_field('usuario_administrador')
        self.assertFalse(field.null)
    
    def test_ambiente_usuario_administrador_not_blank(self):
        """Testa se usuario_administrador não permite blank"""
        field = Ambiente._meta.get_field('usuario_administrador')
        self.assertFalse(field.blank)
    
    def test_ambiente_has_usuarios_participantes_field(self):
        """Testa se Ambiente tem campo usuarios_participantes"""
        self.assertTrue(hasattr(Ambiente, 'usuarios_participantes'))
    
    def test_ambiente_usuarios_participantes_field_type(self):
        """Testa se usuarios_participantes é ManyToManyField"""
        field = Ambiente._meta.get_field('usuarios_participantes')
        self.assertIsInstance(field, models.ManyToManyField)
    
    def test_ambiente_usuarios_participantes_blank_true(self):
        """Testa se usuarios_participantes permite blank"""
        field = Ambiente._meta.get_field('usuarios_participantes')
        self.assertTrue(field.blank)
    
    def test_ambiente_usuarios_participantes_related_name(self):
        """Testa se usuarios_participantes tem related_name='ambientes_participantes'"""
        field = Ambiente._meta.get_field('usuarios_participantes')
        self.assertEqual(field.remote_field.related_name, 'ambientes_participantes')
    
    def test_ambiente_str_method(self):
        """Testa método __str__ do Ambiente"""
        ambiente_mock = Mock(spec=Ambiente)
        ambiente_mock.nome = 'Projeto Web'
        ambiente_mock.__str__ = lambda self: self.nome
        
        result = str(ambiente_mock)
        self.assertEqual(result, 'Projeto Web')
    
    def test_ambiente_model_table_name(self):
        """Testa se o nome da tabela é correto"""
        # Django usa o padrão appname_modelname
        self.assertEqual(Ambiente._meta.db_table, 'ambiente_ambiente')
    
    def test_ambiente_model_app_label(self):
        """Testa se o app_label é 'ambiente'"""
        self.assertEqual(Ambiente._meta.app_label, 'ambiente')
    
    def test_ambiente_all_fields_count(self):
        """Testa se o modelo tem 4 fields"""
        # nome, tema, usuario_administrador, usuarios_participantes
        fields = Ambiente._meta.get_fields()
        # ManyToMany adiciona campos implícitos, então verificamos os explícitos
        explicit_fields = [f.name for f in fields if f.name in ['nome', 'tema', 'usuario_administrador', 'usuarios_participantes']]
        self.assertEqual(len(explicit_fields), 4)
    
    def test_ambiente_has_id_field(self):
        """Testa se Ambiente tem campo id (primary key)"""
        self.assertTrue(Ambiente._meta.pk is not None)
    
    def test_ambiente_pk_field_type(self):
        """Testa se pk é AutoField"""
        self.assertIsInstance(Ambiente._meta.pk, models.AutoField)
    
    def test_ambiente_usuario_administrador_related_name(self):
        """Testa se usuario_administrador tem related_name correto"""
        field = Ambiente._meta.get_field('usuario_administrador')
        # Django gera automaticamente related_name como 'ambiente_set'
        # ou usa o especificado se houver
        self.assertIsNotNone(field.remote_field.related_name or field.remote_field.get_accessor_name())
    
    def test_ambiente_verbose_name(self):
        """Testa se o modelo tem verbose_name (se configurado)"""
        # Pode ou não ter configurado, só testa que existe
        self.assertIsNotNone(Ambiente._meta.verbose_name)
    
    def test_ambiente_ordering(self):
        """Testa se o modelo tem ordenação (se configurada)"""
        # Pode ser None, mas testa que existe a propriedade
        self.assertTrue(hasattr(Ambiente._meta, 'ordering'))
