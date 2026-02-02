from .views import  AmbienteView, AmbienteInvitationViewSet
from django.urls import include, path

invitation_create = AmbienteInvitationViewSet.as_view({
    'post': 'create'
})

urlpatterns = [
    path('', AmbienteView.lista_ambientes, name='lista_ambientes'),
    path('criar/', AmbienteView.criar_ambiente, name='criar_ambiente'),
    path('<int:ambiente_id>/', AmbienteView.detalhe_ambiente, name='detalhe_ambiente'),
    path('<int:ambiente_id>/editar/', AmbienteView.editar_ambiente, name='editar_ambiente'),
    path('<int:ambiente_id>/deletar/', AmbienteView.deletar_ambiente, name='deletar_ambiente'),
    path('<int:ambiente_id>/convidar/', invitation_create, name='enviar_convite'),
]