from django.test import SimpleTestCase
from unittest.mock import Mock, patch, MagicMock
import inspect
from ambiente.views import AmbienteView
from ambiente.forms import AmbienteForm
from ambiente.models import Ambiente


class ListaAmbientesViewUnitTest(SimpleTestCase):
    """Testes unitários da função lista_ambientes"""
    
    def test_lista_ambientes_is_callable(self):
        """Testa se a função lista_ambientes existe e é callable"""
        self.assertTrue(callable(AmbienteView.lista_ambientes))
    
    def test_lista_ambientes_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        # Verifica se tem __wrapped__ (indica decorador)
        self.assertTrue(hasattr(AmbienteView.lista_ambientes, '__wrapped__'))
    
    def test_lista_ambientes_renders_template(self):
        """Testa se a função usa render com template 'ambiente/home.html'"""
        source = inspect.getsource(AmbienteView.lista_ambientes)
        self.assertIn("render", source)
        self.assertIn("'ambiente/home.html'", source)
    
    def test_lista_ambientes_filters_by_user(self):
        """Testa se filtra ambientes por usuário admin ou participante"""
        source = inspect.getsource(AmbienteView.lista_ambientes)
        self.assertIn("usuario_administrador", source)
        self.assertIn("usuarios_participantes", source)
        self.assertIn("request.user", source)
    
    def test_lista_ambientes_uses_distinct(self):
        """Testa se usa distinct() para evitar duplicatas"""
        source = inspect.getsource(AmbienteView.lista_ambientes)
        self.assertIn("distinct", source)
    
    def test_lista_ambientes_annotates_counts(self):
        """Testa se faz anotações de contagem"""
        source = inspect.getsource(AmbienteView.lista_ambientes)
        self.assertIn("annotate", source)
        self.assertIn("Count", source)
    
    def test_lista_ambientes_context_includes_form(self):
        """Testa se o contexto inclui formulário"""
        source = inspect.getsource(AmbienteView.lista_ambientes)
        self.assertIn("AmbienteForm", source)
        self.assertIn("'form'", source)
    
    def test_lista_ambientes_context_includes_ambientes(self):
        """Testa se o contexto inclui ambientes"""
        source = inspect.getsource(AmbienteView.lista_ambientes)
        self.assertIn("'ambientes'", source)


class DetalheAmbienteViewUnitTest(SimpleTestCase):
    """Testes unitários da função detalhe_ambiente"""
    
    def test_detalhe_ambiente_is_callable(self):
        """Testa se a função detalhe_ambiente existe e é callable"""
        self.assertTrue(callable(AmbienteView.detalhe_ambiente))
    
    def test_detalhe_ambiente_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        self.assertTrue(hasattr(AmbienteView.detalhe_ambiente, '__wrapped__'))
    
    def test_detalhe_ambiente_receives_ambiente_id(self):
        """Testa se a função recebe ambiente_id como parâmetro"""
        source = inspect.getsource(AmbienteView.detalhe_ambiente)
        self.assertIn("ambiente_id", source)
    
    def test_detalhe_ambiente_gets_by_id(self):
        """Testa se usa Ambiente.objects.get(id=ambiente_id)"""
        source = inspect.getsource(AmbienteView.detalhe_ambiente)
        self.assertIn("Ambiente.objects.get", source)
        self.assertIn("ambiente_id", source)
    
    def test_detalhe_ambiente_gets_atividades(self):
        """Testa se busca atividades do ambiente"""
        source = inspect.getsource(AmbienteView.detalhe_ambiente)
        self.assertIn("atividade_set", source)
    
    def test_detalhe_ambiente_renders_template(self):
        """Testa se usa render com template 'ambiente/detalhe.html'"""
        source = inspect.getsource(AmbienteView.detalhe_ambiente)
        self.assertIn("render", source)
        self.assertIn("'ambiente/detalhe.html'", source)
    
    def test_detalhe_ambiente_context_includes_ambiente(self):
        """Testa se o contexto inclui ambiente"""
        source = inspect.getsource(AmbienteView.detalhe_ambiente)
        self.assertIn("'ambiente'", source)
    
    def test_detalhe_ambiente_context_includes_atividades(self):
        """Testa se o contexto inclui atividades"""
        source = inspect.getsource(AmbienteView.detalhe_ambiente)
        self.assertIn("'atividades'", source)


class CriarAmbienteViewUnitTest(SimpleTestCase):
    """Testes unitários da função criar_ambiente"""
    
    def test_criar_ambiente_is_callable(self):
        """Testa se a função criar_ambiente existe e é callable"""
        self.assertTrue(callable(AmbienteView.criar_ambiente))
    
    def test_criar_ambiente_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        self.assertTrue(hasattr(AmbienteView.criar_ambiente, '__wrapped__'))
    
    def test_criar_ambiente_receives_request(self):
        """Testa se a função recebe request como parâmetro"""
        source = inspect.getsource(AmbienteView.criar_ambiente)
        self.assertIn("request", source)
    
    def test_criar_ambiente_checks_post_method(self):
        """Testa se verifica se é POST"""
        source = inspect.getsource(AmbienteView.criar_ambiente)
        self.assertIn("request.method", source)
        self.assertIn("'POST'", source)
    
    def test_criar_ambiente_uses_form(self):
        """Testa se usa AmbienteForm"""
        source = inspect.getsource(AmbienteView.criar_ambiente)
        self.assertIn("AmbienteForm", source)
    
    def test_criar_ambiente_sets_admin_user(self):
        """Testa se define usuario_administrador como request.user"""
        source = inspect.getsource(AmbienteView.criar_ambiente)
        self.assertIn("usuario_administrador", source)
        self.assertIn("request.user", source)
    
    def test_criar_ambiente_redirects_on_success(self):
        """Testa se redireciona para lista_ambientes"""
        source = inspect.getsource(AmbienteView.criar_ambiente)
        self.assertIn("redirect", source)
        self.assertIn("'lista_ambientes'", source)
    
    def test_criar_ambiente_renders_on_invalid(self):
        """Testa se renderiza template com erros"""
        source = inspect.getsource(AmbienteView.criar_ambiente)
        self.assertIn("is_valid", source)
        self.assertIn("render", source)


