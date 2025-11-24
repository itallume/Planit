from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Atividade, Cliente
from .forms import AtividadeForm, ClienteForm, EnderecoFormSet, ReferenciaFormSet


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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Renomear 'form' para 'atividade_form' para manter compatibilidade com o template
        if 'form' in context:
            context['atividade_form'] = context.pop('form')
        
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
        context = self.get_context_data()
        cliente_form = context['cliente_form']
        endereco_formset = context['endereco_formset']
        referencia_formset = context['referencia_formset']
        
        if cliente_form.is_valid() and endereco_formset.is_valid() and referencia_formset.is_valid():
            self.object = form.save()
            
            # Salvar cliente se foi preenchido
            if cliente_form.cleaned_data.get('nome'):
                cliente = cliente_form.save()
                endereco_formset.instance = cliente
                endereco_formset.save()
                self.object.cliente = cliente
                self.object.save()
            
            # Salvar referências
            referencia_formset.instance = self.object
            referencia_formset.save()
            
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


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
        
        if cliente_form.is_valid() and endereco_formset.is_valid() and referencia_formset.is_valid():
            self.object = form.save()
            
            # Salvar cliente
            if cliente_form.cleaned_data.get('nome'):
                cliente = cliente_form.save()
                endereco_formset.instance = cliente
                endereco_formset.save()
                self.object.cliente = cliente
                self.object.save()
            
            # Salvar referências
            referencia_formset.instance = self.object
            referencia_formset.save()
            
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class AtividadeDeleteView(DeleteView):
    model = Atividade
    template_name = 'atividade/deletar.html'
    context_object_name = 'atividade'
    pk_url_kwarg = 'atividade_id'
    success_url = reverse_lazy('lista_atividades')


