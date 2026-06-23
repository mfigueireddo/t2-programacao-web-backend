"""Roteamento de URLs do domínio de Tarefas (Tasks).

Mapeia os caminhos do app (já montados sob o prefixo ``tasks/`` pela URLconf
raiz) para as ações do :class:`tasks.views.TaskViewSet`. O esquema segue o
padrão REST do Django REST Framework: o recurso é identificado apenas pela URL e
a operação é definida pelo verbo HTTP (sem verbos no caminho).

Rotas expostas (geradas pelo ``DefaultRouter``):
    - ``GET    tasks/``         -> lista todas as tarefas.
    - ``POST   tasks/``         -> cria uma tarefa.
    - ``GET    tasks/<id>/``    -> detalha uma tarefa.
    - ``PUT    tasks/<id>/``    -> atualização total de uma tarefa.
    - ``PATCH  tasks/<id>/``    -> atualização parcial de uma tarefa.
    - ``DELETE tasks/<id>/``    -> remove uma tarefa.
"""

from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

# O ``DefaultRouter`` registra automaticamente as rotas de coleção (``tasks/``)
# e de item (``tasks/<id>/``), associando cada verbo HTTP à ação correspondente
# do ``ModelViewSet``. Usa-se prefixo vazio porque o ``tasks/`` já é aplicado
# pela URLconf raiz ao incluir este módulo.
router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')

urlpatterns = router.urls
