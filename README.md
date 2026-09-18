# RAG --- Contratações Públicas do Estado do Rio de Janeiro

Projeto desenvolvido pelo **Time 03** para construção de uma solução de
**Retrieval-Augmented Generation (RAG)** aplicada ao cenário de
**Contratações Públicas do Estado do Rio de Janeiro**.

A aplicação utiliza **FastAPI** como framework backend, **Uvicorn** como
servidor ASGI, **SQLite** como banco de dados local e **SQLAlchemy**
para persistência e acesso aos dados.

O projeto também prevê uma arquitetura de recuperação híbrida utilizando
busca semântica e lexical para construção do pipeline RAG.

------------------------------------------------------------------------

## Início rápido

### 1. Criar e ativar o ambiente

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

``` powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Criar o `.env`

Na raiz do projeto:

``` env
DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Gere uma chave JWT local:

``` powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para `JWT_SECRET_KEY`. O `.env` não deve ser enviado
ao GitHub.

### 4. Inicializar o banco

``` powershell
python -m app.init_db
```

### 5. Criar o primeiro administrador

``` powershell
python -m app.create_admin
```

O comando solicita username, email, senha e confirmação. A senha deve
possuir de 12 a 128 caracteres e somente seu hash é armazenado.

Exemplo de execução:

``` text
Username: alisson
Email: a@a.com
Senha (12 a 128 caracteres):
Confirme a senha:
Administrador criado: alisson (id=1).
```

### 6. Iniciar a API

``` powershell
python -m uvicorn app.main:app --reload
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

ReDoc:

``` text
http://127.0.0.1:8000/redoc
```

### 7. Fazer login

No Swagger:

``` text
Auth → POST /auth/login
```

Envie:

``` json
{
  "username": "alisson",
  "password": "sua senha"
}
```

Copie o `access_token`, clique em **Authorize**, escolha **BearerAuth**
e cole somente o token. Depois teste:

``` text
GET /auth/me
```

As rotas `/admin/*` exigem usuário autenticado com `role = admin`.

------------------------------------------------------------------------

## 1. Tecnologias\*\*

Tecnologias previstas/utilizadas no projeto:

-   Python

-   FastAPI

-   Uvicorn

-   Pydantic

-   Pydantic Settings

-   SQLAlchemy

-   SQLite

-   FAISS

-   BM25

-   RRF

-   Pytest

-   LLM

**---**

## 2. Pré-requisitos\*\*

Antes de executar o projeto, verifique se possui o Python instalado.

