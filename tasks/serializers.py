"""Serializers do domínio de Tarefas (Tasks).

Define a tradução entre instâncias do modelo :class:`tasks.models.Task` e a
representação JSON consumida/produzida pela API REST, além de validar os dados
de entrada antes da persistência.
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from users.models import User

from .models import Task


@extend_schema_serializer(
    description=(
        "Representação de uma tarefa do quadro Kanban, usada tanto na entrada "
        "(criação/atualização) quanto na saída da API. Os campos ``id``, "
        "``created_at``, ``closed_at`` e ``creator_name`` são somente leitura "
        "(``closed_at`` é derivado do status; ``creator_name`` é o nome do "
        "criador, devolvido sem consultar a tabela de usuários). O ``creator`` "
        "é obrigatório na criação e imutável depois."
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
        - ``creator`` está presente e referencia o ``id`` de um usuário
          existente na criação (obrigatório); em atualizações é ignorado, pois
          o criador é imutável após a criação.
        - ``responsibles``, quando presente, é uma lista de ``id`` de usuários
          existentes (pode ser vazia ou omitida).
        - ``id``, ``created_at``, ``closed_at`` e ``creator_name`` não são
          aceitos como entrada (somente leitura); ``closed_at`` é derivado do
          ``status`` e ``creator_name`` é gerido a partir do criador.

    Assertivas de saída (ao serializar uma instância):
        - O dicionário resultante contém todos os campos declarados em ``fields``.
        - ``id`` e ``created_at`` refletem os valores persistidos.
        - ``creator_name`` contém o nome do criador (cópia desnormalizada),
          dispensando consulta à tabela de usuários.
    """

    # ``creator`` é declarado explicitamente para ser obrigatório na criação
    # (o modelo permite ``null`` apenas para sobreviver à exclusão da conta, o
    # que, por padrão, tornaria o campo opcional no serializer).
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        """Torna ``creator`` somente leitura em atualizações.

        Descrição:
            Em operações de atualização (quando há instância associada), marca o
            campo ``creator`` como somente leitura, pois o criador não pode ser
            alterado após a criação. Em criações, o campo permanece obrigatório.

        Parâmetros:
            *args: Argumentos posicionais repassados ao ``__init__`` do DRF.
            **kwargs: Argumentos nomeados repassados ao ``__init__`` do DRF.

        Assertivas de saída:
            - Se houver instância (atualização), ``creator`` fica somente
              leitura e é ignorado na entrada.
        """
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['creator'].read_only = True

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
            'creator',
            'creator_name',
            'responsibles',
        ]
        read_only_fields = ['id', 'created_at', 'closed_at', 'creator_name']
