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

from rest_framework import permissions

from users.models import User


class TaskPermission(permissions.BasePermission):
    """Autoriza ações sobre tarefas conforme o papel do requisitante.

    Descrição:
        Implementa, no nível da ação (endpoint), as restrições de criação,
        visualização, edição e remoção de tarefas em função do papel do usuário
        presente em ``request.user``.

    Objetivo:
        Garantir que apenas administradores criem ou removam tarefas e que a
        edição exija um usuário autenticado, deixando as restrições de campo da
        edição por usuário comum para o serializer.

    Assertivas de entrada:
        - ``request.user`` é um :class:`users.models.User` autenticado ou um
          usuário anônimo (``is_authenticated`` falso).
        - ``view.action`` identifica a operação do ``ModelViewSet``.

    Assertivas de saída:
        - Visualização é permitida a qualquer requisitante.
        - Criação e remoção exigem ``role == ADMINISTRADOR``.
        - Edição exige usuário autenticado (de qualquer papel).
    """

    message = 'Você não tem permissão para executar esta ação sobre tarefas.'

    def has_permission(self, request, view):
        """Decide se a ação solicitada é permitida ao requisitante.

        Parâmetros:
            self (TaskPermission): A instância de permissão.
            request (rest_framework.request.Request): A requisição recebida, com
                ``request.user`` já resolvido pela camada de autenticação.
            view (rest_framework.viewsets.ViewSet): A view alvo, cujo
                ``action`` indica a operação.

        Assertivas de entrada:
            - ``view.action`` pertence ao conjunto de ações de um
              ``ModelViewSet`` (``list``, ``retrieve``, ``create``, ``update``,
              ``partial_update`` ou ``destroy``).

        Assertivas de saída:
            - Retorna ``True`` apenas quando o papel do requisitante autoriza a
              ação; caso contrário, ``False`` (resultando em HTTP 403).

        Retornos:
            bool: ``True`` se a ação é permitida; ``False`` caso contrário.
        """
        # Visualização é liberada para todos (inclusive acesso anônimo).
        if view.action in ('list', 'retrieve'):
            return True

        user = request.user

        # Demais ações exigem um usuário identificado.
        if not getattr(user, 'is_authenticated', False):
            return False

        # Criação e remoção: exclusivas do administrador.
        if view.action in ('create', 'destroy'):
            return user.role == User.Role.ADMINISTRADOR

        # Edição: liberada a qualquer usuário autenticado no nível do endpoint;
        # as restrições por campo do usuário comum ficam no serializer.
        if view.action in ('update', 'partial_update'):
            return True

        # Qualquer outra ação não prevista é negada por padrão.
        return False
