# Backend — Quadro Kanban (Trabalho 2 de Programação para Web)

Este repositório contém **exclusivamente o backend** do projeto. O frontend
(HTML/CSS/TypeScript) fica em um repositório separado, conforme exige o
[enunciado](./enunciado.pdf). A visão geral do produto está em
[ORIGINAL-IDEA.md](./ORIGINAL-IDEA.md).

Este documento lista **tudo que será implementado neste repositório**.

---

## 1. Stack e Restrições

- **Framework:** Django + Django REST Framework (API REST pura, **sem HTML, CSS ou JavaScript**).
- **Banco de dados:** com as quatro operações básicas (CRUD) expostas via API.
- **Autenticação:** baseada em token (JWT ou Token do DRF) — o frontend consome a API.
- **Documentação:** Swagger/OpenAPI habilitado e navegável.
- **Publicação:** API publicada em um provedor de serviço Web (separado do site do frontend),
  opcionalmente containerizada com Docker.
- **CORS:** habilitado para permitir o consumo pelo frontend hospedado em outro domínio.

---

## 2. Modelos de Dados

### 2.1 Usuário
Estende/baseia-se no usuário do Django.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| Nome | String | Sim | Único no sistema |
| Senha | String (Hash) | Sim | Armazenada com hash |
| Permissão | Enum | Sim | `ADMINISTRADOR` ou `USUARIO` |

### 2.2 Tarefa

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| Nome | String (máx. 255) | Sim | Título da tarefa |
| Status | Enum | Sim | `A_FAZER`, `EM_PROGRESSO`, `PRONTO`, `ENTREGUE` |
| Descrição | Text | Não | Detalhes da tarefa |
| Responsáveis | M2M Usuário | Não | Um ou mais usuários responsáveis |
| Story Points | Number (0–100) | Não | Estimativa de esforço |
| Data de Criação | DateTime | Sim | Preenchida automaticamente |
| Data Limite | DateTime | Não | Prazo da tarefa |
| Data de Fechamento | DateTime | Não | Preenchida ao mudar para status concluído |
| Criador | FK Usuário | Sim | Usuário que criou a tarefa |

---

## 3. Endpoints da API

### 3.1 Autenticação e Gerência de Usuário
- `POST /auth/signup` — cadastro de nova conta (público).
- `POST /auth/login` — autenticação, retorna token (público).
- `POST /auth/logout` — encerra sessão/invalida token (autenticado).
- `POST /auth/password/change` — troca de senha do usuário logado (autenticado).
- `POST /auth/password/reset` — solicitação de recuperação de senha ("esqueci senha").
- `POST /auth/password/reset/confirm` — confirma redefinição de senha via token.
- `GET  /users/me` — dados do perfil do usuário autenticado.
- `PUT/PATCH /users/me` — edição de nome, senha e permissão (perfil).

### 3.2 Tarefas (CRUD) — **endpoints protegidos** (somente autenticado)
- `GET    /tasks` — lista todas as tarefas (Read).
- `GET    /tasks/:id` — detalha uma tarefa (Read).
- `POST   /tasks` — cria tarefa (Create — **apenas Administrador**).
- `PUT/PATCH /tasks/:id` — edita tarefa (Update — com regras de permissão, ver §4).
- `DELETE /tasks/:id` — remove tarefa (Delete — **apenas Administrador**).

### 3.3 Documentação
- `GET /swagger` (ou `/api/docs`) — interface Swagger UI.
- `GET /schema` — schema OpenAPI.

---

## 4. Regras de Permissão (aplicadas no backend)

| Ação | Administrador | Usuário |
|------|---------------|---------|
| **Create** (tarefa) | ✅ Tarefa completa | ❌ |
| **Read** | ✅ Todas as informações | ✅ Todas as informações |
| **Update** | ✅ Todos os campos | Apenas: adicionar/remover **a si mesmo** como responsável; alterar **status** se for responsável |
| **Delete** | ✅ | ❌ |
| **Editar Usuário** | ✅ | ✅ (próprio perfil) |

As regras serão implementadas via **permissions/serializers do DRF**, validadas no
servidor (não confiar no frontend).

---

## 5. Requisitos do Enunciado Atendidos por Este Repositório

- [ ] **CRUD** completo em banco de dados (modelo Tarefa). *(2,0 pts)*
- [ ] **Pelo menos um endpoint protegido** — todos os endpoints de `tasks/` exigem autenticação.
- [ ] **Usuários do mesmo tipo com visões diferentes** — Usuário só pode editar tarefas
      em que é responsável; o que cada usuário pode fazer varia conforme suas tarefas/permissão.
- [ ] **Swagger** documentado e consultável. *(1,5 pts)*
- [ ] **Gerência de usuário** — cadastro, login, edição de perfil, troca e recuperação de senha. *(2,0 pts)*
- [ ] **Publicação** da API em provedor Web (opcional Docker). *(1,0 pt)*
- [ ] **Comentários** no código. *(0,5 pt)*
- [ ] Repositório **separado** do frontend, com acesso público.
- [ ] **README** com título, integrantes, instruções de instalação/uso, link e relato
      do que funcionou / não funcionou.

---

## 6. Fora do Escopo deste Repositório

- Telas, navegação e qualquer HTML/CSS/JavaScript/TypeScript (responsabilidade do frontend).
- Renderização de páginas: este backend expõe **apenas a API REST**.
