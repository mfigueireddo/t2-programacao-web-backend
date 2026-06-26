"""Roteamento de URLs do domínio de Usuários (Users).

Mapeia os caminhos do app (montados sob o prefixo ``users/`` pela URLconf raiz)
para as views do :mod:`users.views`. Por ora, expõe apenas a consulta de um
usuário por ``id`` para descoberta de papel (permissão) e a listagem de todos
os usuários (restrita a administradores).

Rotas expostas:
    - ``GET users/`` -> lista todos os usuários (apenas ADMINISTRADOR).
    - ``GET users/<id>/`` -> detalha um usuário e seu papel.
"""

"""Rotas de usuários e autenticação."""

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