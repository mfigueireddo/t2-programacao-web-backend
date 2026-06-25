"""Modelos de dados do domínio de Tarefas (Tasks).

Este módulo define a entidade ``Task``, que representa um cartão do quadro
Kanban.
"""

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from users.models import User


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
        - ``creator`` referencia exatamente um :class:`users.models.User`
          existente na criação (obrigatório); após a criação é imutável e pode
          tornar-se ``None`` caso a conta do criador seja excluída.
        - ``creator_name`` reflete o nome do criador (cópia desnormalizada).
        - ``responsible``, quando informado, referencia exatamente um
          :class:`users.models.User` existente (ou ``None``, quando a tarefa
          não possui responsável).

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
    creator = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='created_tasks',
        verbose_name='Criador',
        help_text=(
            'Usuário que criou a tarefa. Definido na criação e imutável depois. '
            'Ao excluir a conta do criador, é anulado (SET_NULL), mas o nome '
            'permanece preservado em "creator_name".'
        ),
    )
    creator_name = models.CharField(
        max_length=170,
        blank=True,
        verbose_name='Nome do Criador',
        help_text=(
            'Nome do criador armazenado de forma desnormalizada (cópia). É '
            'preenchido na criação, atualizado quando o criador se renomeia e '
            'passa a "[DELETADO] <último nome>" quando a conta é excluída. '
            'Permite obter o nome do criador sem consultar a tabela de usuários.'
        ),
    )
    responsible = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        verbose_name='Responsável',
        help_text=(
            'Usuário responsável pela tarefa (no máximo um; pode não haver '
            'nenhum). Ao excluir a conta do responsável, é anulado (SET_NULL).'
        ),
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

    def save(self, *args, **kwargs):
        """Persiste a tarefa preenchendo a data de fechamento automaticamente.

        Descrição:
            Sobrescreve o ``save`` padrão para manter o campo ``closed_at``
            coerente com o ``status``. A data de fechamento nunca é definida
            diretamente pelo cliente: ela é gerida exclusivamente aqui, como
            efeito colateral da mudança de ``status``.

        Objetivo:
            Garantir que ``closed_at`` seja preenchido quando a tarefa entra no
            estágio terminal ``ENTREGUE`` e limpo caso a tarefa seja reaberta
            (mudança para qualquer outro status). Além disso, na criação, semeia
            ``creator_name`` com o nome do criador.

        Parâmetros:
            self (Task): A instância da tarefa a ser persistida.
            *args: Argumentos posicionais repassados a ``models.Model.save``.
            **kwargs: Argumentos nomeados repassados a ``models.Model.save``.

        Assertivas de entrada:
            - ``self.status`` pertence a :class:`Task.Status`.

        Assertivas de saída:
            - Se ``status == ENTREGUE`` e ``closed_at`` estava vazio, este passa
              a conter o instante atual.
            - Se ``status != ENTREGUE``, ``closed_at`` fica ``None`` (cobrindo a
              reabertura, ou seja, a saída do estágio ENTREGUE).
            - Um ``closed_at`` já preenchido em tarefa ``ENTREGUE`` é mantido
              (a operação é idempotente e não reescreve a data original).
            - Em uma criação com ``creator`` definido e ``creator_name`` vazio,
              ``creator_name`` passa a conter o nome do criador.

        Retornos:
            None: A instância é persistida no banco como efeito colateral.
        """
        if self.status == self.Status.ENTREGUE:
            # Preenche apenas na transição para ENTREGUE, preservando uma data
            # de fechamento já registrada (idempotência em salvamentos repetidos).
            if self.closed_at is None:
                self.closed_at = timezone.now()
        else:
            # Tarefa não concluída: garante que não exista data de fechamento,
            # cobrindo o caso de reabertura (saída do estágio ENTREGUE).
            self.closed_at = None

        # Na criação, copia o nome do criador para o campo desnormalizado. A
        # partir daí, a sincronização (renomeação/exclusão) é feita pelos sinais
        # do app ``users``; aqui apenas semeamos o valor inicial.
        if self._state.adding and self.creator_id and not self.creator_name:
            self.creator_name = self.creator.name

        super().save(*args, **kwargs)

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
