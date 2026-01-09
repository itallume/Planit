from django.urls import path, include
from .views import ClienteViewSet, EnderecoViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'clientes/(?P<cliente_id>\d+)/enderecos', EnderecoViewSet, basename='cliente-enderecos')

urlpatterns=[
    path('', include(router.urls)),
]
