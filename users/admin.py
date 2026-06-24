"""Configuração do site administrativo do Django para o domínio de Usuários.

Registra o modelo :class:`users.models.User` no admin, permitindo inspecionar e
manipular usuários pela interface administrativa durante o desenvolvimento.
"""

from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configura a exibição do modelo ``User`` no admin do Django.

    Descrição:
        Define colunas, filtros e busca para a listagem de usuários na interface
        administrativa.

    Objetivo:
        Facilitar a criação e a manutenção manual de usuários durante o
        desenvolvimento.

    Assertivas de entrada:
        - O modelo ``User`` está registrado e migrado no banco.

    Assertivas de saída:
        - A listagem do admin exibe as colunas declaradas em ``list_display``.
    """

    list_display = ('id', 'name', 'role')
    list_filter = ('role',)
    search_fields = ('name',)
    ordering = ('name',)
