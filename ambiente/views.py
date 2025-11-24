from django.shortcuts import render, redirect

from ambiente.forms import AmbienteForm
from ambiente.models import Ambiente
from django.db.models import Count

# Create your views here.

class AmbienteView:
    def lista_ambientes(request):
        ambientes = Ambiente.objects.annotate(num_atividades=Count('atividade'))
        return render(request, 'ambiente/home.html', {'ambientes': ambientes})
    
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
            if form.is_valid():
                form.save()
                return redirect('lista_ambientes')
            else:
                return render(request, 'ambiente/form.html', {'form': form})
        form = AmbienteForm()
        return render(request, 'ambiente/form.html', {'form': form})
    
    def editar_ambiente(request, ambiente_id):
        return render(request, 'ambiente/editar.html', {'ambiente_id': ambiente_id})
    
    def deletar_ambiente(request, ambiente_id):
        return render(request, 'ambiente/deletar.html', {'ambiente_id': ambiente_id})
    
    