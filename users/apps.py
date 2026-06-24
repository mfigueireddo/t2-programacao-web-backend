from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        """Conecta os sinais do app ao inicializar a aplicação.

        Importa :mod:`users.signals` para que os receptores de ``post_save`` e
        ``pre_delete`` (sincronização do nome do criador nas tarefas) sejam
        registrados quando o Django carregar os apps.
        """
        from . import signals  # noqa: F401  (import com efeito de registro)
