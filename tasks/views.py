"""Views (camada de API) do domínio de Tarefas (Tasks).

Expõe o CRUD do modelo :class:`tasks.models.Task` por meio de um ``ViewSet`` do
Django REST Framework.
"""

from rest_framework import viewsets

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """Conjunto de endpoints REST para o CRUD de tarefas.

    Descrição:
        Reúne, em uma única classe, as operações de criar, listar, detalhar,
        atualizar (total/parcial) e remover tarefas, seguindo as convenções de
        rotas de um ``ModelViewSet`` do DRF.

    Objetivo:
        Disponibilizar os endpoints ``tasks/`` exigidos pela especificação:
            - ``GET    /tasks/``        — lista todas as tarefas.
            - ``POST   /tasks/``        — cria uma tarefa (Create).
            - ``GET    /tasks/{id}/``   — detalha uma tarefa (Read).
            - ``PUT    /tasks/{id}/``   — atualização total (Update).
            - ``PATCH  /tasks/{id}/``   — atualização parcial (Update).
            - ``DELETE /tasks/{id}/``   — remove uma tarefa (Delete).

    Parâmetros:
        Não se aplica diretamente; o roteamento e a injeção de ``request`` são
        responsabilidade do DRF/Router.

    Assertivas de entrada:
        - Para criação/atualização, o corpo da requisição é um JSON válido
          aderente ao :class:`TaskSerializer`.
        - Para detalhe/atualização/remoção, ``{id}`` referencia uma tarefa
          existente; caso contrário, responde ``404 Not Found``.

    Assertivas de saída:
        - Operações bem-sucedidas retornam o código HTTP adequado
          (200/201/204) e, quando aplicável, a representação da tarefa.
        - Dados inválidos resultam em ``400 Bad Request`` com os erros de
          validação.

    Retornos:
        rest_framework.response.Response: Resposta HTTP correspondente à
        operação solicitada (gerada pelos métodos herdados do ``ModelViewSet``).
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
