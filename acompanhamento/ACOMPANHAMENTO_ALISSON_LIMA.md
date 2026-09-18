# Acompanhamento - Mini Desafio RAG VendeFácil

**Integrante 1:** Alisson Lima De Souza - [@alisson10000](https://github.com/alisson10000)



**Repositório:** `rag-grande-desafio-grupo03-contratacoes-publicas`

---

## Como preencher

- Um bloco por encontro, em **ordem cronológica** - o encontro mais recente vai no **fim** do arquivo.
- O relato individual é escrito **pelo próprio integrante**, em primeira pessoa. Não escreva pelo colega.
- Escrever entre **17:30 e 17:40**. `commit` + `push` até as **18:00**, mesmo que o dia não tenha fechado.
- Mensagem de commit: `acompanhamento: AAAA-MM-DD`

**Um relato útil responde:** o que eu implementei, qual decisão técnica eu tomei e por quê, onde travei, e como (ou se) resolvi.

<details>
<summary>Exemplo de relato individual bom × ruim</summary>

❌ *"Trabalhei na parte de ingestão junto com meu colega. Avançamos bastante e conseguimos carregar os arquivos."*

✅ *"Implementei os loaders de CSV e JSONL em `src/ingest.py`. Decidi serializar cada linha do `customers.csv` como frase em linguagem natural em vez de manter o formato separado por vírgula, porque nos primeiros testes de similaridade os chunks CSV crus não recuperavam nada - o embedding não separa campo de valor. Travei ~40 min no `tickets.jsonl`: o `state` estava indo para o texto do chunk mas não para os metadados, então o filtro voltava vazio. Resolvi movendo a extração para antes da criação do `Document`. Usei o Claude para gerar o esqueleto do parser de JSONL; ajustei o schema de metadados na mão."*

</details>

---

## Encontro 1 - 2026-09-16



### Relato individual - Alisson Lima de Souza (4h)

Hoje o trabalho ficou concentrado na estruturação inicial do projeto, documentação, configuração do backend e organização do repositório Git.

Foi definida/refinada a Análise de Requisitos do projeto de RAG para o cenário de Contratações Públicas do Estado do Rio de Janeiro.
Foi elaborado o documento de Engenharia de Software, alinhando a arquitetura com a estrutura que será utilizada no código.
Foi definida uma arquitetura modular para o FastAPI, seguindo a organização app/modules/, com módulos separados em model.py, schemas.py, services.py e routes.py.
Foi prevista a pasta notes/ para concentrar documentos do projeto, incluindo análise de requisitos, engenharia de software e demais documentos técnicos.
Foi criado/refinado o AGENTS.md, com instruções para orientar o Codex durante a implementação e evitar alterações fora da arquitetura definida.
Foi configurada a base do backend com FastAPI + Uvicorn + SQLAlchemy + SQLite + Pydantic Settings.
Foi configurado o .env com DATABASE_URL=sqlite:///./app.db e a estrutura de config.py e database.py.
O banco SQLite (app.db) foi criado e foi explicado como acessá-lo pelo DBeaver.
Foi elaborado o README.md com instruções de instalação, criação e ativação da .venv, instalação das dependências, configuração do .env, execução com Uvicorn, acesso ao Swagger, banco de dados e estrutura de pastas.
Foi utilizado pip freeze > requirements.txt para registrar as dependências Python necessárias para que os demais integrantes possam recriar o ambiente com pip install -r requirements.txt.
Foi localizada e utilizada a branch remota feature/estrutura-do-projeto-notes.
Foi identificado um problema no Git: a pasta .venv havia sido versionada, porque inicialmente não estava corretamente ignorada.
O .gitignore foi corrigido para ignorar .venv/, venv/, .env, app.db, bancos locais, caches Python, logs, índices e arquivos gerados.
### Resumo do dia (escrito em conjunto)

**Entregamos hoje:**

- Estruturação inicial do projeto RAG para o cenário de Contratações Públicas
  do Estado do Rio de Janeiro, organizando o backend em FastAPI com arquitetura
  modular.

- Definição da estrutura de pastas do projeto, com organização em `app/core`,
  `app/modules` e `notes`, estabelecendo o padrão dos módulos com `model.py`,
  `schemas.py`, `services.py` e `routes.py`.

- Elaboração e revisão dos documentos de Análise de Requisitos e Engenharia
  de Software, alinhando a documentação com a arquitetura planejada para o
  projeto.

- Criação do `AGENTS.md` para orientar o desenvolvimento com Codex, definindo
  responsabilidades, estrutura do projeto e regras para implementação dos
  módulos.

- Configuração inicial do backend com FastAPI, Uvicorn, SQLAlchemy,
  Pydantic Settings e SQLite.

- Configuração da conexão com o banco de dados por meio do `.env`, utilizando
  `DATABASE_URL=sqlite:///./app.db`, e criação da estrutura inicial de
  `config.py` e `database.py`.

- Criação e validação do banco SQLite `app.db`, incluindo a configuração para
  acesso e inspeção pelo DBeaver.

- Criação do `README.md` com instruções para instalação do projeto, criação e
  ativação do ambiente virtual, instalação das dependências, configuração do
  `.env`, banco de dados, execução do FastAPI/Uvicorn e acesso ao Swagger.

- Geração do `requirements.txt` a partir das dependências instaladas no ambiente
  virtual, permitindo que os demais integrantes reproduzam o ambiente do
  projeto.

- Configuração e utilização da branch
  `feature/estrutura-do-projeto-notes` para desenvolvimento da estrutura e
  documentação.

- Correção do `.gitignore` para impedir o versionamento de arquivos locais e
  gerados, principalmente `.venv/`, `.env`, `app.db`, caches Python, logs e
  índices.

- Correção do problema de versionamento da `.venv`, garantindo que o ambiente
  virtual permaneça somente na máquina de cada desenvolvedor e não seja enviado
  para o repositório.

**Ficou pendente:**

- Implementar os Models SQLAlchemy que representarão as entidades e tabelas
  utilizadas pelo sistema.

- Evoluir os módulos definidos na arquitetura, implementando seus respectivos
  schemas, services e routes.

- Implementar os componentes específicos do pipeline RAG, incluindo ingestão,
  recuperação híbrida, roteamento adaptativo, filtros e geração da resposta.

- Implementar a recuperação utilizando busca semântica (Dense/FAISS) e busca
  lexical (BM25).

- Implementar a fusão dos resultados utilizando RRF e posteriormente a etapa
  de reranking.

- Evoluir a persistência e os mecanismos de observabilidade, testes e avaliação
  definidos na arquitetura.

**Bloqueios em aberto:**

- Nenhum bloqueio técnico impeditivo no momento.

- É necessário continuar o alinhamento entre os integrantes sobre a divisão dos
  próximos módulos e atividades, principalmente as partes do pipeline RAG que
  serão desenvolvidas após a estrutura inicial.

**Próximo passo:**

- Iniciar a implementação dos módulos definidos na Engenharia de Software,
  mantendo o padrão `model.py`, `schemas.py`, `services.py` e `routes.py`.

- Implementar e validar as entidades necessárias no banco SQLite utilizando
  SQLAlchemy.

- Iniciar a implementação do pipeline de ingestão e preparação dos documentos
  das bases de Contratações Públicas.

- Preparar a estrutura para indexação e recuperação utilizando FAISS e BM25.

- Manter os endpoints integrados ao FastAPI para acompanhamento e testes pelo
  Swagger.

**Uso de assistentes de IA:**

Utilizamos assistentes de IA como apoio na elaboração e revisão da documentação
técnica, definição da estrutura de Engenharia de Software, organização dos
módulos do FastAPI, configuração do SQLAlchemy/SQLite, criação das instruções
do projeto e apoio na configuração do Git.

Também utilizamos o Codex como ferramenta de apoio ao desenvolvimento, sendo
criado um `AGENTS.md` para orientar sua atuação de acordo com a arquitetura
definida para o projeto. As decisões sobre arquitetura, organização do projeto,
configuração do ambiente e versionamento foram acompanhadas e validadas durante
o desenvolvimento.

---
## Encontro 1 - 2026-09-18
### Relato individual - Alisson Lima de Souza (4h)

## Atividades realizadas hoje

Hoje foi desenvolvida a parte inicial de **autenticação e controle de acesso** da aplicação de Contratações Públicas do Estado do Rio de Janeiro.

Foi implementada a integração da autenticação com o banco **SQLite**, utilizando a tabela `users` para persistência dos usuários. A estrutura mantém o padrão modular do projeto, separando as responsabilidades entre os módulos `auth` e `admin` e utilizando o mesmo banco `app.db` já adotado pela aplicação.

Na parte de segurança, foi implementado o armazenamento seguro das senhas através de **hash**, evitando que senhas em texto puro sejam gravadas no banco.

Também foi adicionada a autenticação baseada em **JWT (JSON Web Token)**. Após informar usuário e senha no endpoint de login, as credenciais são verificadas e, quando válidas, a API gera um `access_token`. Esse token pode ser utilizado como **Bearer Token** para acessar endpoints protegidos.

Foram configuradas no `.env` as informações necessárias para geração e validação dos tokens:

```env
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Também foi implementada a diferenciação entre os perfis:

```text
user
admin
```

As rotas administrativas ficam protegidas, permitindo acesso somente a usuários autenticados com perfil `admin`.

Foi criado ainda o comando para provisionamento seguro do primeiro administrador:

```powershell
python -m app.create_admin
```

O fluxo foi testado com a criação do primeiro usuário administrador no SQLite.

O fluxo de autenticação implementado ficou:

```text
Usuário + Senha
      ↓
POST /auth/login
      ↓
Consulta do usuário no SQLite
      ↓
Verificação do hash da senha
      ↓
Geração do JWT
      ↓
access_token
      ↓
Bearer Token
      ↓
Acesso às rotas protegidas
```

A autenticação também foi integrada ao **Swagger**, permitindo realizar o login, copiar o `access_token`, utilizar a opção `Authorize` e testar endpoints autenticados diretamente em `/docs`.

Por fim, foi utilizada a branch `feature/banco-login` para concentrar o desenvolvimento relacionado ao **banco de dados, usuários, login, autenticação JWT e administração**, além da atualização das dependências do projeto no `requirements.txt`.
