"""
Modelos de dados do domínio de Usuários (Users).

Este módulo define a entidade ``User``, que representa um usuário do quadro
Kanban, junto com os modelos de apoio à autenticação própria do projeto:

* ``User`` — usuário do quadro, com nome, papel (ADMINISTRADOR ou USUARIO) e
  senha armazenada como hash. É um modelo **independente** do sistema de
  autenticação do Django, mas implementa os métodos necessários (``set_password``,
  ``check_password``, ``is_authenticated``) para suportar login e autorização
  por papel.
* ``AuthToken`` — token emitido no login e enviado em cada requisição da API
  (cabeçalho ``Authorization: Bearer <token>``) para identificar o usuário.
* ``PasswordResetToken`` — token de uso único e com expiração, usado no fluxo
  simplificado de recuperação de senha.
"""

import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class User(models.Model):
    """Usuário do quadro Kanban."""

    class Role(models.TextChoices):
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        USUARIO = 'USUARIO', 'Usuário'

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nome',
        help_text='Nome do usuário (único no sistema).',
    )

    password = models.CharField(
        max_length=128,
        verbose_name='Senha',
        help_text='Senha armazenada em formato de hash.',
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USUARIO,
        verbose_name='Permissão',
        help_text='Papel do usuário: ADMINISTRADOR ou USUARIO.',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação',
    )

    @property
    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_', 'argon2$', 'bcrypt')):
            self.set_password(self.password)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['name']

    def __str__(self):
        return self.name


class AuthToken(models.Model):
    """Token simples usado para autenticar requisições da API."""

    key = models.CharField(max_length=128, unique=True, db_index=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auth_tokens',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(
            user=user,
            key=secrets.token_urlsafe(48),
        )

    def __str__(self):
        return f'Token de {self.user.name}'


class PasswordResetToken(models.Model):
    """Token usado no fluxo simplificado de recuperação de senha."""

    token = models.CharField(max_length=128, unique=True, db_index=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
        )

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=1)

    def __str__(self):
        return f'Recuperação de senha de {self.user.name}'