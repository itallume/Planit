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
from ambiente.models import Ambiente, AmbienteInvitations, Participante, Role
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
import json
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
    
    @login_required
    def configurar_ambiente(request, ambiente_id):
        ambiente = Ambiente.objects.get(id=ambiente_id)
        users_participantes = ambiente.usuarios_participantes.all()
        
        # Buscar participantes com suas roles
        participantes_data = []
        for user in users_participantes:
            try:
                participante = Participante.objects.get(usuario=user, ambiente=ambiente)
                participantes_data.append({
                    'user': user,
                    'participante': participante
                })
            except Participante.DoesNotExist:
                # Se não existir Participante, criar com role padrão (Leitor)
                role_leitor = Role.objects.filter(ambiente=ambiente, nome=Role.LEITOR).first()
                participante = Participante.objects.create(
                    usuario=user,
                    ambiente=ambiente,
                    role=role_leitor
                )
                participantes_data.append({
                    'user': user,
                    'participante': participante
                })
        
        return render(request, 'ambiente/configurar.html', {
            'ambiente': ambiente, 
            'users_participantes': users_participantes,
            'participantes_data': participantes_data
        })
    
  


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
        
        # Criar Participante com role Leitor por padrão
        role_leitor = Role.objects.filter(ambiente=ambiente, nome=Role.LEITOR).first()
        Participante.objects.get_or_create(
            usuario=request.user,
            ambiente=ambiente,
            defaults={'role': role_leitor}
        )
        
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


@login_required
def editar_permissoes_participante(request, ambiente_id, participante_id):
    """
    Edita as permissões de um participante no ambiente.
    Recebe JSON com as permissões via POST.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido.'
        }, status=405)
    
    # Verificar se o usuário tem permissão para editar (deve ser administrador do ambiente)
    ambiente = get_object_or_404(Ambiente, id=ambiente_id)
    if ambiente.usuario_administrador != request.user:
        return JsonResponse({
            'success': False,
            'message': 'Você não tem permissão para editar permissões neste ambiente.'
        }, status=403)
    
    # Buscar o participante
    participante = get_object_or_404(Participante, id=participante_id, ambiente=ambiente)
    
    try:
        data = json.loads(request.body)
        
        # Extrair permissões do request
        pode_visualizar = data.get('pode_visualizar_atividades', True)
        pode_criar = data.get('pode_criar_atividades', False)
        pode_editar = data.get('pode_editar_atividades', False)
        pode_deletar = data.get('pode_deletar_atividades', False)
        
        # Verificar se é uma role predefinida ou criar custom
        role_nome = None
        
        # Leitor: apenas visualizar
        if pode_visualizar and not pode_criar and not pode_editar and not pode_deletar:
            role_nome = Role.LEITOR
        # Editor: visualizar, criar e editar
        elif pode_visualizar and pode_criar and pode_editar and not pode_deletar:
            role_nome = Role.EDITOR
        # Administrador: todas as permissões
        elif pode_visualizar and pode_criar and pode_editar and pode_deletar:
            role_nome = Role.ADMINISTRADOR
        # Custom: qualquer outra combinação
        else:
            role_nome = Role.CUSTOM
        
        # Buscar ou criar a role
        if role_nome == Role.CUSTOM:
            # Para custom, criar uma nova role ou atualizar a existente se for custom
            if participante.role and participante.role.nome == Role.CUSTOM:
                # Atualizar role custom existente
                role = participante.role
                role.pode_visualizar_atividades = pode_visualizar
                role.pode_criar_atividades = pode_criar
                role.pode_editar_atividades = pode_editar
                role.pode_deletar_atividades = pode_deletar
                role.save()
            else:
                # Criar nova role custom
                role = Role.objects.create(
                    nome=Role.CUSTOM,
                    ambiente=ambiente,
                    pode_visualizar_atividades=pode_visualizar,
                    pode_criar_atividades=pode_criar,
                    pode_editar_atividades=pode_editar,
                    pode_deletar_atividades=pode_deletar
                )
        else:
            # Buscar ou criar role predefinida
            role, created = Role.objects.get_or_create(
                ambiente=ambiente, 
                nome=role_nome,
                defaults={
                    'pode_visualizar_atividades': pode_visualizar,
                    'pode_criar_atividades': pode_criar,
                    'pode_editar_atividades': pode_editar,
                    'pode_deletar_atividades': pode_deletar
                }
            )
        
        # Atualizar participante
        participante.role = role
        participante.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Permissões de {participante.usuario.username} atualizadas com sucesso.',
            'role': role.get_nome_display()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar permissões: {str(e)}'
        }, status=500)


@login_required
def obter_permissoes_participante(request, ambiente_id, participante_id):
    """
    Retorna as permissões atuais de um participante.
    """
    ambiente = get_object_or_404(Ambiente, id=ambiente_id)
    participante = get_object_or_404(Participante, id=participante_id, ambiente=ambiente)
    
    if not participante.role:
        # Se não tem role, retornar permissões padrão (Leitor)
        return JsonResponse({
            'success': True,
            'pode_visualizar_atividades': True,
            'pode_criar_atividades': False,
            'pode_editar_atividades': False,
            'pode_deletar_atividades': False,
            'role': 'Leitor'
        })
    
    return JsonResponse({
        'success': True,
        'pode_visualizar_atividades': participante.role.pode_visualizar_atividades,
        'pode_criar_atividades': participante.role.pode_criar_atividades,
        'pode_editar_atividades': participante.role.pode_editar_atividades,
        'pode_deletar_atividades': participante.role.pode_deletar_atividades,
        'role': participante.role.get_nome_display()
    })


# === Views de Notificações ===

@login_required
def listar_notificacoes(request):
    """Lista todas as notificações do usuário."""
    from ambiente.models import Notificacao
    
    notificacoes = Notificacao.objects.filter(usuario=request.user)
    nao_lidas = notificacoes.filter(lida=False)
    
    return render(request, 'ambiente/notificacoes.html', {
        'notificacoes': notificacoes,
        'nao_lidas_count': nao_lidas.count()
    })


@login_required
def marcar_notificacao_lida(request, notificacao_id):
    """Marca uma notificação como lida. GET redireciona, POST retorna JSON."""
    from ambiente.models import Notificacao
    
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    notificacao.lida = True
    notificacao.save()
    
    # Se for POST (via AJAX), retorna JSON
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'Notificação marcada como lida.'
        })
    
    # Se for GET, redirecionar para o link da notificação
    if notificacao.link:
        return redirect(notificacao.link)
    else:
        return redirect('lista_ambientes')


@login_required
def marcar_todas_lidas(request):
    """Marca todas as notificações como lidas."""
    from ambiente.models import Notificacao
    
    if request.method == 'POST':
        Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
        return JsonResponse({
            'success': True,
            'message': 'Todas as notificações foram marcadas como lidas.'
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)


@login_required
def contagem_notificacoes(request):
    """Retorna a contagem de notificações não lidas (para uso em AJAX)."""
    from ambiente.models import Notificacao
    
    count = Notificacao.objects.filter(usuario=request.user, lida=False).count()
    return JsonResponse({'count': count})