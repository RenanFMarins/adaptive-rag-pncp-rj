# RAG — Contratações Públicas do Estado do Rio de Janeiro

Projeto desenvolvido pelo **Time 03** para construção de uma solução de **Retrieval-Augmented Generation (RAG)** aplicada ao cenário de **Contratações Públicas do Estado do Rio de Janeiro**.

A aplicação utiliza **FastAPI** como framework backend, **Uvicorn** como servidor ASGI, **SQLite** como banco de dados local e **SQLAlchemy** para persistência e acesso aos dados.

O projeto também prevê uma arquitetura de recuperação híbrida utilizando busca semântica e lexical para construção do pipeline RAG.

---

## 1. Tecnologias

Tecnologias previstas/utilizadas no projeto:

- Python
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- SQLAlchemy
- SQLite
- FAISS
- BM25
- RRF
- Pytest
- LLM

---

## 2. Pré-requisitos

Antes de executar o projeto, verifique se possui o Python instalado.

```bash
python --version
```

No Windows também pode ser utilizado:

```bash
py --version
```

Recomenda-se utilizar **Python 3.12 ou superior**.

---

## 3. Clonar o projeto

Clone o repositório:

```bash
git clone https://github.com/grande-desafio-ia-rag-03/rag-grande-desafio-grupo03-contratacoes-publicas.git
```

Entre na pasta:

```bash
cd rag-grande-desafio-grupo03-contratacoes-publicas
```

Caso seja necessário trabalhar em uma branch específica:

```bash
git fetch --all
git switch nome-da-branch
```

---

# 4. Criar o ambiente virtual

O ambiente virtual **não é enviado para o GitHub**.

Cada desenvolvedor deverá criar sua própria `.venv` depois de clonar o projeto.

## Windows — PowerShell

```powershell
py -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Windows — Git Bash

```bash
py -m venv .venv
```

Ative:

```bash
source .venv/Scripts/activate
```

Quando estiver ativo, o terminal deverá apresentar algo semelhante a:

```text
(.venv)
```

---

# 5. Instalar as dependências

Com a `.venv` ativada, atualize o `pip`:

```bash
python -m pip install --upgrade pip
```

Se o projeto possuir `requirements.txt`:

```bash
pip install -r requirements.txt
```

Caso esteja realizando a configuração inicial manualmente, as dependências básicas são:

```bash
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings
```

As dependências específicas do pipeline RAG deverão ser adicionadas ao `requirements.txt` conforme os respectivos módulos forem implementados.

---

# 6. Configuração do `.env`

O projeto utiliza variáveis de ambiente para configurações que não devem ficar diretamente no código.

Crie o arquivo:

```text
.env
```

na raiz do projeto.

Exemplo:

```env
DATABASE_URL=sqlite:///./app.db
```

A estrutura ficará semelhante a:

```text
projeto/
├── .env
├── .gitignore
├── README.md
├── app/
└── ...
```

> O arquivo `.env` não deve ser enviado para o GitHub.

---

# 7. Banco de dados

O projeto utiliza inicialmente:

- **SQLite** — banco de dados;
- **SQLAlchemy** — ORM e acesso ao banco.

A configuração é definida no `.env`:

```env
DATABASE_URL=sqlite:///./app.db
```

Isso indica que o SQLite deverá utilizar o arquivo:

```text
app.db
```

na raiz do projeto.

## O que é o `app.db`?

Diferentemente do PostgreSQL, o SQLite não precisa de:

- servidor de banco;
- Docker;
- porta;
- usuário;
- senha;
- serviço executando em segundo plano.

O banco é armazenado em um arquivo local:

```text
app.db
```

Fluxo:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
SQLite
   ↓
app.db
```

---

# 8. Criação do banco

Não é necessário criar o arquivo `app.db` manualmente.

O SQLite criará o arquivo quando a aplicação estabelecer a conexão e executar a criação das tabelas.

A configuração principal está localizada em:

```text
app/core/database.py
```

Exemplo:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
```

---

# 9. Configuração da aplicação

As variáveis do `.env` são carregadas pelo:

```text
app/core/config.py
```

Exemplo:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
```

O fluxo de configuração fica:

```text
.env
  ↓
config.py
  ↓
database.py
  ↓
SQLAlchemy
  ↓
SQLite
```

---

# 10. Criando as tabelas

Os Models SQLAlchemy representam as tabelas do banco.

Exemplo:

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
```

Durante a fase inicial do projeto, as tabelas podem ser criadas com:

```python
Base.metadata.create_all(bind=engine)
```

Conforme o projeto evoluir, recomenda-se utilizar migrations para controlar alterações no esquema do banco.

---

# 11. Visualizar o SQLite no DBeaver

O arquivo `app.db` pode ser aberto diretamente no **DBeaver**.

Não é necessário deixar o Uvicorn rodando para consultar o banco.

No DBeaver:

1. Abra **Nova Conexão**.
2. Escolha **SQLite**.
3. No campo **Caminho**, clique em **Abrir**.
4. Selecione o arquivo `app.db`.
5. Clique em **Testar conexão**.
6. Clique em **Concluir**.

Depois será possível navegar por:

```text
app.db
└── Tabelas
    ├── documents
    ├── ...
