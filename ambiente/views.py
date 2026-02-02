from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, CreateView
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import secrets

from ambiente.forms import AmbienteForm, SendInvitationForm
from ambiente.serializers import AmbienteInvitationSerializer
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


class AmbienteInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar convites de ambiente.
    
    Actions:
    - create: Envia um novo convite (POST)
    - list: Lista convites pendentes do usuário (GET)
    - accept: Aceita um convite (POST /invitations/{id}/accept/)
    - decline: Recusa um convite (POST /invitations/{id}/decline/)
    """
    serializer_class = AmbienteInvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas convites do usuário logado"""
        return AmbienteInvitations.objects.filter(
            guest=self.request.user,
            accepted=False
        ).select_related('inviter', 'ambiente')
    
    def create(self, request, ambiente_id=None):
        """Envia um convite para o ambiente"""
        ambiente = get_object_or_404(Ambiente, id=ambiente_id)
        
        if ambiente.usuario_administrador != request.user and not ambiente.usuarios_participantes.filter(id=request.user.id).exists():
            return Response({
                'success': False,
                'message': 'Você não tem permissão para enviar convites neste ambiente.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AmbienteInvitationSerializer(
            data=request.data,
            context={'ambiente': ambiente, 'inviter': request.user}
        )
        
        if serializer.is_valid():
            invitation = serializer.save()
            return Response({
                'success': True,
                'message': f'Convite para {invitation.email} enviado com sucesso.'
            }, status=status.HTTP_201_CREATED)
        
        errors = serializer.errors
        error_message = errors.get('email', ['Erro ao enviar convite.'])[0]
        
        return Response({
            'success': False,
            'message': error_message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Aceita um convite"""
        invitation = self.get_object()
        
        if invitation.accepted:
            return Response({
                'success': False,
                'message': 'Este convite já foi aceito.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ambiente = invitation.ambiente
        ambiente.usuarios_participantes.add(request.user)
        invitation.accepted = True
        invitation.save()
        
        return Response({
            'success': True,
            'message': f'Você agora faz parte do ambiente "{ambiente.nome}"!'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Recusa um convite"""
        invitation = self.get_object()
        
        if invitation.accepted:
            return Response({
                'success': False,
                'message': 'Este convite já foi aceito.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ambiente_nome = invitation.ambiente.nome
        invitation.delete()
        
        return Response({
            'success': True,
            'message': f'Você recusou o convite para o ambiente "{ambiente_nome}".'
        }, status=status.HTTP_200_OK)
    


    