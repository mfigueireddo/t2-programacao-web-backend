"""
Configuração do site administrativo do Django para o domínio de Usuários.

Registra o modelo :class:`users.models.User` no admin, permitindo inspecionar e
manipular usuários pela interface administrativa durante o desenvolvimento.
"""

from django.contrib import admin

from .models import AuthToken, PasswordResetToken, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__name', 'key')
    ordering = ('-created_at',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'used', 'created_at')
    list_filter = ('used',)
    search_fields = ('user__name', 'token')
    ordering = ('-created_at',)