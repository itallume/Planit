from .views import  AmbienteView, AmbienteInvitationViewSet, editar_permissoes_participante, obter_permissoes_participante
from django.urls import include, path

invitation_create = AmbienteInvitationViewSet.as_view({
    'post': 'create'
})

invitation_accept = AmbienteInvitationViewSet.as_view({
    'post': 'accept'
})

invitation_decline = AmbienteInvitationViewSet.as_view({
    'post': 'decline'
})

urlpatterns = [
    path('', AmbienteView.lista_ambientes, name='lista_ambientes'),
    path('criar/', AmbienteView.criar_ambiente, name='criar_ambiente'),
    path('<int:ambiente_id>/editar/', AmbienteView.editar_ambiente, name='editar_ambiente'),
    path('<int:ambiente_id>/deletar/', AmbienteView.deletar_ambiente, name='deletar_ambiente'),
    path('<int:ambiente_id>/convidar/', invitation_create, name='enviar_convite'),
    path('<int:ambiente_id>/configurar/', AmbienteView.configurar_ambiente, name='configurar_ambiente'),
    path('<int:ambiente_id>/participante/<int:participante_id>/permissoes/', editar_permissoes_participante, name='editar_permissoes'),
    path('<int:ambiente_id>/participante/<int:participante_id>/permissoes/obter/', obter_permissoes_participante, name='obter_permissoes'),
    path('convite/<int:pk>/aceitar/', invitation_accept, name='aceitar_convite'),
    path('convite/<int:pk>/recusar/', invitation_decline, name='recusar_convite'),
]