```

Também é possível utilizar o SQL Editor:

```sql
SELECT * FROM documents;
```

---

# 12. Executar a aplicação

Com a `.venv` ativada:

```bash
python -m uvicorn app.main:app --reload
```

Também é possível utilizar:

```bash
uvicorn app.main:app --reload
```

A primeira opção é recomendada porque garante que o Uvicorn utilizado pertence ao ambiente Python atualmente ativo.

Quando iniciar corretamente, será exibido algo semelhante a:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

---

# 13. Acessar a API

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Documentação ReDoc:

```text
http://127.0.0.1:8000/redoc
```

O Swagger será utilizado durante o desenvolvimento para visualizar e testar os endpoints da aplicação.

---

# 14. Estrutura do projeto

A arquitetura segue uma organização modular.

```text
rag-grande-desafio-grupo03-contratacoes-publicas/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   └── modules/
│       │
│       ├── normative/
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── structured/
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── aggregated/
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── ingest/
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── retrieval/
│       │   ├── dense.py
│       │   ├── bm25.py
│       │   ├── rrf.py
│       │   ├── reranker.py
│       │   └── services.py
│       │
│       ├── query/
│       │   ├── analyzer.py
│       │   ├── router.py
│       │   └── guardrails.py
│       │
│       ├── rag/
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       └── evaluation/
│           ├── schemas.py
│           ├── services.py
│           └── routes.py
│
├── data/
│   ├── raw/
│   ├── inventory/
│   └── processed/
│
├── indexes/
│   ├── faiss/
│   └── bm25/
│
├── logs/
│
├── tests/
│
└── notes/
    ├── ARQUITETURA.md
    ├── PERSONAS.md
    └── corpus_manifest.yaml
```

---

# 15. Responsabilidade das principais pastas

## `app/`

Código principal da aplicação.

## `app/core/`

Configurações compartilhadas pelo sistema.

Contém:

```text
config.py
database.py
exceptions.py
logging.py
```

## `app/modules/`

Módulos de negócio da aplicação.

Cada módulo deve possuir responsabilidades bem definidas.

Quando aplicável, a estrutura padrão será:

```text
model.py
schemas.py
services.py
routes.py
```

### `model.py`

Models SQLAlchemy e representação das tabelas.

### `schemas.py`

Schemas Pydantic para entrada e saída de dados.

### `services.py`

Regras de negócio.

### `routes.py`

Endpoints FastAPI.

---

# 16. Dados e índices

A pasta:

```text
data/
```

é utilizada para organização do corpus.

Exemplo:

```text
data/
├── raw/
├── inventory/
└── processed/
```

Os índices de recuperação serão armazenados separadamente:

```text
indexes/
├── faiss/
└── bm25/
```

O objetivo é manter responsabilidades diferentes:

```text
SQLite
   ↓
dados da aplicação e metadados

FAISS
   ↓
índice vetorial / embeddings

BM25
   ↓
índice lexical
```

---

# 17. Pipeline RAG planejado

A arquitetura prevê o seguinte fluxo:

```text
Pergunta do usuário
        ↓
query_received
        ↓
query_normalization
        ↓
query_analysis
        ↓
scope_validation
        ↓
adaptive_routing
        ↓
metadata_filtering
        ↓
┌──────────────────────────┐
│                          │
↓                          ↓
dense_retrieval       bm25_retrieval
│                          │
└────────────┬─────────────┘
             ↓
         rrf_fusion
             ↓
          reranking
             ↓
     evidence_selection
             ↓
       prompt_building
             ↓
       llm_generation
             ↓
    response_validation
             ↓
      output_guardrails
             ↓
       response_final
```

Os nomes dos estágios deverão ser utilizados também no campo `stage` dos logs da aplicação.

---

# 18. Bases do projeto

O projeto foi dividido inicialmente em três bases principais.

## Base Normativa

Responsáveis:

- Ana Karina
- Ester Neves

Responsável pelos documentos jurídicos e normativos.

---

## Base Estruturada

Responsáveis:

- Alisson Lima de Souza
- Luciano Costa

Responsável por dados estruturados relacionados às contratações públicas.

---

## Base Agregada

Responsáveis:

- Felipe Antunes
- Renan Freitas

Responsável por indicadores, estatísticas e informações consolidadas.

---

# 19. Documentação da sprint

| Documento | Responsável |
|---|---|
| `ARQUITETURA.md` | Alisson Lima de Souza |
| `PERSONAS.md` | Luciano Costa |
| `corpus_manifest.yaml` | Felipe Antunes |

---

# 20. Coordenador

**Luiz Felipe Antunes**

O coordenador acompanha as atividades, organiza as tarefas e auxilia na integração das diferentes partes do projeto, além de participar tecnicamente do desenvolvimento.

---

# 21. `.gitignore`

Arquivos locais não devem ser enviados para o GitHub.

O `.gitignore` deve possuir pelo menos:

```gitignore
# Ambiente virtual
.venv/
venv/

# Variáveis de ambiente
.env

# Banco SQLite local
app.db
*.db

# Python
__pycache__/
*.py[cod]

# Pytest
.pytest_cache/

# IDE
.vscode/
.idea/

# Logs
*.log
```

> A `.venv` nunca deve ser versionada. Cada integrante cria seu próprio ambiente virtual depois de clonar o projeto.

---

# 22. Fluxo rápido para novos desenvolvedores

Depois de clonar o projeto:

```bash
git clone https://github.com/grande-desafio-ia-rag-03/rag-grande-desafio-grupo03-contratacoes-publicas.git

cd rag-grande-desafio-grupo03-contratacoes-publicas
```

Criar ambiente:

```bash
py -m venv .venv
```

Ativar no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Criar `.env`:

```env
DATABASE_URL=sqlite:///./app.db
```

Executar:

```bash
python -m uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

---

# 23. Equipe

**Time 03 — Contratações Públicas do Estado do Rio de Janeiro**

- Luiz Felipe Antunes
- Ana Karina
- Luciano Oliveira
- Marcio da Costa
- Ester da Silva
- Alisson Lima
- Renan Freitas

**Gerente / Coordenador:** Luiz Felipe Antunes