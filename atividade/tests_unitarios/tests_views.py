from django.test import SimpleTestCase
from unittest.mock import Mock, patch, MagicMock
from atividade.views import (
    AtividadesPorAmbienteView, 
    AtividadeDetailView, 
    AtividadeCreateView, 
    AtividadeUpdateView, 
    AtividadeDeleteView,
    ClienteViewSet,
    EnderecoViewSet
)
from atividade.models import Atividade
from atividade.forms import AtividadeForm


class AtividadesPorAmbienteViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadesPorAmbiente"""
    
    def setUp(self):
        self.view = AtividadesPorAmbienteView()
        self.view.kwargs = {'ambiente_id': 1}
        self.view.request = Mock()
        self.view.request.GET = {}
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_template_name(self):
        """Testa se a view usa o template correto"""
        self.assertEqual(self.view.template_name, 'atividade/atividades_por_ambiente.html')
    
    def test_view_context_object_name(self):
        """Testa se o context object name é atividades"""
        self.assertEqual(self.view.context_object_name, 'atividades')
    
    def test_view_paginate_by(self):
        """Testa se a view tem paginação configurada para 2 itens"""
        self.assertEqual(self.view.paginate_by, 2)
    
    def test_view_inherits_from_listview(self):
        """Testa se view herda de ListView"""
        from django.views.generic import ListView
        self.assertTrue(issubclass(AtividadesPorAmbienteView, ListView))
    
    def test_view_inherits_login_required(self):
        """Testa se view requer autenticação"""
        from django.contrib.auth.mixins import LoginRequiredMixin
        self.assertTrue(issubclass(AtividadesPorAmbienteView, LoginRequiredMixin))
    
    def test_view_has_ambiente_permission_mixin(self):
        """Testa se view tem AmbientePermissionMixin"""
        from atividade.mixins import AmbientePermissionMixin
        self.assertTrue(issubclass(AtividadesPorAmbienteView, AmbientePermissionMixin))
    
    def test_view_has_atividade_permission_mixin(self):
        """Testa se view tem AtividadePermissionMixin"""
        from atividade.mixins import AtividadePermissionMixin
        self.assertTrue(issubclass(AtividadesPorAmbienteView, AtividadePermissionMixin))


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
    
    def test_view_inherits_login_required(self):
        """Testa se view requer autenticação"""
        from django.contrib.auth.mixins import LoginRequiredMixin
        self.assertTrue(issubclass(AtividadeDetailView, LoginRequiredMixin))
    
    def test_view_has_ambiente_permission_mixin(self):
        """Testa se view tem AmbientePermissionMixin"""
        from atividade.mixins import AmbientePermissionMixin
        self.assertTrue(issubclass(AtividadeDetailView, AmbientePermissionMixin))


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
    
    def test_view_inherits_login_required(self):
        """Testa se view requer autenticação"""
        from django.contrib.auth.mixins import LoginRequiredMixin
        self.assertTrue(issubclass(AtividadeCreateView, LoginRequiredMixin))


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
    
    def test_view_inherits_login_required(self):
        """Testa se view requer autenticação"""
        from django.contrib.auth.mixins import LoginRequiredMixin
        self.assertTrue(issubclass(AtividadeUpdateView, LoginRequiredMixin))


class AtividadeDeleteViewUnitTest(SimpleTestCase):
    """Testes unitários da view AtividadeDelete"""
    
    def setUp(self):
        self.view = AtividadeDeleteView()
    
    def test_view_model(self):
        """Testa se a view usa o modelo Atividade"""
        self.assertEqual(self.view.model, Atividade)
    
    def test_view_template_name(self):
        """Testa se a view usa o template correto"""
        self.assertEqual(self.view.template_name, 'atividade/deletar.html')
    
    def test_view_pk_url_kwarg(self):
        """Testa se a view usa atividade_id como parâmetro"""
        self.assertEqual(self.view.pk_url_kwarg, 'atividade_id')
    
    def test_view_inherits_from_deleteview(self):
        """Testa se view herda de DeleteView"""
        from django.views.generic import DeleteView
        self.assertTrue(issubclass(AtividadeDeleteView, DeleteView))
    
    def test_view_inherits_login_required(self):
        """Testa se view requer autenticação"""
        from django.contrib.auth.mixins import LoginRequiredMixin
        self.assertTrue(issubclass(AtividadeDeleteView, LoginRequiredMixin))


class ClienteViewSetUnitTest(SimpleTestCase):
    """Testes unitários do ViewSet Cliente"""
    
    def setUp(self):
        self.viewset = ClienteViewSet()
    
    def test_viewset_inherits_from_readonly_model_viewset(self):
        """Testa se viewset herda de ReadOnlyModelViewSet"""
        from rest_framework import viewsets
        self.assertTrue(issubclass(ClienteViewSet, viewsets.ReadOnlyModelViewSet))
    
    def test_viewset_has_permission_classes(self):
        """Testa se viewset tem permission_classes configurado"""
        from rest_framework import permissions
        self.assertIn(permissions.IsAuthenticated, ClienteViewSet.permission_classes)
    
    def test_viewset_has_serializer_class(self):
        """Testa se viewset tem serializer_class configurado"""
        from atividade.serializers import ClienteSerializer
        self.assertEqual(ClienteViewSet.serializer_class, ClienteSerializer)


class EnderecoViewSetUnitTest(SimpleTestCase):
    """Testes unitários do ViewSet Endereco"""
    
    def setUp(self):
        self.viewset = EnderecoViewSet()
    
    def test_viewset_inherits_from_readonly_model_viewset(self):
        """Testa se viewset herda de ReadOnlyModelViewSet"""
        from rest_framework import viewsets
        self.assertTrue(issubclass(EnderecoViewSet, viewsets.ReadOnlyModelViewSet))
    
    def test_viewset_has_permission_classes(self):
        """Testa se viewset tem permission_classes configurado"""
        from rest_framework import permissions
        self.assertIn(permissions.IsAuthenticated, EnderecoViewSet.permission_classes)
    
    def test_viewset_has_serializer_class(self):
        """Testa se viewset tem serializer_class configurado"""
        from atividade.serializers import EnderecoSerializer
        self.assertEqual(EnderecoViewSet.serializer_class, EnderecoSerializer)


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
    
    def test_form_descricao_required(self):
        """Testa se campo descricao é obrigatório"""
        form = AtividadeForm()
        self.assertTrue(form.fields['descricao'].required)
    
    def test_form_descricao_textarea_rows(self):
        """Testa se textarea tem 4 linhas"""
        form = AtividadeForm()
        self.assertEqual(form.fields['descricao'].widget.attrs['rows'], 4)
    
    def test_form_use_required_attribute_disabled(self):
        """Testa se o form desabilita HTML5 required attribute"""
        form = AtividadeForm()
        # Verifica se todos os campos não usam required attribute
        for field_name, field in form.fields.items():
            self.assertFalse(field.widget.use_required_attribute(field))
