from .views import (
    AtividadeDetailView, AtividadeCreateView, 
    AtividadeUpdateView, AtividadeDeleteView, AtividadesPorAmbienteView,
    buscar_clientes, buscar_enderecos_cliente, download_referencia
)
from django.urls import path

urlpatterns = [
    # path('', AtividadeListView.as_view(), name='lista_atividades'),
    path('criar/', AtividadeCreateView.as_view(), name='criar_atividade'),
    path('api/buscar-clientes/', buscar_clientes, name='buscar_clientes'),
    path('api/cliente/<int:cliente_id>/enderecos/', buscar_enderecos_cliente, name='buscar_enderecos_cliente'),
    path('ambiente/<int:ambiente_id>/', AtividadesPorAmbienteView.as_view(), name='atividades_por_ambiente'),
    path('<int:atividade_id>/editar/', AtividadeUpdateView.as_view(), name='editar_atividade'),
    path('<int:atividade_id>/deletar/', AtividadeDeleteView.as_view(), name='deletar_atividade'),
    path('<int:atividade_id>/', AtividadeDetailView.as_view(), name='detalhe_atividade'),
    path('referencia/<int:referencia_id>/download/', download_referencia, name='download_referencia'),
]