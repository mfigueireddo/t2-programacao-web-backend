"""
Serializers do domínio de Tarefas (Tasks).

Define a tradução entre instâncias do modelo :class:`tasks.models.Task` e a
representação JSON consumida/produzida pela API REST, além de validar os dados
de entrada antes da persistência.
"""

from rest_framework import serializers
from users.models import User
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
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
        read_only_fields = [
            'id',
            'created_at',
            'closed_at',
            'creator',
            'creator_name',
        ]

    def validate_description(self, value):
        return value or ''

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if self.instance is None:
            return attrs

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not getattr(user, 'is_authenticated', False):
            return attrs

        if user.role != User.Role.USUARIO:
            return attrs

        self._validate_usuario_update(attrs, user)

        return attrs

    def _validate_usuario_update(self, attrs, user):
        for field, value in attrs.items():
            if field in ('status', 'responsible'):
                continue

            if getattr(self.instance, field) != value:
                raise serializers.ValidationError({
                    field: (
                        'Usuário comum só pode alterar o status da tarefa '
                        'ou atribuir/remover a si mesmo como responsável.'
                    )
                })

        current_responsible = self.instance.responsible

        if 'responsible' in attrs:
            new_responsible = attrs['responsible']

            if new_responsible != current_responsible:
                if new_responsible == user:
                    if current_responsible is not None:
                        raise serializers.ValidationError({
                            'responsible': (
                                'Usuário comum só pode atribuir-se como responsável '
                                'quando a tarefa não possui responsável.'
                            )
                        })

                elif new_responsible is None:
                    if current_responsible != user:
                        raise serializers.ValidationError({
                            'responsible': (
                                'Usuário comum só pode remover a si mesmo da '
                                'responsabilidade da tarefa.'
                            )
                        })

                else:
                    raise serializers.ValidationError({
                        'responsible': (
                            'Usuário comum só pode atribuir a si mesmo como responsável.'
                        )
                    })

            effective_responsible = new_responsible

        else:
            effective_responsible = current_responsible

        if 'status' in attrs and attrs['status'] != self.instance.status:
            if effective_responsible != user:
                raise serializers.ValidationError({
                    'status': (
                        'Usuário comum só pode alterar o status de tarefas '
                        'das quais é responsável.'
                    )
                })