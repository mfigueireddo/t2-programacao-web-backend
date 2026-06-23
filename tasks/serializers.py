"""Serializers do domínio de Tarefas (Tasks).

Define a tradução entre instâncias do modelo :class:`tasks.models.Task` e a
representação JSON consumida/produzida pela API REST, além de validar os dados
de entrada antes da persistência.
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from .models import Task


@extend_schema_serializer(
    description=(
        "Representação de uma tarefa do quadro Kanban, usada tanto na entrada "
        "(criação/atualização) quanto na saída da API. Os campos ``id`` e "
        "``created_at`` são somente leitura."
    ),
)
class TaskSerializer(serializers.ModelSerializer):
    """Serializa e valida tarefas para a API REST.

    Descrição:
        Converte instâncias de ``Task`` em estruturas JSON (serialização) e
        valida/desserializa dados recebidos do cliente em instâncias de ``Task``.

    Objetivo:
        Centralizar as regras de exposição e validação dos campos de tarefa,
        garantindo que apenas dados válidos cheguem ao modelo.

    Assertivas de entrada (ao validar dados recebidos):
        - ``name`` está presente, é string e tem no máximo 255 caracteres.
        - ``status``, quando presente, pertence a :class:`Task.Status`.
        - ``story_points``, quando presente, é inteiro entre 0 e 100.
        - ``id`` e ``created_at`` não são aceitos como entrada (somente leitura).

    Assertivas de saída (ao serializar uma instância):
        - O dicionário resultante contém todos os campos declarados em ``fields``.
        - ``id`` e ``created_at`` refletem os valores persistidos.
    """

    class Meta:
        """Configuração de mapeamento entre o serializer e o modelo ``Task``.

        Descrição:
            Indica o modelo de origem, os campos expostos e quais são apenas
            de leitura.

        Objetivo:
            Declarar de forma explícita o contrato de dados da API de tarefas.
        """

        model = Task
        fields = [
            'id',
            'name',
            'status',
            'description',
            'story_points',
            'created_at',
            'due_date',
            'closed_at',
        ]
        read_only_fields = ['id', 'created_at']
