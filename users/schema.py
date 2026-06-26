"""Extensão para documentar o token Bearer no Swagger."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension

class TokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'users.authentication.TokenAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'Token',
            'description': 'Informe o token retornado pelo login no formato: Bearer <token>.',
        }