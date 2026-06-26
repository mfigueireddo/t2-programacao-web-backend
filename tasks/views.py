"""Views (camada de API) do domínio de Tarefas (Tasks).

Expõe o CRUD do modelo :class:`tasks.models.Task` por meio de um ``ViewSet`` do
Django REST Framework.
"""

"""Views do domínio de Tarefas."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import Task
from .permissions import TaskPermission
from .serializers import TaskSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Lista todas as tarefas',
        description='Retorna tarefas para usuários autenticados.',
    ),
    create=extend_schema(
        summary='Cria uma tarefa',
        description='Cria tarefa. Apenas ADMINISTRADOR pode executar.',
    ),
    retrieve=extend_schema(summary='Detalha uma tarefa'),
    update=extend_schema(summary='Atualiza uma tarefa'),
    partial_update=extend_schema(summary='Atualiza uma tarefa parcialmente'),
    destroy=extend_schema(summary='Remove uma tarefa'),
)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)