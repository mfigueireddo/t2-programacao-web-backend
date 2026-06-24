"""Modelos de dados do domínio de Usuários (Users).

Este módulo define a entidade ``User``, que representa um usuário do quadro
Kanban. Trata-se de um modelo **independente** (não integrado ao sistema de
autenticação do Django) e propositalmente cru: nesta etapa ele apenas dá
suporte aos vínculos de criador e responsáveis de uma tarefa. A autenticação
(login, cadastro, hashing de senha, etc.) será incorporada posteriormente.
"""

from django.db import models


class User(models.Model):
    """Representa um usuário do quadro Kanban.

    Descrição:
        Entidade persistida em banco que identifica uma pessoa que cria tarefas
        e/ou é responsável por elas. É um modelo mínimo, a ser expandido quando
        a autenticação for adicionada ao projeto.

    Objetivo:
        Fornecer a identidade necessária para os vínculos de criador
        (:attr:`tasks.models.Task.creator`) e de responsáveis
        (:attr:`tasks.models.Task.responsibles`).

    Assertivas de entrada:
        - ``name`` é uma string não vazia, única no sistema, com no máximo 150
          caracteres.
        - ``role`` é um dos valores definidos em :class:`User.Role`.

    Assertivas de saída:
        - A instância possui ``id`` inteiro positivo e único.
        - Os demais campos refletem exatamente os valores fornecidos.
    """

    class Role(models.TextChoices):
        """Enumeração dos papéis (permissões) possíveis de um usuário.

        Descrição:
            Conjunto fechado de valores que o campo ``role`` pode assumir,
            associando o valor armazenado a um rótulo legível.

        Objetivo:
            Restringir o campo ``role`` a um domínio válido. As regras de
            permissão que dependem do papel serão aplicadas em etapa futura.

        Assertivas de entrada:
            - O valor atribuído ao campo ``role`` pertence a este conjunto.

        Assertivas de saída:
            - Os valores expostos são exatamente: ``ADMINISTRADOR`` e
              ``USUARIO``.

        Retornos:
            Não se aplica.
        """

        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        USUARIO = 'USUARIO', 'Usuário'

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nome',
        help_text='Nome do usuário (único no sistema).',
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USUARIO,
        verbose_name='Permissão',
        help_text='Papel do usuário: ADMINISTRADOR ou USUARIO.',
    )

    class Meta:
        """Metadados de configuração do modelo ``User``.

        Descrição:
            Define ordenação padrão e rótulos legíveis do modelo.

        Objetivo:
            Garantir uma listagem previsível (por nome) e nomes amigáveis no
            admin e na documentação.
        """

        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['name']

    def __str__(self):
        """Retorna a representação textual legível do usuário.

        Descrição:
            Fornece um rótulo curto e humano para a instância, usado pelo admin,
            logs e shell do Django.

        Objetivo:
            Facilitar a identificação de um usuário sem expor todos os campos.

        Parâmetros:
            self (User): A instância do usuário.

        Assertivas de entrada:
            - ``self.name`` está definido (string).

        Assertivas de saída:
            - O valor retornado é uma string não vazia contendo o nome.

        Retornos:
            str: O nome do usuário.
        """
        return self.name
