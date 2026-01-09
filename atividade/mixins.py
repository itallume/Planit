from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from ambiente.models import Ambiente


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
        # ajeitar
        #essa bomba desse git