\`\`\`bash

python --version

\`\`\`

No Windows também pode ser utilizado:

\`\`\`bash

py --version

\`\`\`

Recomenda-se utilizar **Python 3.12 ou superior\*\***.

**---**

## 3. Clonar o projeto\*\*

Clone o repositório:

\`\`\`bash

git clone
https://github.com/grande-desafio-ia-rag-03/rag-grande-desafio-grupo03-contratacoes-publicas.git

\`\`\`

Entre na pasta:

\`\`\`bash

cd rag-grande-desafio-grupo03-contratacoes-publicas

\`\`\`

Caso seja necessário trabalhar em uma branch específica:

\`\`\`bash

git fetch --all

git switch nome-da-branch

\`\`\`

**---**

# 4. Criar o ambiente virtual\*\*

O ambiente virtual **não é enviado para o GitHub\*\***.

Cada desenvolvedor deverá criar sua própria \`.venv\` depois de clonar o
projeto.

## Windows --- PowerShell\*\*

\`\`\`powershell

py -m venv .venv

\`\`\`

Ative:

\`\`\`powershell

.\\.venv`\Scripts`{=tex}`\Activate`{=tex}.ps1

\`\`\`

## Windows --- Git Bash\*\*

\`\`\`bash

py -m venv .venv

\`\`\`

Ative:

\`\`\`bash

source .venv/Scripts/activate

\`\`\`

Quando estiver ativo, o terminal deverá apresentar algo semelhante a:

\`\`\`text

(.venv)

\`\`\`

**---**

# 5. Instalar as dependências\*\*

Com a \`.venv\` ativada, atualize o \`pip\`:

\`\`\`bash

python -m pip install --upgrade pip

\`\`\`

Se o projeto possuir \`requirements.txt\`:

\`\`\`bash

pip install -r requirements.txt

\`\`\`

Caso esteja realizando a configuração inicial manualmente, as
dependências básicas são:

\`\`\`bash

pip install fastapi "uvicorn\[standard\]" sqlalchemy pydantic-settings

\`\`\`

As dependências específicas do pipeline RAG deverão ser adicionadas ao
\`requirements.txt\` conforme os respectivos módulos forem
implementados.

**---**

# 6. Configuração do \`.env\`\*\*

O projeto utiliza variáveis de ambiente para configurações que não devem
ficar diretamente no código.

Crie o arquivo:

\`\`\`text

.env

\`\`\`

na raiz do projeto.

Exemplo:

\`\`\`env

DATABASE_URL=sqlite:///./app.db

\`\`\`

A estrutura ficará semelhante a:

\`\`\`text

projeto/

├── .env

├── .gitignore

├── README.md

├── app/

└── ...

\`\`\`

\> O arquivo \`.env\` não deve ser enviado para o GitHub.

**---**

# 7. Banco de dados\*\*

O projeto utiliza inicialmente:

-   **SQLite\*\*** --- banco de dados;

-   **SQLAlchemy\*\*** --- ORM e acesso ao banco.

A configuração é definida no \`.env\`:

\`\`\`env

DATABASE_URL=sqlite:///./app.db

\`\`\`

Isso indica que o SQLite deverá utilizar o arquivo:

\`\`\`text

app.db

\`\`\`

na raiz do projeto.

## O que é o \`app.db\`?\*\*

Diferentemente do PostgreSQL, o SQLite não precisa de:

-   servidor de banco;

-   Docker;

-   porta;

-   usuário;

-   senha;

-   serviço executando em segundo plano.

O banco é armazenado em um arquivo local:

\`\`\`text

app.db

\`\`\`

Fluxo:

\`\`\`text

FastAPI

   ↓

SQLAlchemy

   ↓

SQLite

   ↓

app.db

\`\`\`

**---**

# 8. Criação do banco\*\*

Não é necessário criar o arquivo \`app.db\` manualmente.

O SQLite criará o arquivo quando a aplicação estabelecer a conexão e
executar a criação das tabelas.

A configuração principal está localizada em:

\`\`\`text

app/core/database.py

\`\`\`

Exemplo:

\`\`\`python

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

\`\`\`

**---**

# 9. Configuração da aplicação\*\*

As variáveis do \`.env\` são carregadas pelo:

\`\`\`text

app/core/config.py

\`\`\`

Exemplo:

\`\`\`python

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    database_url: str

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

    )

settings = Settings()

\`\`\`

O fluxo de configuração fica:

\`\`\`text

.env

  ↓

config.py

  ↓

database.py

  ↓

SQLAlchemy

  ↓

SQLite

\`\`\`

**---**

# 10. Criando as tabelas\*\*

Com \`DATABASE_URL=sqlite:///./app.db\` no \`.env\`, execute na raiz do
projeto:

\`\`\`bash

python -m app.init_db

\`\`\`

Esse comando cria as tabelas sem depender do Uvicorn. A API chama a
mesma

função \`app.core.database.init_db()\` durante sua inicialização. Ela
importa

todos os models antes de executar \`Base.metadata.create_all()\`,
preservando

dados e tabelas existentes. \`create_all()\` não migra tabelas já
existentes;

alterações futuras de esquema precisarão de migrations.

\| Módulo (\`app/modules/\`) \| Tabelas \|

\|---\|---\|

\| \`corpus/model.py\` \| \`corpus_versions\` \|

\| \`documents/model.py\` \| \`documents\`, \`document_chunks\` \|

\| \`query/model.py\` \| \`queries\`, \`responses\`,
\`response_sources\` \|

\| \`feedback/model.py\` \| \`feedback\` \|

\| \`rag/model.py\` \| \`pipeline_events\` \|

\| \`auth/model.py\` \| \`users\` \|

Todos os models compartilham a \`Base\` de \`app/core/database.py\`,
usando

SQLAlchemy 2.x com \`Mapped\` e \`mapped_column\`.

\`Settings\` ignora variáveis extras do \`.env\`, permitindo
compartilhar o arquivo

com as configurações de modelos já presentes em \`.env.example\`.

Relacionamentos: corpus → documentos → chunks (1:N em cada etapa),

consulta → resposta (1:0..1), resposta → fontes (1:N), chunk → fontes
(1:N),

consulta → feedback (1:N) e consulta → eventos (1:N).

Uma restrição UNIQUE em \`responses.query_id\` impede duas respostas
para a

mesma consulta. \`version\`, \`queries.run_id\` e
\`document_chunks.chunk_id\`

também são únicos. As conexões da aplicação habilitam \`PRAGMA
foreign_keys=ON\`;

não há exclusão em cascata de registros referenciados.

\`response_sources.chunk_id\` é uma FK **inteira\*\*** para
\`document_chunks.id\`.

Já \`document_chunks.chunk_id\` é o identificador **textual\*\***
estável destinado

aos índices externos FAISS e BM25. Não há tabela de índices nem coluna
de

embedding no SQLite.

Os timestamps são gerados pelo SQLite em UTC (sem informação de fuso no

valor armazenado). Valores monetários usam \`Numeric(15, 2)\` e
\`Decimal\` no ORM;

a afinidade NUMERIC do SQLite não impõe precisão/escala como um decimal
fixo.

Metadados opcionais aceitam NULL. \`rating\` permanece inteiro, sem
impor uma

escala de avaliação ainda não especificada.

Os estágios de referência estão em \`PIPELINE_STAGES\` no módulo
\`rag\`:

\`query_analysis\`, \`roteamento\`, \`retrieval_denso\`,
\`retrieval_bm25\`, \`fusao_rrf\`,

\`rerank\`, \`geracao\`, \`validacao\` e \`feedback\`. Eles seguem o
pedido de implementação,

a análise de requisitos e \`notas/AGENTS.md\`; os nomes em inglês nas
seções de

pipeline deste README e de \`ARQUITETURA.md\` divergem dessa convenção.

\`stage\` permanece VARCHAR para permitir extensão sem migração de enum.

A camada de serviços deverá manter o mesmo \`run_id\` da consulta em
seus eventos

e criar novas versões do corpus sem modificar versões publicadas; não
foram

adicionados triggers de imutabilidade nesta camada relacional.

Testes offline (instale \`requirements-dev.txt\`; bancos isolados, sem
alterar o \`app.db\` local):

\`\`\`bash

python -m unittest discover -s tests/integration -p "test\_\*.py" -v

\`\`\`

Os testes cobrem rastreabilidade, FKs, unicidade, consulta sem resposta,

feedback/eventos, tipos de dados e inicialização idempotente pela CLI.

**---**

# 11. Visualizar o SQLite no DBeaver\*\*

O arquivo \`app.db\` pode ser aberto diretamente no **DBeaver\*\***.

Não é necessário deixar o Uvicorn rodando para consultar o banco.

No DBeaver:

1\. Abra **Nova Conexão\*\***.

2\. Escolha **SQLite\*\***.

3\. No campo **Caminho\*\***, clique em **Abrir\*\***.

4\. Selecione o arquivo \`app.db\`.

5\. Clique em **Testar conexão\*\***.

6\. Clique em **Concluir\*\***.

Depois será possível navegar por:

\`\`\`text

app.db

└── Tabelas

    ├── documents

    ├── ...

\`\`\`

Também é possível utilizar o SQL Editor:

\`\`\`sql

SELECT \* FROM documents;

\`\`\`

**---**

# 12. Executar a aplicação\*\*

Com a \`.venv\` ativada e a chave JWT configurada conforme a seção 24:

\`\`\`bash

python -m uvicorn app.main:app --reload

\`\`\`

Também é possível utilizar:

\`\`\`bash

uvicorn app.main:app --reload

\`\`\`

A primeira opção é recomendada porque garante que o Uvicorn utilizado
pertence ao ambiente Python atualmente ativo.

Quando iniciar corretamente, será exibido algo semelhante a:

\`\`\`text

INFO: Uvicorn running on http://127.0.0.1:8000

INFO: Application startup complete.

\`\`\`

**---**

# 13. Acessar a API\*\*

API:

\`\`\`text

http://127.0.0.1:8000

\`\`\`

Swagger:

\`\`\`text

http://127.0.0.1:8000/docs

\`\`\`

Documentação ReDoc:

\`\`\`text

http://127.0.0.1:8000/redoc

\`\`\`

O Swagger será utilizado durante o desenvolvimento para visualizar e
testar os endpoints da aplicação.

**---**

# 14. Estrutura do projeto\*\*

A arquitetura segue uma organização modular.

\`\`\`text

rag-grande-desafio-grupo03-contratacoes-publicas/

│

├── .env

├── .gitignore

├── README.md

├── requirements.txt

│

├── app/

│   ├── **init**.py

│   ├── main.py

│   │

│   ├── core/

│   │   ├── **init**.py

│   │   ├── config.py

│   │   ├── database.py

│   │   ├── exceptions.py

│   │   └── logging.py

│   │

│   └── modules/

│       │

│       ├── normative/

│       │   ├── model.py

│       │   ├── schemas.py

│       │   ├── services.py

│       │   └── routes.py

│       │

│       ├── structured/

│       │   ├── model.py

│       │   ├── schemas.py

│       │   ├── services.py

│       │   └── routes.py

│       │

│       ├── aggregated/

│       │   ├── model.py

│       │   ├── schemas.py

│       │   ├── services.py

│       │   └── routes.py

│       │

│       ├── ingest/

│       │   ├── schemas.py

│       │   ├── services.py

│       │   └── routes.py

│       │

│       ├── retrieval/

│       │   ├── dense.py

│       │   ├── bm25.py

│       │   ├── rrf.py

│       │   ├── reranker.py

│       │   └── services.py

│       │

│       ├── query/

│       │   ├── analyzer.py

│       │   ├── router.py

│       │   └── guardrails.py

│       │

│       ├── rag/

│       │   ├── schemas.py

│       │   ├── services.py

│       │   └── routes.py

│       │

│       └── evaluation/

│           ├── schemas.py

│           ├── services.py

│           └── routes.py

│

├── data/

│   ├── raw/

│   ├── inventory/

│   └── processed/

│

├── indexes/

│   ├── faiss/

│   └── bm25/

│

├── logs/

│

├── tests/

│

└── notes/

    ├── ARQUITETURA.md

    ├── PERSONAS.md

    └── corpus_manifest.yaml

\`\`\`

**---**

# 15. Responsabilidade das principais pastas\*\*

## \`app/\`\*\*

Código principal da aplicação.

## \`app/core/\`\*\*

Configurações compartilhadas pelo sistema.

Contém:

\`\`\`text

config.py

database.py

exceptions.py

logging.py

\`\`\`

## \`app/modules/\`\*\*

Módulos de negócio da aplicação.

Cada módulo deve possuir responsabilidades bem definidas.

Quando aplicável, a estrutura padrão será:

\`\`\`text

model.py

schemas.py

services.py

routes.py

\`\`\`

**\### \`model.py\`**

Models SQLAlchemy e representação das tabelas.

**\### \`schemas.py\`**

Schemas Pydantic para entrada e saída de dados.

**\### \`services.py\`**

Regras de negócio.

**\### \`routes.py\`**

Endpoints FastAPI.

**---**

# 16. Dados e índices\*\*

A pasta:

\`\`\`text

data/

\`\`\`

é utilizada para organização do corpus.

Exemplo:

\`\`\`text

data/

├── raw/

├── inventory/

└── processed/

\`\`\`

Os índices de recuperação serão armazenados separadamente:

\`\`\`text

indexes/

├── faiss/

└── bm25/

\`\`\`

O objetivo é manter responsabilidades diferentes:

\`\`\`text

SQLite

   ↓

dados da aplicação e metadados

FAISS

   ↓

índice vetorial / embeddings

BM25

   ↓

índice lexical

\`\`\`

**---**

# 17. Pipeline RAG planejado\*\*

A arquitetura prevê o seguinte fluxo:

\`\`\`text

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

│                          │

↓                          ↓

dense_retrieval       bm25_retrieval

│                          │

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

\`\`\`

Os nomes dos estágios deverão ser utilizados também no campo \`stage\`
dos logs da aplicação.

**---**

# 18. Bases do projeto\*\*

O projeto foi dividido inicialmente em três bases principais.

## Base Normativa\*\*

Responsáveis:

-   Ana Karina

-   Ester Neves

Responsável pelos documentos jurídicos e normativos.

**---**

## Base Estruturada\*\*

Responsáveis:

-   Alisson Lima de Souza

-   Luciano Costa

Responsável por dados estruturados relacionados às contratações
públicas.

**---**

## Base Agregada\*\*

Responsáveis:

-   Felipe Antunes

-   Renan Freitas

Responsável por indicadores, estatísticas e informações consolidadas.

**---**

# 19. Documentação da sprint\*\*

\| Documento \| Responsável \|

\|---\|---\|

\| \`ARQUITETURA.md\` \| Alisson Lima de Souza \|

\| \`PERSONAS.md\` \| Luciano Costa \|

\| \`corpus_manifest.yaml\` \| Felipe Antunes \|

**---**

# 20. Coordenador\*\*

**Luiz Felipe Antunes\*\***

O coordenador acompanha as atividades, organiza as tarefas e auxilia na
integração das diferentes partes do projeto, além de participar
tecnicamente do desenvolvimento.

**---**

# 21. \`.gitignore\`\*\*

Arquivos locais não devem ser enviados para o GitHub.

O \`.gitignore\` deve possuir pelo menos:

\`\`\`gitignore

\# Ambiente virtual

.venv/

venv/

\# Variáveis de ambiente

.env

\# Banco SQLite local

app.db

\*.db

\# Python

**pycache**/

\*.py\[cod\]

\# Pytest

.pytest_cache/

\# IDE

.vscode/

.idea/

\# Logs

\*.log

\`\`\`

\> A \`.venv\` nunca deve ser versionada. Cada integrante cria seu
próprio ambiente virtual depois de clonar o projeto.

**---**

# 22. Fluxo rápido para novos desenvolvedores\*\*

Depois de clonar o projeto:

\`\`\`bash

git clone
https://github.com/grande-desafio-ia-rag-03/rag-grande-desafio-grupo03-contratacoes-publicas.git

cd rag-grande-desafio-grupo03-contratacoes-publicas

\`\`\`

Criar ambiente:

\`\`\`bash

py -m venv .venv

\`\`\`

Ativar no PowerShell:

\`\`\`powershell

.\\.venv`\Scripts`{=tex}`\Activate`{=tex}.ps1

\`\`\`

Instalar dependências:

\`\`\`bash

pip install -r requirements.txt

\`\`\`

Criar \`.env\` e preencher \`JWT_SECRET_KEY\` com uma chave aleatória
local

(veja a seção 24; a API recusa uma chave vazia):

\`\`\`env

DATABASE_URL=sqlite:///./app.db

JWT_SECRET_KEY=

JWT_ALGORITHM=HS256

JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

\`\`\`

Executar:

\`\`\`bash

python -m uvicorn app.main:app --reload

\`\`\`

Abrir:

\`\`\`text

http://127.0.0.1:8000/docs

\`\`\`

**---**

# 23. Equipe\*\*

**Time 03 --- Contratações Públicas do Estado do Rio de Janeiro\*\***

-   Luiz Felipe Antunes.

-   Ana Karina.

-   Luciano Oliveira.

-   Marcio da Costa.

-   Ester da Silva.

-   Alisson Lima.

-   Renan Freitas.

**Gerente / Coordenador:\*\*** Luiz Felipe Antunes

**---**

# 24. Autenticação JWT e administração\*\*

A autenticação usa a tabela \`users\` no mesmo SQLite, \`Base\`, engine
e sessões

do restante do projeto. O módulo \`auth\` contém o model, os schemas, os
serviços

e as rotas de autenticação. O módulo \`admin\` gerencia esse mesmo
model, sem criar

outra tabela de usuários. Hash de senha, JWT e dependências de
autorização ficam

em \`app/core/security.py\`.

## Instalação e configuração\*\*

Na raiz, com a \`.venv\` ativada:

\`\`\`powershell

python -m pip install -r requirements.txt

\`\`\`

As dependências de autenticação são \`PyJWT\`, \`pwdlib\[argon2\]\` e

\`email-validator\`. Para os testes com \`TestClient\`, instale também:

\`\`\`powershell

python -m pip install -r requirements-dev.txt

\`\`\`

Gere uma chave local:

\`\`\`powershell

python -c "import secrets; print(secrets.token_urlsafe(48))"

\`\`\`

Copie o resultado para \`JWT_SECRET_KEY\` **somente no seu
\`.env\`\*\***, preservando

as demais variáveis. \`.env.example\` contém apenas a chave vazia:

\`\`\`env

DATABASE_URL=sqlite:///./app.db

JWT_SECRET_KEY=

JWT_ALGORITHM=HS256

JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

\`\`\`

A API exige uma chave de pelo menos 32 bytes. Nesta implementação, o
algoritmo

permitido é HS256; a expiração é configurável entre 1 e 10080 minutos.

Não existe chave padrão embutida. A criação do banco e o comando de
criação

do administrador funcionam sem a chave JWT; a inicialização da API a
exige.

## Criar o primeiro administrador\*\*

Execute em um terminal interativo:

\`\`\`powershell

python -m app.init_db

python -m app.create_admin

\`\`\`

O comando pede username, email, senha e confirmação. A senha deve ter de

12 a 128 caracteres e não aparece no terminal nem nos argumentos do
processo.

Somente seu hash Argon2id é salvo. O username aceita letras, números,
\`\_\`,

\`.\` e \`-\`, com 3 a 64 caracteres; ele é normalizado para minúsculas.

Username e email são únicos sem diferenciação de maiúsculas ASCII.

O comando recusa uma segunda criação se já existir qualquer
administrador,

inclusive inativo. Também não sobrescreve contas nem promove um
username/email

já cadastrado. A verificação e a criação usam uma transação SQLite com
bloqueio

de escrita para impedir dois administradores iniciais em execuções
concorrentes.

O cadastro público está disponível em **POST /auth/register\*\***, sem
token.

No Swagger, envie:

\`\`\`json

{

  "username": "novo_usuario",

  "email": "usuario@example.com",

  "password": "uma senha de pelo menos 12 caracteres"

}

\`\`\`

O endpoint retorna **201\*\*** com os dados da conta, sem senha ou hash.

Username ou email duplicado retorna **409\*\***; dados inválidos
retornam **422\*\***.

Depois do cadastro, use \`/auth/login\` para obter o token.

O serviço \`app.modules.auth.services.create_user(db, UserCreate(...))\`
cria somente

usuários com role \`user\`; o schema rejeita \`role\` e \`is_active\` na
entrada.

O primeiro admin é provisionado exclusivamente pelo comando local acima.

Para criar outras contas como \`user\` ou \`admin\`, faça login como
administrador,

autorize o token no Swagger e execute **POST /admin/users\*\***:

\`\`\`json

{

  "username": "novo_admin",

  "email": "novo_admin@example.com",

  "password": "uma senha de pelo menos 12 caracteres",

  "role": "admin"

}

\`\`\`

Use \`"role": "user"\` para usuário comum; esse também é o padrão se
omitido.

O endpoint retorna **201\*\***, rejeita roles diferentes com **422\*\***
e duplicidades

com **409\*\***. Somente administradores autenticados podem utilizá-lo:
sem token

retorna **401\*\***, e usuário comum recebe **403\*\***. O cadastro
público

\`POST /auth/register\` continua rejeitando o campo \`role\`.

## Iniciar e fazer login\*\*

\`\`\`powershell

python -m uvicorn app.main:app --reload

\`\`\`

Abra \`http://127.0.0.1:8000/docs\`. Em **Auth → POST /auth/login\*\***,
clique em

**Try it out\*\*** e envie um JSON com as credenciais criadas:

\`\`\`json

{

  "username": "seu_admin",

  "password": "sua senha definida no comando local"

}

\`\`\`

A resposta contém \`access_token\`, \`token_type: "bearer"\` e
\`expires_in\`

(segundos). O login recebe JSON, não formulário OAuth2.

## Usar o JWT pelo Swagger\*\*

1\. Copie apenas o valor de \`access_token\` retornado pelo login.

2\. Clique em **Authorize\*\*** no topo do Swagger.

3\. Em **BearerAuth\*\***, cole o token, sem escrever \`Bearer \` antes
dele.

4\. Confirme **Authorize\*\*** e feche a janela.

5\. Execute **GET /auth/me\*\*** para consultar a conta autenticada.

6\. Com o admin, teste **GET /admin/users\*\*** e **GET
/admin/users/{user_id}\*\***.

7\. Para alterar uma conta, use **PATCH
/admin/users/{user_id}/status\*\*** com

   \`{"is_active": false}\` ou \`{"is_active": true}\`.

Em outros clientes HTTP, envie o cabeçalho \`Authorization: Bearer
\<access_token\>\`.

Todas as rotas administrativas possuem a dependência \`require_admin\`
no router.

A listagem aceita \`offset\` (padrão 0) e \`limit\` (padrão 50, máximo
100).

\| Situação \| HTTP \|

\|---\|---\|

\| Login válido, usuário ativo \| 200 \|

\| Login inválido, usuário inexistente ou inativo \| 401 \|

\| Token ausente, inválido, expirado ou conta inativa/excluída \| 401 \|

\| Usuário comum acessando \`/admin/\*\` \| 403 \|

\| Admin consulta/altera usuário inexistente \| 404 \|

\| Admin tenta desativar a própria conta \| 409 \|

\| Corpo inválido ou tentativa de alterar role pelo endpoint de status
\| 422 \|

Os tokens têm \`sub\` (ID do usuário), \`iat\` e \`exp\`, e a assinatura
é validada

com o algoritmo definido pelo servidor. A role e o estado ativo são
consultados

no banco em cada requisição: desativar uma conta bloqueia seus tokens já
emitidos.

Reativar a conta permite novamente tokens ainda válidos; não há
revogação

individual, refresh token nem tabela de tokens nesta etapa. As respostas
de

usuário nunca incluem senha ou \`password_hash\`.

## Testar\*\*

\`\`\`powershell

python -m unittest discover -s tests/integration -p "test\_\*.py" -v

\`\`\`

Os testes usam SQLite temporário e chaves aleatórias de teste, sem
depender de

uma chave JWT no \`.env\` e sem criar contas no \`app.db\` real. Cobrem
login,

permissões, tokens inválidos/expirados, contas inativas, unicidade,
hash, criação

inicial concorrente, CLI, Swagger/OpenAPI e a persistência relacional
existente.
