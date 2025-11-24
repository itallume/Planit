from django.shortcuts import render, redirect

from ambiente.forms import AmbienteForm
from ambiente.models import Ambiente
from django.db.models import Count, Q

# Create your views here.

class AmbienteView:
    def lista_ambientes(request):
        ambientes = Ambiente.objects.annotate(
            num_atividades=Count('atividade'),
            num_pendentes=Count('atividade', filter=Q(atividade__status='Pendente')),
            num_concluidas=Count('atividade', filter=Q(atividade__status='Concluído')),
            num_atrasadas=Count('atividade', filter=Q(atividade__status='Atrasado'))
        )
        form = AmbienteForm()
        return render(request, 'ambiente/home.html', {'ambientes': ambientes, 'form': form})
    
    def detalhe_ambiente(request, ambiente_id):
        ambiente = Ambiente.objects.get(id=ambiente_id)
        atividades = ambiente.atividade_set.all()
        return render(request, 'ambiente/detalhe.html', {
            'ambiente': ambiente,
            'atividades': atividades
        })
    
    def criar_ambiente(request):
        if request.method == 'POST':
            form = AmbienteForm(request.POST)
            ambientes = Ambiente.objects.annotate(
                num_atividades=Count('atividade'),
                num_pendentes=Count('atividade', filter=Q(atividade__status='Pendente')),
                num_concluidas=Count('atividade', filter=Q(atividade__status='Concluído')),
                num_atrasadas=Count('atividade', filter=Q(atividade__status='Atrasado'))
            )
            if form.is_valid():
                form.save()
                return redirect('lista_ambientes')
            else:
                # Renderiza home.html com o form preenchido e erros
                return render(request, 'ambiente/home.html', {'ambientes': ambientes, 'form': form})
        # Se acessar diretamente, redireciona para lista
        return redirect('lista_ambientes')
    
    def editar_ambiente(request, ambiente_id):
        ambiente = Ambiente.objects.get(id=ambiente_id)
        if request.method == 'POST':
            form = AmbienteForm(request.POST, instance=ambiente)
            ambientes = Ambiente.objects.annotate(
                num_atividades=Count('atividade'),
                num_pendentes=Count('atividade', filter=Q(atividade__status='Pendente')),
                num_concluidas=Count('atividade', filter=Q(atividade__status='Concluído')),
                num_atrasadas=Count('atividade', filter=Q(atividade__status='Atrasado'))
            )
            if form.is_valid():
                form.save()
                return redirect('lista_ambientes')
            else:
                # Renderiza home.html com o form preenchido e erros, e id do ambiente para abrir modal de editar
                return render(request, 'ambiente/home.html', {
                    'ambientes': ambientes,
                    'form_editar': form,
                    'ambiente_editar_id': ambiente.id
                })
        # GET: renderiza home.html com dados do ambiente para edição
        form = AmbienteForm(instance=ambiente)
        ambientes = Ambiente.objects.annotate(
            num_atividades=Count('atividade'),
            num_pendentes=Count('atividade', filter=Q(atividade__status='Pendente')),
            num_concluidas=Count('atividade', filter=Q(atividade__status='Concluído')),
            num_atrasadas=Count('atividade', filter=Q(atividade__status='Atrasado'))
        )
        return render(request, 'ambiente/home.html', {
            'ambientes': ambientes,
            'form_editar': form,
            'ambiente_editar_id': ambiente.id
        })
    
    def deletar_ambiente(request, ambiente_id):
        return render(request, 'ambiente/deletar.html', {'ambiente_id': ambiente_id})
    
    