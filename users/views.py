"""Views (camada de API) do domínio de Usuários (Users).

Expõe a consulta de um usuário por ``id`` para que o frontend descubra seu papel
(permissão). Enquanto não há autenticação por token, esta é a forma de o cliente
saber quais ações deve habilitar na interface para o usuário informado.

Expõe também a listagem de todos os usuários do sistema, restrita a
administradores autenticados.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions

from .models import User
from .permissions import IsAdministrador
from .serializers import UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Consulta o papel de um usuário",
        description=(
            "Retorna os dados do usuário identificado por ``{id}``, incluindo "
            "seu papel (``role``) e o rótulo legível (``role_display``). "
            "Permite ao frontend descobrir as permissões do usuário enquanto a "
            "autenticação por token não está disponível. Responde "
            "``404 Not Found`` se o ``id`` não existir."
        ),
    ),
)
class UserRetrieveView(generics.RetrieveAPIView):
    """Endpoint REST para consultar um usuário (e seu papel) por ``id``.

    Descrição:
        Disponibiliza a operação de detalhe de usuário, devolvendo o papel
        associado ao ``id`` informado na URL.

    Objetivo:
        Atender ``GET /users/{id}/``, permitindo que o frontend descubra o papel
        do usuário e adapte a interface às permissões correspondentes. Por não
        haver ainda autenticação por token, a identificação é feita pelo ``id``
        passado na rota, e não por uma credencial.

    Assertivas de entrada:
        - ``{id}`` referencia um usuário existente; caso contrário, responde
          ``404 Not Found``.

    Assertivas de saída:
        - Em caso de sucesso, retorna ``200 OK`` com a representação do usuário
          (``id``, ``name``, ``role`` e ``role_display``).

    Retornos:
        rest_framework.response.Response: Resposta HTTP com os dados do usuário
        (gerada pelo método herdado de ``RetrieveAPIView``).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # A consulta de papel é liberada para qualquer requisitante: o frontend
    # precisa dela justamente para decidir o que exibir antes de qualquer ação
    # protegida.
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    get=extend_schema(
        summary="Lista todos os usuários do sistema",
        description=(
            "Retorna a coleção completa de usuários cadastrados, incluindo o "
            "papel (``role``) e o rótulo legível (``role_display``) de cada um. "
            "Acesso restrito: apenas usuários autenticados com papel "
            "``ADMINISTRADOR`` podem consultar. Responde ``401 Unauthorized`` "
            "para acesso anônimo e ``403 Forbidden`` para usuários sem o papel "
            "de administrador."
        ),
    ),
)
class UserListView(generics.ListAPIView):
    """Endpoint REST para listar todos os usuários do sistema.

    Descrição:
        Disponibiliza a operação de listagem de usuários, devolvendo a coleção
        completa de cadastros. O acesso é exclusivo de administradores
        autenticados.

    Objetivo:
        Atender ``GET /users/``, permitindo que um administrador obtenha todos
        os usuários do sistema (com seus papéis).

    Assertivas de entrada:
        - ``request.user`` está autenticado e possui ``role == ADMINISTRADOR``;
          caso contrário, responde ``401 Unauthorized`` (anônimo) ou
          ``403 Forbidden`` (papel insuficiente).

    Assertivas de saída:
        - Em caso de sucesso, retorna ``200 OK`` com a lista de usuários
          (``id``, ``name``, ``role`` e ``role_display`` de cada um).

    Retornos:
        rest_framework.response.Response: Resposta HTTP com a lista de usuários
        (gerada pelo método herdado de ``ListAPIView``).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Listagem completa é uma operação administrativa: exige usuário
    # autenticado com papel ADMINISTRADOR.
    permission_classes = [IsAdministrador]
