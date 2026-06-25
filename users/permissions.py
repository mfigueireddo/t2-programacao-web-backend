"""Permissões (autorização por papel) do domínio de Usuários (Users).

Define quem pode executar cada ação sobre usuários, com base no papel
(:class:`users.models.User.Role`) do usuário identificado em ``request.user``.
"""

from rest_framework import permissions

from .models import User


class IsAdministrador(permissions.BasePermission):
    """Autoriza apenas usuários autenticados com papel ``ADMINISTRADOR``.

    Descrição:
        Restringe o acesso ao requisitante presente em ``request.user`` que
        esteja autenticado e cujo papel seja ``ADMINISTRADOR``.

    Objetivo:
        Proteger endpoints administrativos (como a listagem de todos os
        usuários do sistema), garantindo que apenas administradores possam
        acessá-los.

    Assertivas de entrada:
        - ``request.user`` é um :class:`users.models.User` autenticado ou um
          usuário anônimo (``is_authenticated`` falso).

    Assertivas de saída:
        - Retorna ``True`` apenas quando o requisitante está autenticado e seu
          papel é ``ADMINISTRADOR``; caso contrário, ``False``.
    """

    message = 'Apenas administradores podem executar esta ação.'

    def has_permission(self, request, view):
        """Decide se o requisitante é um administrador autenticado.

        Parâmetros:
            self (IsAdministrador): A instância de permissão.
            request (rest_framework.request.Request): A requisição recebida, com
                ``request.user`` já resolvido pela camada de autenticação.
            view (rest_framework.generics.GenericAPIView): A view alvo.

        Assertivas de entrada:
            - ``request.user`` foi resolvido pela camada de autenticação.

        Assertivas de saída:
            - Retorna ``True`` somente para um usuário autenticado com
              ``role == ADMINISTRADOR``; caso contrário, ``False`` (resultando
              em HTTP 401/403).

        Retornos:
            bool: ``True`` se o requisitante é administrador; ``False`` caso
            contrário.
        """
        user = request.user

        if not getattr(user, 'is_authenticated', False):
            return False

        return user.role == User.Role.ADMINISTRADOR
