from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from ambiente.models import Ambiente, Participante


class AmbientePermissionMixin:
    """Mixin para verificar se o usuário tem permissão para acessar um ambiente"""
    
    def verificar_permissao_ambiente(self, ambiente):
        """Verifica se o usuário atual tem permissão para acessar o ambiente"""
        user = self.request.user
        return user == ambiente.usuario_administrador or user in ambiente.usuarios_participantes.all()
    
    def dispatch(self, request, *args, **kwargs):
        # Tentar obter o ambiente baseado em diferentes parâmetros
        ambiente = None
        
        # Para views com ambiente_id nos kwargs (lista, criar)
        if 'ambiente_id' in kwargs:
            ambiente = get_object_or_404(Ambiente, id=kwargs['ambiente_id'])
        # Para views com ambiente_id no GET (criar atividade)
        elif request.GET.get('ambiente_id'):
            try:
                ambiente = Ambiente.objects.get(id=request.GET.get('ambiente_id'))
            except Ambiente.DoesNotExist:
                messages.error(request, 'Ambiente não encontrado.')
                return redirect('lista_ambientes')
        # Para views de detalhe/edição/exclusão de atividade
        elif hasattr(self, 'get_object'):
            try:
                obj = self.model.objects.get(pk=kwargs.get(self.pk_url_kwarg or 'pk'))
                if hasattr(obj, 'ambiente'):
                    ambiente = obj.ambiente
            except self.model.DoesNotExist:
                pass
        
        # Verificar permissão se ambiente foi encontrado
        if ambiente and not self.verificar_permissao_ambiente(ambiente):
            messages.error(request, 'Você não tem permissão para acessar este ambiente.')
            return redirect('lista_ambientes')
        
        return super().dispatch(request, *args, **kwargs)


class AtividadePermissionMixin:
    """Mixin para verificar permissões CRUD de atividades baseado nas roles do usuário"""
    
    def get_user_permissions(self, ambiente):
        """Retorna as permissões do usuário no ambiente"""
        user = self.request.user
        
        # Administrador do ambiente tem todas as permissões
        if user == ambiente.usuario_administrador:
            return {
                'pode_visualizar_atividades': True,
                'pode_criar_atividades': True,
                'pode_editar_atividades': True,
                'pode_deletar_atividades': True
            }
        
        # Buscar participante e suas permissões
        try:
            participante = Participante.objects.get(usuario=user, ambiente=ambiente)
            if participante.role:
                return {
                    'pode_visualizar_atividades': participante.role.pode_visualizar_atividades,
                    'pode_criar_atividades': participante.role.pode_criar_atividades,
                    'pode_editar_atividades': participante.role.pode_editar_atividades,
                    'pode_deletar_atividades': participante.role.pode_deletar_atividades
                }
        except Participante.DoesNotExist:
            pass
        
        # Sem permissões por padrão
        return {
            'pode_visualizar_atividades': False,
            'pode_criar_atividades': False,
            'pode_editar_atividades': False,
            'pode_deletar_atividades': False
        }
    
    def verificar_permissao_criar(self, ambiente):
        """Verifica se o usuário pode criar atividades"""
        perms = self.get_user_permissions(ambiente)
        return perms['pode_criar_atividades']
    
    def verificar_permissao_editar(self, ambiente):
        """Verifica se o usuário pode editar atividades"""
        perms = self.get_user_permissions(ambiente)
        return perms['pode_editar_atividades']
    
    def verificar_permissao_deletar(self, ambiente):
        """Verifica se o usuário pode deletar atividades"""
        perms = self.get_user_permissions(ambiente)
        return perms['pode_deletar_atividades']
    
    def verificar_permissao_visualizar(self, ambiente):
        """Verifica se o usuário pode visualizar atividades"""
        perms = self.get_user_permissions(ambiente)
        return perms['pode_visualizar_atividades']
