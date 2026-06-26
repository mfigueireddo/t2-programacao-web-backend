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

"""Autenticação por token para a API."""

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