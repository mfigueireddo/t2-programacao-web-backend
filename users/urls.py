"""Roteamento de URLs do domínio de Usuários (Users).

Mapeia os caminhos do app (montados sob o prefixo ``users/`` pela URLconf raiz)
para as views do :mod:`users.views`. Por ora, expõe apenas a consulta de um
usuário por ``id`` para descoberta de papel (permissão) e a listagem de todos
os usuários (restrita a administradores).

Rotas expostas:
    - ``GET users/`` -> lista todos os usuários (apenas ADMINISTRADOR).
    - ``GET users/<id>/`` -> detalha um usuário e seu papel.
"""

from django.urls import path

from .views import UserListView, UserRetrieveView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserRetrieveView.as_view(), name='user-detail'),
]
