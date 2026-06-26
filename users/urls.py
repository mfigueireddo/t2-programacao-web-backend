"""
Roteamento de URLs do domínio de Usuários (Users).

Mapeia os caminhos do app (incluídos na raiz pela URLconf do projeto) para as
views de :mod:`users.views`, cobrindo tanto a autenticação quanto a gestão de
usuários.

Rotas de autenticação:
    - ``POST auth/signup/``          -> cadastro de usuário.
    - ``POST auth/login/``           -> login (retorna token + dados do usuário).
    - ``POST auth/logout/``          -> logout (invalida o token atual).
    - ``GET    auth/me/``              -> dados do usuário autenticado.
    - ``DELETE auth/me/``              -> exclui a conta do usuário autenticado.
    - ``POST   auth/change-password/`` -> troca de senha do usuário autenticado.
    - ``POST   auth/forgot-password/`` -> inicia a recuperação de senha.
    - ``POST   auth/reset-password/``  -> redefine a senha via token.

Rotas de usuários (``UserViewSet``):
    - ``GET    users/``        -> lista todos os usuários (apenas ADMINISTRADOR).
    - ``GET    users/<id>/``   -> detalha um usuário e seu papel.
    - ``DELETE users/<id>/``   -> exclui um usuário (o próprio ou ADMINISTRADOR).
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    ForgotPasswordView,
    LoginView,
    LogoutView,
    MeView,
    ResetPasswordView,
    SignupView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='auth-signup'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='auth-reset-password'),
]

urlpatterns += router.urls