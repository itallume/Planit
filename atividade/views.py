from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from datetime import timedelta
from .models import Atividade, Cliente
from .forms import AtividadeForm, ClienteForm, EnderecoFormSet, ReferenciaFormSet
from ambiente.models import Ambiente
import json


def buscar_clientes(request):
    """API para buscar clientes por nome ou email"""
    query = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all().order_by('nome')
    
    if query:
        clientes = clientes.filter(Q(nome__icontains=query) | Q(email__icontains=query))
    limit = 10 if query else 20
    clientes = clientes.values('id', 'nome', 'email')[:limit]
    return JsonResponse(list(clientes), safe=False)

class AtividadesPorAmbienteView(ListView):
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

class AtividadeListView(ListView):
    model = Atividade
    template_name = 'atividade/lista.html'
    context_object_name = 'atividades'
    paginate_by = 10


class AtividadeDetailView(DetailView):
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
        return context


class AtividadeCreateView(CreateView):
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
        # Renomear 'form' para 'atividade_form' para manter compatibilidade com o template
        if 'form' in context:
            context['atividade_form'] = context.pop('form')
        
        ambiente_id = self.request.GET.get('ambiente_id')
        if ambiente_id:
            try:
                ambiente = Ambiente.objects.get(id=ambiente_id)
                context['ambiente'] = ambiente
            except Ambiente.DoesNotExist:
                pass
        
        if self.request.POST:
            context['cliente_form'] = ClienteForm(self.request.POST, prefix='cliente')
            context['endereco_formset'] = EnderecoFormSet(self.request.POST, prefix='endereco')
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
        
        # Validar que o ambiente foi definido
        if not ambiente_id:
            form.add_error(None, 'É necessário selecionar um ambiente')
            return self.form_invalid(form)
        
        try:
            ambiente = Ambiente.objects.get(id=ambiente_id)
        except Ambiente.DoesNotExist:
            form.add_error(None, 'Ambiente inválido')
            return self.form_invalid(form)
        
        # Validar referências formset primeiro (sempre necessário)
        if not referencia_formset.is_valid():
            return self.form_invalid(form)
        
        # Processar cliente - pode vir do campo cliente (já preenchido via JS) ou do formulário novo
        cliente_id = self.request.POST.get('atividade_form-cliente')
        criar_novo = self.request.POST.get('criar-novo-cliente')
        cliente = None
        
        if cliente_id:
            # Cliente existente foi selecionado
            try:
                cliente = Cliente.objects.get(id=cliente_id)
            except Cliente.DoesNotExist:
                form.add_error(None, 'Cliente selecionado não existe')
                return self.form_invalid(form)
        elif criar_novo:
            # Novo cliente será criado
            if not cliente_form.is_valid() or not endereco_formset.is_valid():
                return self.form_invalid(form)
            
            if cliente_form.cleaned_data.get('nome'):
                cliente = cliente_form.save()
                endereco_formset.instance = cliente
                endereco_formset.save()
        
        # Salvar atividade
        self.object = form.save(commit=False)
        self.object.ambiente = ambiente
        if cliente:
            self.object.cliente = cliente
        self.object.save()
        
        # Salvar referências
        referencia_formset.instance = self.object
        referencia_formset.save()
        
        return redirect(self.get_success_url())


class AtividadeUpdateView(UpdateView):
    model = Atividade
    form_class = AtividadeForm
    template_name = 'atividade/form.html'
    pk_url_kwarg = 'atividade_id'
    success_url = reverse_lazy('lista_atividades')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Renomear 'form' para 'atividade_form' para manter compatibilidade com o template
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
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        cliente_form = context['cliente_form']
        endereco_formset = context['endereco_formset']
        referencia_formset = context['referencia_formset']
        
        # Validar referências formset primeiro (sempre necessário)
        if not referencia_formset.is_valid():
            return self.form_invalid(form)
        
        # Processar cliente
        cliente_id = self.request.POST.get('atividade_form-cliente')
        criar_novo = self.request.POST.get('criar-novo-cliente')
        cliente = None
        
        if cliente_id:
            # Cliente existente foi selecionado
            try:
                cliente = Cliente.objects.get(id=cliente_id)
            except Cliente.DoesNotExist:
                form.add_error(None, 'Cliente selecionado não existe')
                return self.form_invalid(form)
        elif criar_novo:
            # Novo cliente ou atualizar cliente existente
            if not cliente_form.is_valid() or not endereco_formset.is_valid():
                return self.form_invalid(form)
            
            if cliente_form.cleaned_data.get('nome'):
                cliente = cliente_form.save()
                endereco_formset.instance = cliente
                endereco_formset.save()
        
        # Salvar atividade
        self.object = form.save()
        
        # Atualizar cliente
        if cliente:
            self.object.cliente = cliente
            self.object.save()
        
        # Salvar referências
        referencia_formset.instance = self.object
        referencia_formset.save()
        
        return redirect(self.success_url)


class AtividadeDeleteView(DeleteView):
    model = Atividade
    template_name = 'atividade/deletar.html'
    context_object_name = 'atividade'
    pk_url_kwarg = 'atividade_id'
    success_url = reverse_lazy('lista_atividades')


