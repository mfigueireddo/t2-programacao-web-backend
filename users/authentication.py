"""Autenticação (provisória) do domínio de Usuários.

Enquanto o projeto não possui login/autenticação de verdade (cf. observação em
:mod:`users.models`), esta classe oferece uma forma **temporária** de o backend
descobrir *quem* está fazendo a requisição: o cliente informa o ``id`` do
usuário no cabeçalho HTTP ``X-User-Id`` e o backend resolve a instância
correspondente, populando ``request.user`` exatamente como uma autenticação real
faria.

Atenção (segurança):
    Este mecanismo é **inseguro** e serve apenas para destravar as regras de
    autorização por papel durante o desenvolvimento. Qualquer cliente pode se
    declarar o usuário que quiser, pois não há prova de identidade (senha,
    token assinado, etc.). Deve ser substituído por autenticação real (ex.:
    Token/JWT) antes de qualquer uso em produção. Por se basear em
    ``request.user``, a troca não exigirá mudanças nas permissões nem nos
    serializers.
"""

from rest_framework import authentication, exceptions

from .models import User


class ProvisionalHeaderAuthentication(authentication.BaseAuthentication):
    """Resolve o usuário da requisição a partir do cabeçalho ``X-User-Id``.

    Descrição:
        Lê o ``id`` enviado no cabeçalho ``X-User-Id`` e devolve o
        :class:`users.models.User` correspondente para que o DRF o exponha em
        ``request.user``. Na ausência do cabeçalho, a requisição é tratada como
        anônima (``request.user`` torna-se ``AnonymousUser``).

    Objetivo:
        Fornecer, de forma provisória, a identidade necessária para as regras de
        autorização por papel, sem ainda implementar autenticação completa.

    Assertivas de entrada:
        - Quando presente, ``X-User-Id`` é o ``id`` (inteiro) de um usuário
          existente.

    Assertivas de saída:
        - Sem o cabeçalho: retorna ``None`` (acesso anônimo).
        - Com cabeçalho válido: retorna ``(user, None)`` e ``user`` passa a ser
          ``request.user``.
        - Com cabeçalho inválido (não numérico ou usuário inexistente): levanta
          ``AuthenticationFailed`` (HTTP 401).
    """

    def authenticate(self, request):
        """Identifica o usuário da requisição pelo cabeçalho ``X-User-Id``.

        Parâmetros:
            self (ProvisionalHeaderAuthentication): A instância autenticadora.
            request (rest_framework.request.Request): A requisição recebida.

        Assertivas de entrada:
            - ``request`` expõe os cabeçalhos HTTP em ``request.headers``.

        Assertivas de saída:
            - Retorna ``None`` quando ``X-User-Id`` está ausente.
            - Retorna ``(User, None)`` quando o cabeçalho referencia um usuário
              existente.

        Retornos:
            tuple[User, None] | None: O par ``(usuário, auth)`` exigido pelo DRF,
            ou ``None`` para indicar requisição anônima.
        """
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            # Sem cabeçalho: requisição anônima. As permissões decidem se o
            # acesso anônimo é permitido para a ação solicitada.
            return None

        try:
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            raise exceptions.AuthenticationFailed(
                'Cabeçalho X-User-Id inválido: usuário não encontrado.'
            )

        return (user, None)
