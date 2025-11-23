from django.shortcuts import render, redirect, get_object_or_404
from .models import Atividade, Cliente
from .forms import AtividadeForm, ClienteForm, EnderecoFormSet, ReferenciaFormSet

# Create your views here.

class AtividadeView:
    def lista_atividades(request):
        atividades = Atividade.objects.all()
        return render(request, 'atividade/lista.html', {'atividades': atividades})
    
    def detalhe_atividade(request, atividade_id):
        atividade = get_object_or_404(Atividade, id=atividade_id)
        referencias = atividade.referencia_set.all()
        cliente = atividade.cliente
        enderecos = cliente.endereco_set.all() if cliente else []
        return render(request, 'atividade/detalhe.html', {
            'atividade': atividade,
            'referencias': referencias,
            'cliente': cliente,
            'enderecos': enderecos
        })
    
    def criar_atividade(request):
        if request.method == 'POST':
            atividade_form = AtividadeForm(request.POST)
            cliente_form = ClienteForm(request.POST, prefix='cliente')
            
            if atividade_form.is_valid() and cliente_form.is_valid():
                atividade = atividade_form.save()
                
                # Salvar cliente se foi preenchido
                if cliente_form.cleaned_data.get('nome'):
                    cliente = cliente_form.save()
                    endereco_formset = EnderecoFormSet(request.POST, instance=cliente, prefix='endereco')
                    if endereco_formset.is_valid():
                        endereco_formset.save()
                    atividade.cliente = cliente
                    atividade.save()
                
                # Salvar referências
                referencia_formset = ReferenciaFormSet(request.POST, request.FILES, instance=atividade, prefix='referencia')
                if referencia_formset.is_valid():
                    referencia_formset.save()
                
                return redirect('lista_atividades')
            else:
                endereco_formset = EnderecoFormSet(request.POST, prefix='endereco')
                referencia_formset = ReferenciaFormSet(request.POST, request.FILES, prefix='referencia')
        else:
            atividade_form = AtividadeForm()
            cliente_form = ClienteForm(prefix='cliente')
            endereco_formset = EnderecoFormSet(prefix='endereco')
            referencia_formset = ReferenciaFormSet(prefix='referencia')
        
        return render(request, 'atividade/form.html', {
            'atividade_form': atividade_form,
            'cliente_form': cliente_form,
            'endereco_formset': endereco_formset,
            'referencia_formset': referencia_formset
        })
    
    def editar_atividade(request, atividade_id):
        atividade = get_object_or_404(Atividade, id=atividade_id)
        cliente = atividade.cliente
        
        if request.method == 'POST':
            atividade_form = AtividadeForm(request.POST, instance=atividade)
            
            if cliente:
                cliente_form = ClienteForm(request.POST, instance=cliente, prefix='cliente')
                endereco_formset = EnderecoFormSet(request.POST, instance=cliente, prefix='endereco')
            else:
                cliente_form = ClienteForm(request.POST, prefix='cliente')
                endereco_formset = EnderecoFormSet(request.POST, prefix='endereco')
            
            referencia_formset = ReferenciaFormSet(request.POST, request.FILES, instance=atividade, prefix='referencia')
            
            if atividade_form.is_valid() and cliente_form.is_valid() and referencia_formset.is_valid():
                atividade = atividade_form.save()
                
                # Salvar cliente
                if cliente_form.cleaned_data.get('nome'):
                    cliente = cliente_form.save()
                    if endereco_formset.is_valid():
                        endereco_formset.save()
                    atividade.cliente = cliente
                    atividade.save()
                
                # Salvar referências
                referencia_formset.save()
                
                return redirect('lista_atividades')
        else:
            atividade_form = AtividadeForm(instance=atividade)
            
            if cliente:
                cliente_form = ClienteForm(instance=cliente, prefix='cliente')
                endereco_formset = EnderecoFormSet(instance=cliente, prefix='endereco')
            else:
                cliente_form = ClienteForm(prefix='cliente')
                endereco_formset = EnderecoFormSet(prefix='endereco')
            
            referencia_formset = ReferenciaFormSet(instance=atividade, prefix='referencia')
        
        return render(request, 'atividade/form.html', {
            'atividade_form': atividade_form,
            'cliente_form': cliente_form,
            'endereco_formset': endereco_formset,
            'referencia_formset': referencia_formset,
            'atividade': atividade
        })
    
    def deletar_atividade(request, atividade_id):
        atividade = get_object_or_404(Atividade, id=atividade_id)
        if request.method == 'POST':
            atividade.delete()
            return redirect('lista_atividades')
        return render(request, 'atividade/deletar.html', {'atividade': atividade})


