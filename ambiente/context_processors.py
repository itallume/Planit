from .models import AmbienteInvitations

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
