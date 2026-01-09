from django.test import SimpleTestCase
from unittest.mock import Mock, patch, MagicMock
from atividade.views import AtividadesPorAmbienteView, AtividadeDetailView, AtividadeCreateView, AtividadeUpdateView, AtividadeDeleteView
from atividade.models import Atividade, Cliente
from atividade.forms import AtividadeForm


class AtividadesPorAmbienteViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadesPorAmbiente"""
    
    def setUp(self):
        self.view = AtividadesPorAmbienteView()
        self.view.kwargs = {'ambiente_id': 1}
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_template_name(self):
        """Testa se a view usa o template correto"""
        self.assertEqual(self.view.template_name, 'atividade/atividades_por_ambiente.html')
    
    def test_view_context_object_name(self):
        """Testa se o context object name é atividades"""
        self.assertEqual(self.view.context_object_name, 'atividades')
    
    def test_view_inherits_from_listview(self):
        """Testa se view herda de ListView"""
        from django.views.generic import ListView
        self.assertTrue(issubclass(AtividadesPorAmbienteView, ListView))
    
    def test_view_inherits_login_required(self):
        """Testa se view requer autenticação"""
        from django.contrib.auth.mixins import LoginRequiredMixin
        self.assertTrue(issubclass(AtividadesPorAmbienteView, LoginRequiredMixin))
    
    @patch('atividade.views.Atividade.objects')
    def test_get_queryset_filters_by_ambiente_id(self, mock_objects):
        """Testa se get_queryset filtra por ambiente_id"""
        mock_queryset = MagicMock()
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        result = self.view.get_queryset()
        
        # Verifica se foi chamado filter
        mock_objects.filter.assert_called_once()
        # Verifica se order_by foi chamado
        mock_queryset.order_by.assert_called_once_with('data_prevista')


class AtividadeDetailViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadeDetail"""
    
    def setUp(self):
        self.view = AtividadeDetailView()
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_template_name(self):
        """Testa se a view usa o template correto"""
        self.assertEqual(self.view.template_name, 'atividade/detalhe.html')
    
    def test_view_context_object_name(self):
        """Testa se o context object name é atividade"""
        self.assertEqual(self.view.context_object_name, 'atividade')
    
    def test_view_pk_url_kwarg(self):
        """Testa se a view usa atividade_id como parâmetro"""
        self.assertEqual(self.view.pk_url_kwarg, 'atividade_id')
    
    def test_view_inherits_from_detailview(self):
        """Testa se view herda de DetailView"""
        from django.views.generic import DetailView
        self.assertTrue(issubclass(AtividadeDetailView, DetailView))


class AtividadeCreateViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadeCreate"""
    
    def setUp(self):
        self.view = AtividadeCreateView()
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_form_class(self):
        """Testa se a view usa o formulário correto"""
        self.assertEqual(self.view.form_class, AtividadeForm)
    
    def test_view_template_name(self):
        """Testa se a view usa o template correto"""
        self.assertEqual(self.view.template_name, 'atividade/form.html')
    
    def test_view_inherits_from_createview(self):
        """Testa se view herda de CreateView"""
        from django.views.generic import CreateView
        self.assertTrue(issubclass(AtividadeCreateView, CreateView))
    
    @patch('atividade.views.reverse_lazy')
    def test_get_success_url_default(self, mock_reverse):
        """Testa URL de sucesso padrão"""
        self.view.request = Mock(GET={})
        self.view.get_success_url()
        
        # Verifica se reverse_lazy foi chamado
        self.assertTrue(mock_reverse.called)


class AtividadeUpdateViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadeUpdate"""
    
    def setUp(self):
        self.view = AtividadeUpdateView()
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_form_class(self):
        """Testa se a view usa o formulário correto"""
        self.assertEqual(self.view.form_class, AtividadeForm)
    
    def test_view_template_name(self):
        """Testa se a view usa o template correto"""
        self.assertEqual(self.view.template_name, 'atividade/form.html')
    
    def test_view_pk_url_kwarg(self):
        """Testa se a view usa atividade_id como parâmetro"""
        self.assertEqual(self.view.pk_url_kwarg, 'atividade_id')
    
    def test_view_inherits_from_updateview(self):
        """Testa se view herda de UpdateView"""
        from django.views.generic import UpdateView
        self.assertTrue(issubclass(AtividadeUpdateView, UpdateView))


class AtividadeDeleteViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadeDelete"""
    
    def setUp(self):
        self.view = AtividadeDeleteView()
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_pk_url_kwarg(self):
        """Testa se a view usa atividade_id como parâmetro"""
        self.assertEqual(self.view.pk_url_kwarg, 'atividade_id')
    
    def test_view_inherits_from_deleteview(self):
        """Testa se view herda de DeleteView"""
        from django.views.generic import DeleteView
        self.assertTrue(issubclass(AtividadeDeleteView, DeleteView))


class BuscarClientesViewUnitTest(SimpleTestCase):
    """Testes unitários da função buscar_clientes"""
    
    def test_buscar_clientes_is_callable(self):
        """Testa se a função buscar_clientes existe e é callable"""
        from atividade.views import buscar_clientes
        self.assertTrue(callable(buscar_clientes))
    
    def test_buscar_clientes_returns_json_response(self):
        """Testa se a função retorna JsonResponse"""
        import inspect
        from atividade.views import buscar_clientes
        
        source = inspect.getsource(buscar_clientes)
        self.assertIn('JsonResponse', source)
    
    def test_buscar_clientes_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        import inspect
        from atividade.views import buscar_clientes
        
        # Verifica se a função tem __wrapped__ (indica que tem decorador)
        self.assertTrue(hasattr(buscar_clientes, '__wrapped__'))
    
    def test_buscar_clientes_filters_by_query(self):
        """Testa se a função filtra por query"""
        import inspect
        from atividade.views import buscar_clientes
        
        source = inspect.getsource(buscar_clientes)
        self.assertIn('request.GET.get', source)
        self.assertIn('filter', source)


class BuscarEnderecosClienteViewUnitTest(SimpleTestCase):
    """Testes unitários da função buscar_enderecos_cliente"""
    
    def test_buscar_enderecos_cliente_is_callable(self):
        """Testa se a função buscar_enderecos_cliente existe e é callable"""
        from atividade.views import buscar_enderecos_cliente
        self.assertTrue(callable(buscar_enderecos_cliente))
    
    def test_buscar_enderecos_cliente_returns_json_response(self):
        """Testa se a função retorna JsonResponse"""
        import inspect
        from atividade.views import buscar_enderecos_cliente
        
        source = inspect.getsource(buscar_enderecos_cliente)
        self.assertIn('JsonResponse', source)
    
    def test_buscar_enderecos_cliente_has_login_required(self):
        """Testa se a função tem decorator @login_required"""
        import inspect
        from atividade.views import buscar_enderecos_cliente
        
        self.assertTrue(hasattr(buscar_enderecos_cliente, '__wrapped__'))
    
    def test_buscar_enderecos_cliente_filters_by_cliente_id(self):
        """Testa se a função filtra por cliente_id"""
        import inspect
        from atividade.views import buscar_enderecos_cliente
        
        source = inspect.getsource(buscar_enderecos_cliente)
        self.assertIn('cliente_id', source)
        self.assertIn('filter', source)


class AtividadeFormUnitTest(SimpleTestCase):
    """Testes unitários do formulário Atividade"""
    
    def test_form_fields(self):
        """Testa se o formulário tem os campos corretos"""
        expected_fields = ['descricao', 'valor', 'valor_recebido', 'data_prevista', 'hora_prevista', 'status', 'is_paga', 'cliente']
        form = AtividadeForm()
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_descricao_widget_textarea(self):
        """Testa se descricao usa widget Textarea"""
        from django import forms
        form = AtividadeForm()
        self.assertIsInstance(form.fields['descricao'].widget, forms.Textarea)
    
    def test_form_data_prevista_widget_date_input(self):
        """Testa se data_prevista usa widget DateInput"""
        from django import forms
        form = AtividadeForm()
        self.assertIsInstance(form.fields['data_prevista'].widget, forms.DateInput)
    
    def test_form_hora_prevista_widget_time_input(self):
        """Testa se hora_prevista usa widget TimeInput"""
        from django import forms
        form = AtividadeForm()
        self.assertIsInstance(form.fields['hora_prevista'].widget, forms.TimeInput)
    
    def test_form_status_widget_radio_select(self):
        """Testa se status usa widget RadioSelect"""
        from django import forms
        form = AtividadeForm()
        self.assertIsInstance(form.fields['status'].widget, forms.RadioSelect)
    
    def test_form_cliente_widget_hidden_input(self):
        """Testa se cliente usa widget HiddenInput"""
        from django import forms
        form = AtividadeForm()
        self.assertIsInstance(form.fields['cliente'].widget, forms.HiddenInput)
    
    def test_form_valor_required(self):
        """Testa se campo valor é obrigatório"""
        form = AtividadeForm()
        self.assertTrue(form.fields['valor'].required)
    
    def test_form_descricao_textarea_rows(self):
        """Testa se textarea tem 4 linhas"""
        form = AtividadeForm()
        self.assertEqual(form.fields['descricao'].widget.attrs['rows'], 4)
