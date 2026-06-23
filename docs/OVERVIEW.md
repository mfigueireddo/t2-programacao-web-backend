# Visão Geral da Arquitetura

Roteiro de leitura para entender como o projeto está arquitetado e como o fluxo do programa funciona.

## Visão geral da arquitetura

É um backend **Django + Django REST Framework** que expõe um CRUD de Tarefas (cartões de um quadro Kanban). 
A estrutura segue o padrão clássico Django, dividida em duas partes:

- **`config/`** — o "projeto" Django: configuração global, roteamento raiz e
  pontos de entrada do servidor (WSGI/ASGI).
- **`tasks/`** — o "app" Django: todo o domínio de Tarefas (modelo, validação,
  lógica de API, rotas).

O fluxo de uma requisição é: `config/urls.py` → `tasks/urls.py` → `tasks/views.py` → `tasks/serializers.py` ↔ `tasks/models.py` → banco SQLite.

---

## Roteiro de leitura

Sugiro ler **na ordem de inicialização e depois na ordem do fluxo da requisição**:

### 1. [BUILD.md](./BUILD.md) e [USAGE.md](./USAGE.md)

Já dão o contexto de negócio: o que a API faz, quais endpoints existem e quais campos a Tarefa tem.

**Atente-se:** a tabela de endpoints em USAGE.md (seção 2) segue o padrão REST do DRF — o recurso é identificado pela URL (`/tasks/`, `/tasks/<id>/`) e a operação vem do verbo HTTP. As rotas são geradas por um `DefaultRouter` em `tasks/urls.py`.

### 2. [manage.py](../manage.py)

Ponto de entrada de todos os comandos administrativos (`runserver`, `migrate`, etc.).

**Atente-se:** a única linha que importa é a que aponta `DJANGO_SETTINGS_MODULE` para `config.settings` — é o que amarra o projeto às configurações.

### 3. [config/settings.py](../config/settings.py)

O "painel de controle". Define apps instalados, middlewares, banco de dados, fuso horário e as configurações de DRF/Swagger/CORS.

**Atente-se:** os apps de terceiros (`rest_framework`, `drf_spectacular`, `corsheaders`) e o app local `tasks`; o banco é SQLite local; `CORS_ALLOW_ALL_ORIGINS = True` e `DEBUG = True` são para desenvolvimento apenas. `USE_TZ` ativo explica por que as datas têm fuso.

### 4. [config/urls.py](../config/urls.py)

O roteador raiz — a primeira coisa que recebe qualquer requisição. Distribui para `admin/`, `tasks/`, e a documentação (`schema/`, `swagger/`).

**Atente-se:** a linha `include('tasks.urls')` é o "pulo" para as rotas do app; é o ponto onde o fluxo entra no domínio de Tarefas.

### 5. [tasks/models.py](../tasks/models.py)

O coração do domínio: define a entidade `Task` e seus campos, incluindo o enum de `status` (A_FAZER, EM_PROGRESSO, PRONTO, ENTREGUE).

**Atente-se:** quais campos são preenchidos automaticamente (`created_at`) e quais são opcionais (`due_date`, `closed_at`, `story_points`); a ordenação padrão (mais recentes primeiro). É a base para entender os outros arquivos do app.

### 6. [tasks/serializers.py](../tasks/serializers.py)

A camada de tradução/validação entre JSON e o modelo. Define quais camposentram/saem da  API e regras de validação.

**Atente-se:** `read_only_fields` (`id`, `created_at` não são aceitos como entrada) e a validação custom de `story_points` (teto de 100).

### 7. [tasks/views.py](../tasks/views.py)

A lógica da API. É enxuto de propósito: usa um `ModelViewSet`, que já entrega todo o CRUD a partir do queryset + serializer.

**Atente-se:** não há método escrito manualmente — todo o comportamento vem das classes do DRF. Por isso models e serializers são onde a lógica real mora.

### 8. [tasks/urls.py](../tasks/urls.py)

Fecha o ciclo: mapeia cada rota/método HTTP para uma ação específica do `TaskViewSet`.

**Atente-se:** aqui está a tal decisão "não-REST-pura" — em vez de um `DefaultRouter` automático, cada ação do ViewSet é ligada manualmente a uma URL com verbo (`create`, `update/<id>`, `delete/<id>`). É o arquivo que o TODO marca para revisão.

### 9. Complementares (leitura rápida)

- [tasks/admin.py](../tasks/admin.py) — configura a interface administrativa do Django para Tarefas (colunas, filtros, busca). Caminho paralelo à API.
- [tasks/migrations/0001_initial.py](../tasks/migrations/0001_initial.py) — a tradução do modelo para o esquema do banco; útil para confirmar o que foi efetivamente criado.
- [config/wsgi.py](../config/wsgi.py) / [config/asgi.py](../config/asgi.py) — pontos de entrada do servidor em produção; pode ignorar no início.

---

## Resumo do fluxo

Uma requisição entra por `config/urls.py`, é encaminhada para `tasks/urls.py`, que escolhe a ação do `TaskViewSet` (`views.py`); a view usa o `TaskSerializer` (`serializers.py`) para validar/converter dados, que por sua vez espelha o modelo `Task` (`models.py`), persistido no SQLite. 
Os pontos onde mora a lógica de verdade são **models** e **serializers**; views e urls são "cola" do DRF.
