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
        - ``responsible``, quando presente, é o ``id`` de um usuário existente
          ou ``null`` (a tarefa tem no máximo um responsável, ou nenhum).
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

    # ``description`` é declarado explicitamente para aceitar ``null`` na entrada,
    # além de string vazia ou omissão. O modelo usa ``TextField(blank=True)`` sem
    # ``null=True`` (a convenção do Django é usar apenas string vazia); por isso o
    # valor ``None`` recebido é normalizado para ``""`` em ``validate_description``.
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

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

    def validate(self, attrs):
        """Aplica as restrições de edição do usuário comum (``USUARIO``).

        Descrição:
            Em atualizações feitas por um usuário de papel ``USUARIO``, restringe
            o que pode ser alterado: somente o ``status`` da tarefa e a atribuição
            do próprio usuário como responsável (ou a remoção de si mesmo).
            Administradores e criações não sofrem qualquer restrição aqui.

        Objetivo:
            Cumprir, no nível dos campos, as regras de autorização que a
            permissão de endpoint não consegue impor (pois dependem de *quais*
            campos mudaram e de *quem* está editando).

        Parâmetros:
            self (TaskSerializer): A instância do serializer.
            attrs (dict): Os dados já validados campo a campo. Em ``PATCH``,
                contém apenas os campos enviados; em ``PUT``, todos os graváveis.

        Assertivas de entrada:
            - Em atualização, ``self.instance`` referencia a tarefa alvo.
            - ``self.context['request'].user`` identifica o requisitante.

        Assertivas de saída:
            - Para ``USUARIO`` em atualização, levanta ``ValidationError`` se
              algum campo diferente de ``status``/``responsible`` for alterado,
              ou se o responsável for definido como alguém diferente do próprio
              usuário.
            - Nos demais casos, retorna ``attrs`` inalterado.

        Retornos:
            dict: Os atributos validados (eventualmente após rejeição por erro).
        """
        attrs = super().validate(attrs)

        # Restrições só se aplicam a atualizações (instância existente).
        if self.instance is None:
            return attrs

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # Sem usuário autenticado ou sendo administrador: nada a restringir aqui
        # (o acesso já foi autorizado pela permissão de endpoint).
        if not getattr(user, 'is_authenticated', False):
            return attrs
        if user.role != User.Role.USUARIO:
            return attrs

        self._validate_usuario_update(attrs, user)
        return attrs

    def _validate_usuario_update(self, attrs, user):
        """Verifica as alterações permitidas a um usuário comum em uma tarefa.

        Descrição:
            Auxilia :meth:`validate` impondo, para o papel ``USUARIO``, três
            restrições na atualização: (1) nenhum campo além de ``status`` e
            ``responsible`` pode mudar; (2) o usuário só pode atribuir-se como
            responsável quando a tarefa não tem nenhum, e só pode remover-se
            quando é o responsável atual (nunca atribuir nem remover terceiros);
            e (3) o ``status`` só pode ser alterado se o usuário for o
            responsável pela tarefa.

        Parâmetros:
            self (TaskSerializer): A instância do serializer.
            attrs (dict): Os dados validados da atualização.
            user (users.models.User): O usuário comum que faz a requisição.

        Assertivas de entrada:
            - ``self.instance`` referencia a tarefa em edição.

        Assertivas de saída:
            - Levanta ``serializers.ValidationError`` na primeira violação
              encontrada; não retorna valor em caso de sucesso.
            - A checagem de responsabilidade do ``status`` considera o estado
              resultante do responsável: se o usuário se atribui e altera o
              status na mesma requisição, a operação é aceita.

        Retornos:
            None.
        """
        # Campos cuja alteração é vedada ao usuário comum. ``status`` e
        # ``responsible`` têm tratamento próprio mais abaixo.
        for field, value in attrs.items():
            if field in ('status', 'responsible'):
                continue
            # Só é violação se o valor enviado de fato difere do atual (um PUT
            # reenvia campos inalterados, que não devem ser considerados edição).
            if getattr(self.instance, field) != value:
                raise serializers.ValidationError({
                    field: (
                        'Usuário comum só pode alterar o status da tarefa ou '
                        'atribuir/remover a si mesmo como responsável.'
                    )
                })

        # Responsável: o usuário comum só pode atribuir-se quando a tarefa não
        # tem responsável, ou remover-se quando é o responsável atual. Apura
        # também o estado resultante (``efetivo``) usado na checagem de status.
        atual = self.instance.responsible
        if 'responsible' in attrs:
            novo = attrs['responsible']
            if novo != atual:
                if novo == user:
                    # Atribuir-se: só é permitido quando não há responsável.
                    if atual is not None:
                        raise serializers.ValidationError({
                            'responsible': (
                                'Usuário comum só pode atribuir-se como '
                                'responsável quando a tarefa não possui '
                                'nenhum responsável.'
                            )
                        })
                elif novo is None:
                    # Remover o responsável: só é permitido se for a si mesmo.
                    if atual != user:
                        raise serializers.ValidationError({
                            'responsible': (
                                'Usuário comum só pode remover a si mesmo da '
                                'responsabilidade da tarefa.'
                            )
                        })
                else:
                    # Atribuir a um terceiro é sempre vedado ao usuário comum.
                    raise serializers.ValidationError({
                        'responsible': (
                            'Usuário comum só pode atribuir a si mesmo como '
                            'responsável.'
                        )
                    })
            efetivo = novo
        else:
            efetivo = atual

        # Status: só pode ser alterado se o usuário for o responsável pela tarefa
        # (considerando uma eventual atribuição de si mesmo na mesma requisição).
        if 'status' in attrs and attrs['status'] != self.instance.status:
            if efetivo != user:
                raise serializers.ValidationError({
                    'status': (
                        'Usuário comum só pode alterar o status de tarefas das '
                        'quais é responsável.'
                    )
                })

    def validate_description(self, value):
        """Normaliza ``None`` para string vazia no campo ``description``.

        Descrição:
            O campo aceita ``null`` na entrada (``allow_null=True``), mas o
            modelo usa ``TextField(blank=True)`` sem ``null=True``. Para evitar
            gravar ``None`` no banco, converte o valor nulo em string vazia.

        Objetivo:
            Permitir que o cliente envie ``description: null`` sem erro,
            preservando a convenção do Django de usar ``""`` como vazio.

        Parâmetros:
            self (TaskSerializer): A instância do serializer.
            value (str | None): O valor recebido para ``description``.

        Assertivas de entrada:
            - ``value`` é ``None`` ou uma string.

        Assertivas de saída:
            - O valor retornado é sempre uma string (``""`` quando a entrada
              era ``None``).

        Retornos:
            str: A descrição normalizada (string vazia no lugar de ``None``).
        """
        return value or ''

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
            'responsible',
        ]
        read_only_fields = ['id', 'created_at', 'closed_at', 'creator_name']
