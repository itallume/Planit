from .views import AtividadeView, AtividadeListView
from django.urls import path

urlpatterns = [
    path('', AtividadeListView.as_view(), name='lista_atividades'),
    path('criar/', AtividadeView.criar_atividade, name='criar_atividade'),
    path('<int:atividade_id>/', AtividadeView.detalhe_atividade, name='detalhe_atividade'),
    path('<int:atividade_id>/editar/', AtividadeView.editar_atividade, name='editar_atividade'),
    path('<int:atividade_id>/deletar/', AtividadeView.deletar_atividade, name='deletar_atividade'),
]