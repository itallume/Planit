from .models import AmbienteInvitations, Notificacao

def invitations_processor(request):
    if request.user.is_authenticated:
        invitations = AmbienteInvitations.objects.filter(guest=request.user, accepted=False).select_related('inviter', 'ambiente')
        return {
            'pending_invitations': invitations,
            'invitations_count': invitations.count()
        }
    return {
        'pending_invitations': [],
        'invitations_count': 0
    }


def notificacoes_processor(request):
    """Context processor para adicionar notificações não lidas ao contexto"""
    if request.user.is_authenticated:
        notificacoes = Notificacao.objects.filter(usuario=request.user, lida=False).select_related('atividade', 'ambiente')[:10]
        return {
            'notificacoes_nao_lidas': notificacoes,
            'notificacoes_nao_lidas_count': notificacoes.count()
        }
    return {
        'notificacoes_nao_lidas': [],
        'notificacoes_nao_lidas_count': 0
    }
