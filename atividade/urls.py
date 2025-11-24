from .views import (
    AtividadeListView, AtividadeDetailView, AtividadeCreateView, 
    AtividadeUpdateView, AtividadeDeleteView
)
from django.urls import path

urlpatterns = [
    path('', AtividadeListView.as_view(), name='lista_atividades'),
    path('criar/', AtividadeCreateView.as_view(), name='criar_atividade'),
    path('<int:atividade_id>/', AtividadeDetailView.as_view(), name='detalhe_atividade'),
    path('<int:atividade_id>/editar/', AtividadeUpdateView.as_view(), name='editar_atividade'),
    path('<int:atividade_id>/deletar/', AtividadeDeleteView.as_view(), name='deletar_atividade'),
]