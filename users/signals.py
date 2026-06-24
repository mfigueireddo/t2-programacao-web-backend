"""Sinais (signals) do domínio de Usuários.

Mantêm o nome do criador, armazenado de forma desnormalizada em
:attr:`tasks.models.Task.creator_name`, sincronizado com o usuário de origem.
São tratados dois eventos do ciclo de vida do :class:`users.models.User`:

- **Renomeação** (``post_save``): o nome salvo em cada tarefa criada pelo
  usuário é atualizado para o novo nome.
- **Exclusão da conta** (``pre_delete``): o nome salvo passa a seguir o formato
  ``[DELETADO] <último nome>``. Em seguida, o próprio Django anula a FK
  ``creator`` (``on_delete=SET_NULL``) e remove o usuário da relação
  ``responsibles`` (limpeza automática da tabela M2M).

Opta-se por sinais — e não apenas por sobrescrever ``save``/``delete`` no
modelo — porque ``pre_delete`` é disparado para cada objeto também em exclusões
em lote (por exemplo, a ação "remover selecionados" do admin), garantindo que a
regra de negócio valha independentemente de como a exclusão é realizada.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from tasks.models import Task

from .models import User


@receiver(post_save, sender=User)
def sync_creator_name_on_rename(sender, instance, created, **kwargs):
    """Propaga o nome atual do usuário para as tarefas que ele criou.

    Descrição:
        Após salvar um usuário, atualiza o campo desnormalizado
        ``creator_name`` de todas as tarefas das quais ele é criador, mantendo a
        cópia coerente com o nome corrente.

    Objetivo:
        Garantir que a renomeação de um usuário se reflita imediatamente no nome
        do criador exibido nas tarefas, sem consulta à tabela de usuários.

    Parâmetros:
        sender (type): A classe que emitiu o sinal (``User``).
        instance (User): A instância recém-salva.
        created (bool): ``True`` se a instância acabou de ser criada.
        **kwargs: Demais argumentos do sinal (ignorados).

    Assertivas de entrada:
        - ``instance.name`` está definido (string).

    Assertivas de saída:
        - Para criações (``created`` verdadeiro), nada é alterado (um usuário
          recém-criado ainda não é criador de nenhuma tarefa).
        - Caso contrário, toda tarefa com ``creator == instance`` passa a ter
          ``creator_name == instance.name``.

    Retornos:
        None.
    """
    if created:
        # Usuário recém-criado ainda não é criador de nenhuma tarefa.
        return

    # ``update`` em massa: uma única consulta SQL e não dispara ``Task.save``
    # (que apenas semeia o valor inicial na criação, irrelevante aqui).
    Task.objects.filter(creator=instance).update(creator_name=instance.name)


@receiver(pre_delete, sender=User)
def mark_creator_name_on_delete(sender, instance, **kwargs):
    """Marca o nome do criador como excluído antes de remover a conta.

    Descrição:
        Imediatamente antes da exclusão de um usuário, prefixa o nome salvo nas
        tarefas das quais ele é criador com ``[DELETADO] ``, preservando o
        último nome conhecido.

    Objetivo:
        Cumprir a regra de negócio de manter, na tarefa, o registro de quem a
        criou mesmo após a exclusão da conta. A anulação da FK ``creator`` e a
        remoção das relações de responsável são tratadas pelo próprio Django.

    Parâmetros:
        sender (type): A classe que emitiu o sinal (``User``).
        instance (User): A instância prestes a ser excluída.
        **kwargs: Demais argumentos do sinal (ignorados).

    Assertivas de entrada:
        - ``instance.name`` está definido (string) e ainda não foi excluído.

    Assertivas de saída:
        - Toda tarefa com ``creator == instance`` passa a ter
          ``creator_name == "[DELETADO] " + instance.name``.
    """
    Task.objects.filter(creator=instance).update(
        creator_name=f'[DELETADO] {instance.name}'
    )
