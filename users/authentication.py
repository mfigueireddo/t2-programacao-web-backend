"""
Autenticação por token do domínio de Usuários.

O projeto possui autenticação própria baseada em tokens. Após o login (cf.
fluxo em :mod:`users`), o cliente recebe um token e o envia em cada requisição
no cabeçalho HTTP ``Authorization: Bearer <token>``. Esta classe lê esse
cabeçalho, valida o token contra o modelo :class:`users.models.AuthToken` e
popula ``request.user`` com o usuário correspondente, permitindo que as regras
de autorização por papel funcionem.

Por se basear em ``request.user``, as permissões e os serializers não precisam
conhecer os detalhes do mecanismo de autenticação.
"""

from rest_framework import authentication, exceptions

from .models import AuthToken


class TokenAuthentication(authentication.BaseAuthentication):
    """Autentica usando o cabeçalho Authorization: Bearer <token>."""

    keyword = 'Bearer'

    def authenticate(self, request):
        header = request.headers.get('Authorization')

        if not header:
            return None

        parts = header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed(
                'Cabeçalho Authorization inválido. Use: Bearer <token>.'
            )

        token_key = parts[1]

        try:
            token = AuthToken.objects.select_related('user').get(key=token_key)
        except AuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido ou expirado.')

        return token.user, token

    def authenticate_header(self, request):
        return self.keyword