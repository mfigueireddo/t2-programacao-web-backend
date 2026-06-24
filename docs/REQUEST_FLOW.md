# Fluxo das Requisições

Documento complementar ao [OVERVIEW.md](./OVERVIEW.md). 
Enquanto o OVERVIEW descreve **o que é cada arquivo**, este documento descreve **o que acontece em cada requisição**, passo a passo, do recebimento do HTTP até a resposta.

Todas as requisições percorrem o mesmo caminho de camadas:

```
Requisição HTTP
    -> config/urls.py        (roteador raiz)
    -> tasks/urls.py         (roteador do app — escolhe a ação do ViewSet)
    -> tasks/views.py        (TaskViewSet — ação do ModelViewSet)
    -> tasks/serializers.py  (TaskSerializer — validação/serialização)  <->  tasks/models.py (Task)
    -> banco SQLite
    -> Resposta HTTP (JSON)
```

O que muda de uma requisição para outra é **qual ação** do `TaskViewSet` é executada e **quais etapas de validação/persistência** ela dispara.

---

## Onde mora cada responsabilidade

Um mapa de "quem faz o quê" — útil para localizar em que etapa cada coisa acontece:

| Etapa | Arquivo | Responsabilidade |
|-------|---------|------------------|
| Roteamento raiz | [config/urls.py](../config/urls.py) | Casa o prefixo `tasks/` e delega para o app; também expõe `admin/`, `schema/`, `swagger/`. |
| Roteamento do app | [tasks/urls.py](../tasks/urls.py) | Um `DefaultRouter` gera as rotas REST (`/tasks/` e `/tasks/<id>/`) e associa cada método HTTP a uma **ação** do `TaskViewSet` (`list`, `create`, `retrieve`, `update`, `partial_update`, `destroy`). |
| Controle / orquestração | [tasks/views.py](../tasks/views.py) | `TaskViewSet` (um `ModelViewSet`): recebe a `request`, busca no `queryset`, chama o serializer e monta a `Response`. Nenhum método é escrito à mão. |
| Validação e (de)serialização | [tasks/serializers.py](../tasks/serializers.py) | Converte JSON ↔ objeto, aplica `read_only_fields` e impõe que `creator` seja obrigatório na criação e imutável depois. **É aqui que mora a maior parte das validações.** |
| Regras de domínio e schema | [tasks/models.py](../tasks/models.py) e [users/models.py](../users/models.py) | Definem os campos, tipos, `choices` de `status`/`role`, o teto de `story_points` (`MaxValueValidator`), e a lógica de `Task.save()` (preenche `created_at`; gerencia `closed_at` conforme o status; semeia `creator_name`). |
| Sincronização de criador | [users/signals.py](../users/signals.py) | Sinais `post_save`/`pre_delete` do `User` mantêm `Task.creator_name` coerente (renomeação e exclusão da conta → `[DELETADO] <nome>`). |
| Persistência | SQLite | Armazena/recupera os registros. |

### As três camadas onde a validação ocorre

A validação não acontece num único lugar. Em ordem de execução:

1. **Roteamento (URL)** — antes de qualquer view. 

As rotas de item geradas pelo `DefaultRouter` capturam o `pk` com o padrão `[^/.]+`. A view (`get_object`) busca a tarefa por esse `pk`; se nenhuma corresponder — inclusive quando o valor não é um inteiro válido —, o DRF responde `404` sem chegar à lógica de domínio.

2. **Serializer (campo a campo)** — o grosso da validação. 

Ao chamar `serializer.is_valid()`, o DRF aplica:
- Validações implícitas derivadas do modelo (tipo, `max_length=255` de `name`, pertencimento de `status` ao enum `Status`, `story_points` entre 0 e 100 — `PositiveSmallIntegerField` + `MaxValueValidator`, obrigatoriedade de `name`, existência do usuário em `creator`/`responsibles`);
- `read_only_fields = ['id', 'created_at', 'closed_at', 'creator_name']` — esses campos são **ignorados** se vierem no corpo;
- `creator` é obrigatório na criação e, nas atualizações, tornado somente leitura (imutável).

3. **Modelo / banco** — última linha de defesa. 

Restrições de coluna e a lógica de `Task.save()` (preenche `created_at` via `auto_now_add`; ajusta `closed_at` conforme o status; semeia `creator_name`) são aplicadas na persistência.

> Falhas na etapa 1 viram `404`; falhas na etapa 2 viram `400 Bad Request` com o detalhe dos erros por campo, **antes** de qualquer escrita no banco.