"""Modelos de dados do domínio de Tarefas (Tasks).

Este módulo define a entidade ``Task``, que representa um cartão do quadro
Kanban.
"""

from django.core.validators import MaxValueValidator
from django.db import models


class Task(models.Model):
    """Representa uma tarefa (cartão) do quadro Kanban.

    Descrição:
        Entidade persistida em banco que armazena as informações de uma tarefa,
        como nome, status, descrição, estimativa de esforço e datas de controle.

    Objetivo:
        Servir como fonte única de verdade para as operações de CRUD expostas
        pela API REST do quadro Kanban.

    Assertivas de entrada:
        - ``name`` é uma string não vazia com no máximo 255 caracteres.
        - ``status`` é um dos valores definidos em :class:`Task.Status`.
        - ``story_points``, quando informado, é um inteiro entre 0 e 100.
        - ``due_date`` e ``closed_at``, quando informados, são ``datetime``
          válidos (com fuso horário, pois ``USE_TZ`` está ativo).

    Assertivas de saída:
        - A instância possui ``id`` inteiro positivo e único.
        - ``created_at`` está preenchido com o instante de criação.
        - Os demais campos refletem exatamente os valores fornecidos.
    """

    class Status(models.TextChoices):
        """Enumeração dos estágios possíveis de uma tarefa no quadro.

        Descrição:
            Conjunto fechado de valores que o campo ``status`` pode assumir.
            Cada item associa um valor armazenado no banco a um rótulo legível.

        Objetivo:
            Restringir o campo ``status`` a um domínio válido e fornecer rótulos
            amigáveis para exibição e documentação.

        Assertivas de entrada:
            - O valor atribuído ao campo ``status`` pertence a este conjunto.

        Assertivas de saída:
            - Os valores expostos são exatamente: ``A_FAZER``, ``EM_PROGRESSO``,
              ``PRONTO`` e ``ENTREGUE``.

        Retornos:
            Não se aplica.
        """

        A_FAZER = 'A_FAZER', 'A Fazer'
        EM_PROGRESSO = 'EM_PROGRESSO', 'Em Progresso'
        PRONTO = 'PRONTO', 'Pronto'
        ENTREGUE = 'ENTREGUE', 'Entregue'

    name = models.CharField(
        max_length=255,
        verbose_name='Nome',
        help_text='Título da tarefa (máx. 255 caracteres).',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.A_FAZER,
        verbose_name='Status',
        help_text='Estágio atual da tarefa no quadro Kanban.',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Detalhes da tarefa (opcional).',
    )
    story_points = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(100)],
        verbose_name='Story Points',
        help_text='Estimativa de esforço, de 0 a 100 (opcional).',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação',
        help_text='Preenchida automaticamente na criação da tarefa.',
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data Limite',
        help_text='Prazo da tarefa (opcional).',
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Fechamento',
        help_text='Preenchida quando a tarefa é concluída (opcional).',
    )

    class Meta:
        """Metadados de configuração do modelo ``Task``.

        Descrição:
            Define ordenação padrão e rótulos legíveis do modelo.

        Objetivo:
            Garantir uma listagem previsível (mais recentes primeiro) e nomes
            amigáveis no admin e na documentação.
        """

        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['-created_at']

    def __str__(self):
        """Retorna a representação textual legível da tarefa.

        Descrição:
            Fornece um rótulo curto e humano para a instância, usado pelo admin,
            logs e shell do Django.

        Objetivo:
            Facilitar a identificação de uma tarefa sem expor todos os campos.

        Parâmetros:
            self (Task): A instância da tarefa.

        Assertivas de entrada:
            - ``self.name`` está definido (string).

        Assertivas de saída:
            - O valor retornado é uma string não vazia contendo o nome da tarefa.

        Retornos:
            str: O nome (título) da tarefa.
        """
        return self.name
