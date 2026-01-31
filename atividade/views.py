from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q
from datetime import timedelta
import os
import mimetypes
from .models import Atividade, Cliente, Referencia, Endereco
from .forms import AtividadeForm, ClienteForm, EnderecoFormSet, ReferenciaFormSet
from ambiente.models import Ambiente
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import AmbientePermissionMixin
from rest_framework import viewsets, permissions
from .serializers import ClienteSerializer, EnderecoSerializer

class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Permitir busca por nome ou email via parâmetro 'search'"""
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(nome__icontains=search) | Q(email__icontains=search))
        limit = 10 if search else 20
        queryset = queryset.values('id', 'nome', 'email', 'telefone', 'sobre').order_by('nome')[:limit]
        return queryset

class EnderecoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cliente_id = self.kwargs.get('cliente_id')
        return Endereco.objects.filter(cliente_id=cliente_id).values(
            'id', 'rua', 'cidade', 'estado', 'cep', 'complemento'
        )

# @login_required
# def buscar_clientes(request):
#     """API para buscar clientes por nome ou email"""
#     query = request.GET.get('q', '').strip()
#     clientes = Cliente.objects.all().order_by('nome')
    
#     if query:
#         clientes = clientes.filter(Q(nome__icontains=query) | Q(email__icontains=query))
#     limit = 10 if query else 20
#     clientes = clientes.values('id', 'nome', 'email', 'telefone', 'sobre')[:limit]
#     return JsonResponse(list(clientes), safe=False)



# @login_required
# def buscar_enderecos_cliente(request, cliente_id):
#     """API para buscar endereços de um cliente específico"""
#     enderecos = Endereco.objects.filter(cliente_id=cliente_id).values(
#         'id', 'rua', 'cidade', 'estado', 'cep', 'complemento'
#     )
#     return JsonResponse(list(enderecos), safe=False)

class AtividadesPorAmbienteView(LoginRequiredMixin, AmbientePermissionMixin, ListView):
    model = Atividade
    template_name = 'atividade/atividades_por_ambiente.html'
    context_object_name = 'atividades'

    def get_queryset(self):
        ambiente_id = self.kwargs.get('ambiente_id')
        hoje = timezone.now().date()
        trinta_dias_atras = hoje - timedelta(days=30)
        trinta_dias_frente = hoje + timedelta(days=30)
        
        return Atividade.objects.filter(
            ambiente__id=ambiente_id,
            data_prevista__gte=trinta_dias_atras,
            data_prevista__lte=trinta_dias_frente
        ).order_by('data_prevista')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ambiente_id = self.kwargs.get('ambiente_id')
        ambiente = get_object_or_404(Ambiente, id=ambiente_id)
        context['ambiente'] = ambiente
        
        # Gerar dados para agenda
        hoje = timezone.now().date()
        atividades_por_dia = {}
        for i in range(-30, 31):
            data = hoje + timedelta(days=i)
            count = Atividade.objects.filter(
                ambiente__id=ambiente_id,
                data_prevista=data
            ).count()
            atividades_por_dia[data.isoformat()] = count
        
        context['atividades_por_dia'] = json.dumps(atividades_por_dia)
        return context

class AtividadeDetailView(LoginRequiredMixin, AmbientePermissionMixin, DetailView):
    model = Atividade
    template_name = 'atividade/detalhe.html'
    context_object_name = 'atividade'
    pk_url_kwarg = 'atividade_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atividade = self.get_object()
        context['referencias'] = atividade.referencia_set.all()
        context['cliente'] = atividade.cliente
        if atividade.cliente:
            context['enderecos'] = atividade.cliente.endereco_set.all()
        else:
            context['enderecos'] = []
        # Passar o ambiente_id para o template poder voltar para a página correta
        if atividade.ambiente:
            context['ambiente_id'] = atividade.ambiente.id
        else:
            context['ambiente_id'] = None
        return context

class AtividadeCreateView(LoginRequiredMixin, AmbientePermissionMixin, CreateView):
    model = Atividade
    form_class = AtividadeForm
    template_name = 'atividade/form.html'
    success_url = reverse_lazy('lista_atividades')
    
    def get_success_url(self):
        ambiente_id = self.request.GET.get('ambiente_id')
        if ambiente_id:
            return reverse_lazy('atividades_por_ambiente', kwargs={'ambiente_id': ambiente_id})
        return reverse_lazy('lista_atividades')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' in context:
            context['atividade_form'] = context.pop('form')
        
        ambiente_id = self.request.GET.get('ambiente_id')
        if ambiente_id:
            try:
                ambiente = Ambiente.objects.get(id=ambiente_id)
                context['ambiente'] = ambiente
            except Ambiente.DoesNotExist:
                return reverse_lazy('lista_atividades')
        else:
            return reverse_lazy('lista_atividades')
        
        data_prevista = self.request.GET.get('data_prevista')
        if data_prevista and 'atividade_form' in context:
            context['atividade_form'].fields['data_prevista'].initial = data_prevista
        
        if self.request.POST:
            cliente_id = self.request.POST.get('cliente')
            cliente_instance = None
            if cliente_id:
                try:
                    cliente_instance = Cliente.objects.get(id=cliente_id)
                except Cliente.DoesNotExist:
                    cliente_instance = None

            context['cliente_form'] = ClienteForm(self.request.POST, instance=cliente_instance, prefix='cliente')
            context['endereco_formset'] = EnderecoFormSet(self.request.POST, instance=cliente_instance, prefix='endereco')
            context['referencia_formset'] = ReferenciaFormSet(self.request.POST, self.request.FILES, prefix='referencia')
        else:
            context['cliente_form'] = ClienteForm(prefix='cliente')
            context['endereco_formset'] = EnderecoFormSet(prefix='endereco')
            context['referencia_formset'] = ReferenciaFormSet(prefix='referencia')
        return context
    
    def form_valid(self, form):
        ambiente_id = self.request.GET.get('ambiente_id')
        
        context = self.get_context_data()
        cliente_form = context['cliente_form']
        endereco_formset = context['endereco_formset']
        referencia_formset = context['referencia_formset']
        
        if not ambiente_id:
            form.add_error(None, 'É necessário selecionar um ambiente')
            return self.form_invalid(form)
        
        try:
            ambiente = Ambiente.objects.get(id=ambiente_id)
        except Ambiente.DoesNotExist:
            form.add_error(None, 'Ambiente inválido')
            return self.form_invalid(form)
        
        if not referencia_formset.is_valid():
            return self.form_invalid(form)
        
        # Processar cliente - verificar se há dados de cliente no formulário
        cliente_id = self.request.POST.get('cliente')
        cliente_nome = cliente_form.cleaned_data.get('nome') if cliente_form.is_valid() else None
        cliente = None
        
        if cliente_id and cliente_nome:
            # Cliente existente sendo editado
            try:
                cliente = Cliente.objects.get(id=cliente_id)
                if cliente_form.is_valid():
                    cliente = cliente_form.save()
                    
                    endereco_formset.instance = cliente
                    if endereco_formset.is_valid():
                        endereco_formset.save()
                    elif endereco_formset.is_bound and endereco_formset.errors:
                        return self.form_invalid(form)
                else:
                    return self.form_invalid(form)
            except Cliente.DoesNotExist:
                form.add_error(None, 'Cliente selecionado não existe')
                return self.form_invalid(form)
        elif cliente_nome:
            if cliente_form.is_valid():
                cliente = cliente_form.save()
                
                endereco_formset.instance = cliente
                if endereco_formset.is_bound and not endereco_formset.is_valid():
                    cliente.delete()
                    return self.form_invalid(form)
                
                if endereco_formset.is_bound:
                    endereco_formset.save()
            else:
                return self.form_invalid(form)
        
        self.object = form.save(commit=False)
        self.object.ambiente = ambiente
        if cliente:
            self.object.cliente = cliente
        self.object.save()
        
        referencia_formset.instance = self.object
        referencia_formset.save()
        
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class AtividadeUpdateView(LoginRequiredMixin, AmbientePermissionMixin, UpdateView):
    model = Atividade
    form_class = AtividadeForm
    template_name = 'atividade/form.html'
    pk_url_kwarg = 'atividade_id'
    
    def get_success_url(self):
        atividade = self.get_object()
        return reverse_lazy('atividades_por_ambiente', kwargs={'ambiente_id': atividade.ambiente.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' in context:
            context['atividade_form'] = context.pop('form')
        
        atividade = self.get_object()
        cliente = atividade.cliente
        
        if self.request.POST:
            context['cliente_form'] = ClienteForm(self.request.POST, instance=cliente, prefix='cliente')
            if cliente:
                context['endereco_formset'] = EnderecoFormSet(self.request.POST, instance=cliente, prefix='endereco')
            else:
                context['endereco_formset'] = EnderecoFormSet(self.request.POST, prefix='endereco')
            context['referencia_formset'] = ReferenciaFormSet(self.request.POST, self.request.FILES, instance=atividade, prefix='referencia')
        else:
            context['cliente_form'] = ClienteForm(instance=cliente, prefix='cliente')
            if cliente:
                context['endereco_formset'] = EnderecoFormSet(instance=cliente, prefix='endereco')
            else:
                context['endereco_formset'] = EnderecoFormSet(prefix='endereco')
            context['referencia_formset'] = ReferenciaFormSet(instance=atividade, prefix='referencia')
        
        context['atividade'] = atividade
        context['ambiente'] = atividade.ambiente
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        cliente_form = context['cliente_form']
        endereco_formset = context['endereco_formset']
        referencia_formset = context['referencia_formset']
        
        if not referencia_formset.is_valid():
            return self.form_invalid(form)
        
        cliente_id = self.request.POST.get('cliente')
        cliente_nome = cliente_form.cleaned_data.get('nome') if cliente_form.is_valid() else None
        cliente = None
        
        if cliente_id and cliente_nome:
            try:
                cliente = Cliente.objects.get(id=cliente_id)
                if cliente_form.is_valid():
                    cliente = cliente_form.save()
                    
                    endereco_formset.instance = cliente
                    if endereco_formset.is_valid():
                        endereco_formset.save()
                    elif endereco_formset.is_bound and endereco_formset.errors:
                        return self.form_invalid(form)
                else:
                    return self.form_invalid(form)
            except Cliente.DoesNotExist:
                form.add_error(None, 'Cliente selecionado não existe')
                return self.form_invalid(form)
        elif cliente_nome:
            if cliente_form.is_valid():
                cliente = cliente_form.save()
                
                endereco_formset.instance = cliente
                if endereco_formset.is_bound and not endereco_formset.is_valid():
                    cliente.delete()
                    return self.form_invalid(form)
                
                if endereco_formset.is_bound:
                    endereco_formset.save()
            else:
                return self.form_invalid(form)
        
        self.object = form.save()
        
        if cliente:
            self.object.cliente = cliente
            self.object.save()
        
        referencia_formset.instance = self.object
        referencia_formset.save()
        
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        """Sobrescrever para adicionar contexto de erro"""
        print("=== FORM INVALID ===")
        print(f"Atividade form errors: {form.errors}")
        context = self.get_context_data(form=form)
        print(f"Cliente form errors: {context['cliente_form'].errors}")
        print(f"Endereco formset errors: {context['endereco_formset'].errors}")
        print(f"Referencia formset errors: {context['referencia_formset'].errors}")
        return self.render_to_response(context)

class AtividadeDeleteView(LoginRequiredMixin, AmbientePermissionMixin, DeleteView):
    model = Atividade
    template_name = 'atividade/deletar.html'
    context_object_name = 'atividade'
    pk_url_kwarg = 'atividade_id'
    success_url = reverse_lazy('lista_atividades')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atividade = self.get_object()
        # Passar o ambiente_id para o template poder voltar para a página correta
        context['ambiente_id'] = atividade.ambiente.id
        return context
    
    def get_success_url(self):
        # Redirecionar para a página de atividades do ambiente após exclusão
        atividade = self.get_object()
        return reverse_lazy('atividades_por_ambiente', kwargs={'ambiente_id': atividade.ambiente.id})

@login_required
def download_referencia(request, referencia_id: int):
    referencia = get_object_or_404(Referencia, id=referencia_id)
    if not referencia.arquivo:
        raise Http404("Arquivo não encontrado")

    original_name = os.path.basename(referencia.arquivo.name)
    base, ext = os.path.splitext(original_name)
    desired_name = (referencia.nome_arquivo or '').strip()

    if desired_name:
        # If a custom name is provided, ensure it has the original extension
        if not os.path.splitext(desired_name)[1] and ext:
            filename = desired_name + ext
        else:
            filename = desired_name
    else:
        # Fallback to stored filename with extension
        filename = original_name

    content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    return FileResponse(
        referencia.arquivo.open('rb'),
        as_attachment=True,
        filename=filename,
        content_type=content_type,
    )


