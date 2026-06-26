"""Permissões (autorização por papel) do domínio de Tarefas.

Define quem pode executar cada ação sobre tarefas, com base no papel
(:class:`users.models.User.Role`) do usuário identificado em ``request.user``.

Regras de endpoint (decididas aqui):
    - Visualizar (``list``/``retrieve``): liberado para todos.
    - Criar (``create``): apenas ``ADMINISTRADOR``.
    - Remover (``destroy``): apenas ``ADMINISTRADOR``.
    - Editar (``update``/``partial_update``): ``ADMINISTRADOR`` ou ``USUARIO``.

A edição por ``USUARIO`` é liberada *no nível do endpoint*, mas é restrita *no
nível dos campos* (só ``status`` e atribuir/remover a si mesmo como
responsável). Essa parte, por depender do conteúdo enviado, é validada no
serializer
(:class:`tasks.serializers.TaskSerializer`), não aqui.
"""

"""Permissões de tarefas."""

from rest_framework import permissions

from users.models import User


class TaskPermission(permissions.BasePermission):
    """Autoriza ações sobre tarefas conforme o papel do usuário logado."""

    message = 'Você não tem permissão para executar esta ação sobre tarefas.'

    def has_permission(self, request, view):
        user = request.user

        if not getattr(user, 'is_authenticated', False):
            return False

        if view.action in ('list', 'retrieve'):
            return True

        if view.action in ('create', 'destroy'):
            return user.role == User.Role.ADMINISTRADOR

        if view.action in ('update', 'partial_update'):
            return True

        return False