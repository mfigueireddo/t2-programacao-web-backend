"""Configuração do site administrativo do Django para o domínio de Tarefas.

Registra o modelo :class:`tasks.models.Task` no admin, permitindo inspecionar e
manipular tarefas pela interface administrativa durante o desenvolvimento.
"""

from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configura a exibição do modelo ``Task`` no admin do Django.

    Descrição:
        Define colunas, filtros e busca para a listagem de tarefas na interface
        administrativa.

    Objetivo:
        Facilitar a visualização e a manutenção manual de tarefas durante o
        desenvolvimento, sem necessidade de usar a API diretamente.

    Parâmetros:
        Não se aplica (classe de configuração consumida pelo admin do Django).

    Assertivas de entrada:
        - O modelo ``Task`` está registrado e migrado no banco.

    Assertivas de saída:
        - A listagem do admin exibe as colunas declaradas em ``list_display``.

    Retornos:
        Não se aplica.
    """

    list_display = (
        'id', 'name', 'status', 'creator', 'creator_name',
        'story_points', 'created_at', 'due_date',
    )
    list_filter = ('status',)
    search_fields = ('name', 'description', 'creator_name')
    ordering = ('-created_at',)
