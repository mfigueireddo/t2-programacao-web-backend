# Guia de Uso

Este documento mostra como **rodar o sistema** no estado atual e como **explorar os endpoints** disponíveis. 

Para o passo a passo de instalação do ambiente, veja o [BUILD.md](./BUILD.md).

> Estado atual: a API expõe apenas o **CRUD de Tarefas**. 
> Ainda não há autenticação, usuários ou permissões — todas as operações estão liberadas.

---

## 1. Formas de explorar os endpoints

Há três maneiras práticas de testar a API:

### 1.1 Swagger UI

Interface visual onde é possível ler a documentação e **executar** cada requisição direto do navegador.

- Abra: **http://127.0.0.1:8000/swagger/**
- Clique em um endpoint → **"Try it out"** → preencha o corpo → **"Execute"**.

O schema OpenAPI bruto (YAML) fica em **http://127.0.0.1:8000/schema/**.

### 1.2 Interface navegável do DRF

O Django REST Framework também serve páginas HTML navegáveis para cada rota.
Basta abrir as URLs no navegador, por exemplo:

- **http://127.0.0.1:8000/tasks/** — lista as tarefas e permite criar via formulário.

### 1.3 Linha de comando (`curl`)

Útil para automação e testes rápidos (exemplos na seção 3).

---

## 2. Referência dos endpoints

Todas as rotas estão sob o prefixo `tasks/`.

| Operação | Método | Rota | Descrição |
|----------|--------|------|-----------|
| Listar todas | `GET` | `/tasks/` | Retorna todas as tarefas |
| Criar | `POST` | `/tasks/create` | Cria uma nova tarefa |
| Detalhar | `GET` | `/tasks/<id>` | Retorna uma tarefa específica |
| Atualizar (total) | `PUT` | `/tasks/update/<id>` | Substitui todos os campos editáveis |
| Atualizar (parcial) | `PATCH` | `/tasks/update/<id>` | Atualiza apenas os campos enviados |
| Remover | `DELETE` | `/tasks/delete/<id>` | Exclui uma tarefa |

### Campos da Tarefa

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-------------|-------------|
| `id` | inteiro | — | Somente leitura (gerado automaticamente) |
| `name` | string | **Sim** | Máx. 255 caracteres |
| `status` | enum | Não | `A_FAZER` (padrão), `EM_PROGRESSO`, `PRONTO`, `ENTREGUE` |
| `description` | string | Não | Texto livre |
| `story_points` | inteiro | Não | Entre 0 e 100 |
| `created_at` | datetime | — | Somente leitura (preenchido na criação) |
| `due_date` | datetime | Não | Formato ISO 8601 (ex.: `2026-07-01T12:00:00Z`) |
| `closed_at` | datetime | Não | Formato ISO 8601 |

---

## 3. Exemplos com `curl`

> No Windows, prefira o **PowerShell** ou o **Git Bash**. 
Os exemplos abaixo usam a sintaxe do Bash.

### 3.1 Criar uma tarefa (`POST /tasks/create`)

```bash
curl -X POST http://127.0.0.1:8000/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Implementar autenticação",
        "status": "A_FAZER",
        "description": "Login e cadastro de usuários",
        "story_points": 8,
        "due_date": "2026-07-01T12:00:00Z"
      }'
```

Resposta (`201 Created`):

```json
{
  "id": 1,
  "name": "Implementar autenticação",
  "status": "A_FAZER",
  "description": "Login e cadastro de usuários",
  "story_points": 8,
  "created_at": "2026-06-23T13:00:00-03:00",
  "due_date": "2026-07-01T09:00:00-03:00",
  "closed_at": null
}
```

### 3.2 Listar todas as tarefas (`GET /tasks/`)

```bash
curl http://127.0.0.1:8000/tasks/
```

### 3.3 Detalhar uma tarefa (`GET /tasks/<id>`)

```bash
curl http://127.0.0.1:8000/tasks/1
```

### 3.4 Atualização parcial (`PATCH /tasks/update/<id>`)

Altera apenas o status:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/update/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "EM_PROGRESSO"}'
```

### 3.5 Atualização total (`PUT /tasks/update/<id>`)

Reenvia todos os campos editáveis:

```bash
curl -X PUT http://127.0.0.1:8000/tasks/update/1 \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Implementar autenticação JWT",
        "status": "PRONTO",
        "description": "Concluído",
        "story_points": 8
      }'
```

### 3.6 Remover uma tarefa (`DELETE /tasks/delete/<id>`)

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/delete/1
```

Resposta: `204 No Content` (sem corpo).

---

## 4. Códigos de resposta esperados

| Código | Significado |
|--------|-------------|
| `200 OK` | Leitura/atualização bem-sucedida |
| `201 Created` | Tarefa criada com sucesso |
| `204 No Content` | Tarefa removida com sucesso |
| `400 Bad Request` | Dados inválidos (ex.: `story_points` fora de 0–100) |
| `404 Not Found` | Tarefa com o `id` informado não existe |

---

## 5. Administração (opcional)

Se um superusuário foi criado (`python manage.py createsuperuser`), é possível
gerenciar as tarefas pela interface administrativa:

- **http://127.0.0.1:8000/admin/**