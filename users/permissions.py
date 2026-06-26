"""Permissões (autorização por papel) do domínio de Usuários (Users).

Define quem pode executar cada ação sobre usuários, com base no papel
(:class:`users.models.User.Role`) do usuário identificado em ``request.user``.
"""

"""Permissões do domínio de Usuários."""

from rest_framework import permissions

from .models import User


class IsAdministrador(permissions.BasePermission):
    message = 'Apenas administradores podem executar esta ação.'

    def has_permission(self, request, view):
        user = request.user

        return (
            getattr(user, 'is_authenticated', False)
            and user.role == User.Role.ADMINISTRADOR
        )


class IsSelfOrAdministrador(permissions.BasePermission):
    message = 'Você só pode alterar sua própria conta.'

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not getattr(user, 'is_authenticated', False):
            return False

        return user.role == User.Role.ADMINISTRADOR or obj == user