from .views import signup_view, signin_view, logout_view, home_view
from django.urls import include, path

urlpatterns = [
    path('', home_view, name='home'),
    path('cadastro/', signup_view, name='signup'),
    path('entrar/', signin_view, name='signin'),
    path('sair/', logout_view, name='logout'),
]