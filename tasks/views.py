"""
Views (camada de API) do domínio de Tarefas (Tasks).

Expõe o CRUD do modelo :class:`tasks.models.Task` por meio de um ``ViewSet`` do
Django REST Framework.
"""

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import viewsets
from .models import Task
from .permissions import TaskPermission
from .serializers import TaskSerializer

# Exemplo de corpo válido para criação. ``creator``, ``creator_name``,
# ``created_at`` e ``closed_at`` são somente-leitura (preenchidos pelo backend) e
# por isso não aparecem aqui. ``responsible`` aceita o id de um usuário existente
# ou ``null`` (tarefa sem responsável); o valor ``0`` gerado por padrão pelo
# Swagger não corresponde a nenhum usuário e causa erro de validação.
TASK_CREATE_EXAMPLE = OpenApiExample(
    'Tarefa nova',
    summary='Criação de uma tarefa',
    description=(
        'Apenas "name" é obrigatório. "responsible" deve ser o id de um usuário '
        'existente ou null. Datas usam o formato ISO 8601 com fuso.'
    ),
    value={
        'name': 'Implementar tela de login',
        'status': 'A_FAZER',
        'description': 'Criar formulário e integrar com o endpoint de autenticação.',
        'story_points': 5,
        'due_date': '2026-07-15T18:00:00-03:00',
        'responsible': None,
    },
    request_only=True,
)

# Exemplo para atualização parcial (PATCH): normalmente só se altera o status ou
# o responsável. Usuários comuns só podem mexer nesses dois campos.
TASK_PATCH_EXAMPLE = OpenApiExample(
    'Mover tarefa e atribuir responsável',
    summary='Atualização parcial',
    description='Envie apenas os campos que deseja alterar.',
    value={
        'status': 'EM_PROGRESSO',
        'responsible': 2,
    },
    request_only=True,
)


@extend_schema_view(
    list=extend_schema(
        summary='Lista todas as tarefas',
        description='Retorna todas as tarefas. Disponível para qualquer usuário autenticado.',
    ),
    create=extend_schema(
        summary='Cria uma tarefa',
        description=(
            'Cria uma tarefa. Apenas usuários com papel ADMINISTRADOR podem executar. '
            'O criador é definido automaticamente a partir do usuário autenticado. '
            'O campo "responsible" deve ser o id de um usuário existente ou null — '
            'o valor 0 sugerido por padrão não é válido.'
        ),
        examples=[TASK_CREATE_EXAMPLE],
    ),
    retrieve=extend_schema(
        summary='Detalha uma tarefa',
        description='Retorna os dados de uma tarefa específica pelo seu id.',
    ),
    update=extend_schema(
        summary='Atualiza uma tarefa',
        description=(
            'Substitui todos os campos editáveis da tarefa. Administradores alteram '
            'qualquer campo; usuários comuns só podem alterar o status ou atribuir/'
            'remover a si mesmos como responsável. "responsible" é um id de usuário ou null.'
        ),
        examples=[TASK_CREATE_EXAMPLE],
    ),
    partial_update=extend_schema(
        summary='Atualiza uma tarefa parcialmente',
        description=(
            'Atualiza apenas os campos enviados. Usuários comuns só podem alterar o '
            'status ou atribuir/remover a si mesmos como responsável.'
        ),
        examples=[TASK_PATCH_EXAMPLE],
    ),
    destroy=extend_schema(
        summary='Remove uma tarefa',
        description='Exclui permanentemente a tarefa indicada pelo id.',
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)