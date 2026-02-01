from pyexpat.errors import messages
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, CreateView
import secrets

from ambiente.forms import AmbienteForm, SendInvitationForm
from ambiente.models import Ambiente, AmbienteInvitations
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
# Create your views here.

class AmbienteView:
    @login_required
    def lista_ambientes(request):
        # Filtrar apenas ambientes onde o usuário é administrador OU participante
        invitations = AmbienteInvitations.objects.filter(guest=request.user, accepted=False)

        ambientes = Ambiente.objects.filter(
            Q(usuario_administrador=request.user) | Q(usuarios_participantes=request.user)
        ).distinct().annotate(
            num_atividades=Count('atividade'),
            num_pendentes=Count('atividade', filter=Q(atividade__status='Pendente')),
            num_concluidas=Count('atividade', filter=Q(atividade__status='Concluído')),
            num_atrasadas=Count('atividade', filter=Q(atividade__status='Atrasado'))
        )
        form = AmbienteForm()
        return render(request, 'ambiente/home.html', {'ambientes': ambientes, 'invitations': invitations, 'form': form})
    
    @login_required
    def detalhe_ambiente(request, ambiente_id):
        ambiente = Ambiente.objects.get(id=ambiente_id)
        atividades = ambiente.atividade_set.all()
        return render(request, 'ambiente/detalhe.html', {
            'ambiente': ambiente,
            'atividades': atividades
        })
    
    @login_required
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
                ambiente = form.save(commit=False)
                ambiente.usuario_administrador = request.user
                ambiente.save()
                return redirect('lista_ambientes')
            else:
                # Renderiza home.html com o form preenchido e erros
                return render(request, 'ambiente/home.html', {'ambientes': ambientes, 'form': form})
        # Se acessar diretamente, redireciona para lista
        return redirect('lista_ambientes')
    
    @login_required
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
    
    @login_required
    def deletar_ambiente(request, ambiente_id):
        ambiente = Ambiente.objects.get(id=ambiente_id)
        if request.method == 'POST':
            ambiente.delete()
            return redirect('lista_ambientes')
        return redirect('lista_ambientes')
    
class CreateAmbienteInvitationView(LoginRequiredMixin, CreateView):
    model = AmbienteInvitations
    form_class = SendInvitationForm
    template_name = 'ambiente/send_invitation.html'

    def post(self, request, ambiente_id):
        ambiente = get_object_or_404(Ambiente, id=ambiente_id)
        email = request.POST.get('email')
        
        token = secrets.token_hex(32)

        guest = User.objects.filter(email=email).first()
        if not guest:
            messages.error(request, 'Usuário com este email não encontrado.')
            return redirect('lista_ambientes', ambiente_id=ambiente.id)
        
        invitation = AmbienteInvitations.objects.create(
            inviter=request.user,
            ambiente=ambiente,
            email=email,
            token=token,
            guest=guest
        )
        messages.success(request, f'Convite para {email} enviado com sucesso.')
        return redirect('lista_ambientes', ambiente_id=ambiente.id)
    
    
class AcceptAmbienteInvitationView(LoginRequiredMixin, View):
    def post(self, request, token):
        convite = get_object_or_404(AmbienteInvitations, token=token, guest=request.user, accepted=False)
        ambiente = convite.ambiente
        ambiente.usuarios_participantes.add(request.user)
        convite.accepted = True
        convite.save()
        
        return redirect('lista_ambientes')

    