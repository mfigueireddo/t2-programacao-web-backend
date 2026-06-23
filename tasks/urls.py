"""Roteamento de URLs do domínio de Tarefas (Tasks).

Mapeia os caminhos sob o prefixo ``tasks/`` para as ações do
:class:`tasks.views.TaskViewSet`. O esquema de URLs segue o formato solicitado
para o projeto (com verbos explícitos no caminho) em vez do padrão puramente
REST de um ``DefaultRouter``.

Rotas expostas:
    - ``GET    tasks/``              -> lista todas as tarefas.
    - ``POST   tasks/create``        -> cria uma tarefa.
    - ``GET    tasks/<id>``          -> detalha uma tarefa.
    - ``PUT    tasks/update/<id>``   -> atualização total de uma tarefa.
    - ``PATCH  tasks/update/<id>``   -> atualização parcial de uma tarefa.
    - ``DELETE tasks/delete/<id>``   -> remove uma tarefa.
"""

from django.urls import path

from .views import TaskViewSet

# Mapeamento explícito dos métodos HTTP para as ações do ViewSet.
# Cada chamada a ``TaskViewSet.as_view`` cria uma view que despacha o método
# HTTP recebido para a ação correspondente do ``ModelViewSet``.

#: View de listagem: responde a ``GET`` em ``tasks/``.
task_list = TaskViewSet.as_view({'get': 'list'})

#: View de criação: responde a ``POST`` em ``tasks/create``.
task_create = TaskViewSet.as_view({'post': 'create'})

#: View de detalhe: responde a ``GET`` em ``tasks/<id>``.
task_detail = TaskViewSet.as_view({'get': 'retrieve'})

#: View de atualização: responde a ``PUT``/``PATCH`` em ``tasks/update/<id>``.
task_update = TaskViewSet.as_view({'put': 'update', 'patch': 'partial_update'})
    
#: View de remoção: responde a ``DELETE`` em ``tasks/delete/<id>``.
task_delete = TaskViewSet.as_view({'delete': 'destroy'})

urlpatterns = [
    path('', task_list, name='task-list'),
    path('create', task_create, name='task-create'),
    path('<int:pk>', task_detail, name='task-detail'),
    path('update/<int:pk>', task_update, name='task-update'),
    path('delete/<int:pk>', task_delete, name='task-delete'),
]