class EditarAmbienteViewUnitTest(SimpleTestCase):
    """Testes unitários da função editar_ambiente"""
    
    def test_editar_ambiente_is_callable(self):
        """Testa se a função editar_ambiente existe e é callable"""
        self.assertTrue(callable(AmbienteView.editar_ambiente))
    
    def test_editar_ambiente_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        self.assertTrue(hasattr(AmbienteView.editar_ambiente, '__wrapped__'))
    
    def test_editar_ambiente_receives_ambiente_id(self):
        """Testa se recebe ambiente_id como parâmetro"""
        source = inspect.getsource(AmbienteView.editar_ambiente)
        self.assertIn("ambiente_id", source)
    
    def test_editar_ambiente_gets_by_id(self):
        """Testa se busca ambiente por id"""
        source = inspect.getsource(AmbienteView.editar_ambiente)
        self.assertIn("Ambiente.objects.get", source)
    
    def test_editar_ambiente_checks_post_method(self):
        """Testa se verifica método POST"""
        source = inspect.getsource(AmbienteView.editar_ambiente)
        self.assertIn("request.method", source)
        self.assertIn("'POST'", source)
    
    def test_editar_ambiente_uses_form_with_instance(self):
        """Testa se usa formulário com instância"""
        source = inspect.getsource(AmbienteView.editar_ambiente)
        self.assertIn("AmbienteForm", source)
        self.assertIn("instance", source)
    
    def test_editar_ambiente_saves_form(self):
        """Testa se salva o formulário"""
        source = inspect.getsource(AmbienteView.editar_ambiente)
        self.assertIn("form.save", source)
    
    def test_editar_ambiente_redirects_on_success(self):
        """Testa se redireciona para lista"""
        source = inspect.getsource(AmbienteView.editar_ambiente)
        self.assertIn("redirect", source)


class DeletarAmbienteViewUnitTest(SimpleTestCase):
    """Testes unitários da função deletar_ambiente"""
    
    def test_deletar_ambiente_is_callable(self):
        """Testa se a função deletar_ambiente existe e é callable"""
        self.assertTrue(callable(AmbienteView.deletar_ambiente))
    
    def test_deletar_ambiente_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        self.assertTrue(hasattr(AmbienteView.deletar_ambiente, '__wrapped__'))
    
    def test_deletar_ambiente_receives_ambiente_id(self):
        """Testa se recebe ambiente_id como parâmetro"""
        source = inspect.getsource(AmbienteView.deletar_ambiente)
        self.assertIn("ambiente_id", source)
    
    def test_deletar_ambiente_gets_by_id(self):
        """Testa se busca ambiente por id"""
        source = inspect.getsource(AmbienteView.deletar_ambiente)
        self.assertIn("Ambiente.objects.get", source)
    
    def test_deletar_ambiente_checks_post_method(self):
        """Testa se verifica método POST"""
        source = inspect.getsource(AmbienteView.deletar_ambiente)
        self.assertIn("request.method", source)
        self.assertIn("'POST'", source)
    
    def test_deletar_ambiente_deletes_on_post(self):
        """Testa se deleta o ambiente"""
        source = inspect.getsource(AmbienteView.deletar_ambiente)
        self.assertIn("delete", source)
    
    def test_deletar_ambiente_redirects(self):
        """Testa se redireciona após deletar"""
        source = inspect.getsource(AmbienteView.deletar_ambiente)
        self.assertIn("redirect", source)


class AmbienteFormUnitTest(SimpleTestCase):
    """Testes unitários do formulário Ambiente"""
    
    def test_ambiente_form_fields(self):
        """Testa se o formulário tem os campos corretos"""
        expected_fields = ['nome', 'tema']
        form = AmbienteForm()
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_ambiente_form_nome_required(self):
        """Testa se campo nome é obrigatório"""
        form = AmbienteForm()
        self.assertTrue(form.fields['nome'].required)
    
    def test_ambiente_form_tema_not_required(self):
        """Testa se campo tema não é obrigatório"""
        form = AmbienteForm()
        self.assertFalse(form.fields['tema'].required)
    
    def test_ambiente_form_uses_modelform(self):
        """Testa se o formulário herda de ModelForm"""
        from django.forms import ModelForm
        self.assertTrue(issubclass(AmbienteForm, ModelForm))
    
    def test_ambiente_form_meta_model(self):
        """Testa se o Meta.model é Ambiente"""
        self.assertEqual(AmbienteForm.Meta.model, Ambiente)
    
    def test_ambiente_form_meta_fields(self):
        """Testa se Meta.fields inclui nome e tema"""
        expected_fields = ['nome', 'tema']
        self.assertEqual(AmbienteForm.Meta.fields, expected_fields)
    
    def test_ambiente_form_nome_field_type(self):
        """Testa se campo nome é CharField"""
        from django import forms
        form = AmbienteForm()
        self.assertIsInstance(form.fields['nome'], forms.CharField)
    
    def test_ambiente_form_tema_field_type(self):
        """Testa se campo tema é CharField"""
        from django import forms
        form = AmbienteForm()
        self.assertIsInstance(form.fields['tema'], forms.CharField)
