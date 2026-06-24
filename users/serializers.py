"""Serializers do domínio de Usuários (Users).

Define a tradução entre instâncias do modelo :class:`users.models.User` e a
representação JSON produzida pela API REST. Por ora, expõe apenas os dados
necessários para que o frontend descubra o papel (permissão) de um usuário.
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from .models import User


@extend_schema_serializer(
    description=(
        "Representação somente leitura de um usuário, usada para que o frontend "
        "consulte o papel (permissão) associado a um ``id``. O campo "
        "``role_display`` traz o rótulo legível correspondente ao ``role``."
    ),
)
class UserSerializer(serializers.ModelSerializer):
    """Serializa usuários para a consulta de papel pela API REST.

    Descrição:
        Converte instâncias de ``User`` em estruturas JSON, expondo o
        identificador, o nome e o papel (com o respectivo rótulo legível).

    Objetivo:
        Permitir que o frontend, a partir do ``id`` de um usuário, descubra seu
        papel e ajuste a interface às permissões correspondentes, enquanto a
        autenticação definitiva (com tokens) não é implementada.

    Assertivas de entrada:
        - Não se aplica: o serializer é usado apenas para saída (somente
          leitura).

    Assertivas de saída (ao serializar uma instância):
        - O dicionário resultante contém ``id``, ``name``, ``role`` e
          ``role_display``.
        - ``role`` pertence a :class:`users.models.User.Role` e
          ``role_display`` é o seu rótulo legível.
    """

    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
        help_text='Rótulo legível do papel do usuário.',
    )

    class Meta:
        """Configuração de mapeamento entre o serializer e o modelo ``User``.

        Descrição:
            Indica o modelo de origem e os campos expostos (todos somente
            leitura).

        Objetivo:
            Declarar de forma explícita o contrato de dados da consulta de
            papel de usuário.
        """

        model = User
        fields = ['id', 'name', 'role', 'role_display']
        read_only_fields = fields
