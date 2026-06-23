# Como rodar o projeto

Backend REST do Quadro Kanban (Trabalho 2 de Programação para Web), construído com **Django + Django REST Framework**.

## TL-DR
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Pré-requisitos

- **Python 3.13+** instalado e disponível no `PATH`.
- **pip** (já incluso no Python).

## 1. Criar e ativar o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

## 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 3. Aplicar as migrações do banco de dados

Cria o banco SQLite (`db.sqlite3`) e as tabelas:

```bash
python manage.py migrate
```

## 4. (Opcional) Criar um superusuário para o admin

```bash
python manage.py createsuperuser
```

## 5. Rodar o servidor de desenvolvimento

```bash
python manage.py runserver
```

A API ficará disponível em `http://127.0.0.1:8000/`
