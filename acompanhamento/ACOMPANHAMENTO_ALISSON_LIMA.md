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
## Encontro 2 - 2026-09-18
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

## Encontro 3 - 2026-09-21

### Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na investigação e implementação da integração do projeto com a **API do Portal Nacional de Contratações Públicas (PNCP)**. O objetivo foi criar e validar um microprojeto capaz de consultar dados reais de contratações públicas e acessar os documentos disponibilizados pelo PNCP, preparando a base para a futura etapa de ingestão do pipeline RAG.

Inicialmente, estudei os endpoints disponibilizados pelo PNCP e realizei testes para entender o formato das respostas, parâmetros obrigatórios, paginação e comportamento da API.

A implementação foi organizada no módulo:

```text
app/modules/pncp/
├── __init__.py
├── client.py
└── service.py
```

Foi criado o `client.py` para centralizar a comunicação HTTP com o PNCP. A decisão foi separar a infraestrutura de comunicação das regras de negócio, evitando que cada função do `service.py` precisasse implementar individualmente configuração de sessão, timeout e novas tentativas.

O cliente utiliza `requests.Session` e concentra configurações como:

* sessão HTTP reutilizável;
* timeout das requisições;
* tratamento de erros de conexão;
* novas tentativas para falhas temporárias;
* backoff entre tentativas;
* tratamento de códigos HTTP como `429`, `500`, `502`, `503` e `504`.

Com essa separação, o fluxo principal ficou:

```text
service.py
    ↓
client.py
    ↓
requests.Session
    ↓
API do PNCP
```

No `service.py`, implementei e organizei as operações específicas do PNCP. Atualmente o serviço consegue realizar consultas de:

* modalidades de contratação;
* contratações publicadas;
* contratos;
* contratações com propostas abertas;
* Atas de Registro de Preços vinculadas a uma compra;
* quantidade de documentos de uma ata;
* documentos associados a uma ata;
* download de documentos;
* download dos documentos associados a uma ata.

Durante os testes foi necessário compreender que nem todos os endpoints do PNCP apresentam exatamente o mesmo formato de resposta. Alguns retornam objetos paginados, enquanto outros retornam diretamente listas ou valores simples.

Por exemplo, o endpoint de quantidade de documentos de uma ata retornou diretamente um número inteiro, enquanto o endpoint de documentos retornou uma lista contendo os metadados de cada arquivo.

Também implementei tratamento para evitar registros duplicados durante a paginação, utilizando o campo `numeroControlePNCP` como identificador dos registros já coletados.

### Validação com dados reais do PNCP

Além dos testes automatizados, criei/refatorei o arquivo:

```text
visualizar_pncp.py
```

Esse programa funciona como um teste de integração real. Diferentemente dos testes unitários, ele realiza chamadas diretamente para os servidores do PNCP e apresenta os resultados no terminal.

O fluxo validado pelo programa ficou:

```text
PNCP
 ↓
Modalidades
 ↓
Contratações
 ↓
Contratos
 ↓
Atas
 ↓
Documentos da Ata
 ↓
URL oficial do documento
 ↓
Download do arquivo
```

A consulta de modalidades retornou **19 modalidades ativas**.

Também foi possível realizar consultas paginadas de contratações e contratos. Durante essas consultas foi identificado o código HTTP `429`, indicando limitação por excesso de requisições. O sistema foi preparado para reconhecer essa situação, interrompendo a paginação e preservando os registros que já haviam sido coletados.

Em uma das execuções reais, antes do `429`, foram recuperadas dezenas de contratações e centenas de contratos, demonstrando que a paginação e a coleta estavam funcionando.

### Validação de uma Ata de Registro de Preços

Para validar o fluxo de documentos, utilizei uma contratação real disponível no PNCP com os seguintes identificadores:

```text
CNPJ: 00394452000103
Ano da compra: 2024
Sequencial da compra: 22765
```

A API retornou uma Ata de Registro de Preços com:

```text
Número da ata: 90007
Ano: 2024
Sequencial da ata: 1
Controle PNCP:
00394452000103-1-022765/2024-000001
```

O objeto da contratação está relacionado à aquisição de instrumentos musicais e materiais de consumo para a fanfarra do 2º Regimento de Cavalaria de Guarda.

A partir dessa ata, a aplicação consultou a quantidade de documentos existentes e encontrou:

```text
4 documentos
```

Em seguida, foi utilizado o endpoint de documentos da ata para recuperar os metadados de cada arquivo, incluindo:

```text
sequencialDocumento
titulo
tipoDocumentoNome
url
```

Essa descoberta foi importante porque permite utilizar o `sequencialDocumento` fornecido pelo próprio PNCP, em vez de tentar inferir ou construir manualmente o identificador do documento.

### Download dos documentos

Durante a implementação do download encontrei um problema importante.

Inicialmente, o download era realizado utilizando o mesmo `PNCPClient` empregado nas consultas JSON. Essa chamada retornava:

```text
HTTP 422
```

Entretanto, testes realizados diretamente com a URL fornecida pelo PNCP mostraram que o arquivo existia e podia ser baixado normalmente.

A causa foi isolada na diferença entre as requisições utilizadas para consultar a API JSON e aquelas utilizadas para recuperar arquivos binários.

Por isso, mantive o `PNCPClient` responsável pelas consultas da API e separei o fluxo de download de arquivos.

A arquitetura passou a funcionar da seguinte maneira:

```text
                  PNCP
                   │
        ┌──────────┴──────────┐
        │                     │
   Consultas JSON        Documentos
        │                     │
        ▼                     ▼
   PNCPClient            requests.get
        │                     │
 modalidades,              stream
 contratos, atas              │
 e metadados                  ▼
                         arquivo local
```

Após essa alteração, o download foi realizado com sucesso.

O PNCP retornou o arquivo com:

```text
Content-Type: application/octet-stream
Tamanho: 9.132.650 bytes
Aproximadamente: 8,71 MB
```

O documento foi armazenado localmente em:

```text
downloads_pncp/
└── ata_1_documento_1.pdf
```

O resultado comprovou o funcionamento do fluxo completo desde a consulta dos dados públicos até a recuperação física do documento.

### Testes automatizados

Também trabalhei na refatoração dos testes automatizados utilizando `pytest`.

Os testes anteriores estavam diretamente acoplados à sessão HTTP utilizada pelo `service.py`. Com a criação do `PNCPClient`, os mocks foram alterados para acompanhar a nova arquitetura.

Os testes do serviço passaram a simular a comunicação por meio do cliente, permitindo testar as regras do `service.py` sem depender da disponibilidade real do PNCP.

Após a refatoração foi obtido o seguinte resultado:

```text
19 testes executados
19 testes aprovados
0 falhas
```

Foram testados cenários relacionados a:

* carregamento de modalidades;
* modalidades ativas e inativas;
* erro na consulta de modalidades;
* coleta de contratações;
* remoção de contratações duplicadas;
* ausência de resultados;
* paginação;
* coleta de contratos;
* paginação de contratos;
* contratações com propostas abertas;
* tratamento de erro;
* consulta das atas;
* ausência de atas;
* quantidade de documentos;
* listagem de documentos;
* ausência de documentos;
* erros na consulta de documentos;
* download de documento.

Após a separação final do download binário das consultas JSON, ficou necessária uma nova execução e eventual adequação específica do teste automatizado de download para refletir a implementação atual com `requests.get`.

### Decisões técnicas

As principais decisões técnicas tomadas hoje foram:

1. Separar a infraestrutura HTTP das regras relacionadas ao PNCP por meio de `client.py` e `service.py`.

2. Centralizar no cliente o tratamento de timeout, conexão, tentativas e backoff das consultas JSON.

3. Manter no `service.py` as operações específicas do domínio de contratações públicas.

4. Utilizar a URL oficial retornada pelo próprio PNCP para acessar documentos.

5. Não inferir o identificador dos documentos, utilizando o `sequencialDocumento` retornado pela API.

6. Separar o download de conteúdo binário das consultas JSON.

7. Implementar tratamento de paginação e eliminação de registros duplicados.

8. Identificar e tratar respostas `429` causadas pelo limite de requisições do PNCP.

9. Manter testes automatizados independentes das chamadas reais à API e utilizar o `visualizar_pncp.py` especificamente para testes de integração.

### Resumo do dia

**Entreguei hoje:**

* investigação dos endpoints necessários da API do PNCP;
* criação/refatoração do módulo `pncp`;
* implementação do `client.py`;
* refatoração do `service.py`;
* configuração de sessão HTTP, timeout, retry e backoff;
* consulta das modalidades do PNCP;
* consulta paginada de contratações;
* consulta paginada de contratos;
* consulta de contratações com propostas abertas;
* consulta de Atas de Registro de Preços;
* consulta da quantidade de documentos de uma ata;
* consulta dos metadados dos documentos;
* identificação das URLs oficiais dos arquivos;
* implementação do download de documentos;
* validação do download de um arquivo real de aproximadamente 8,71 MB;
* criação/refatoração do `visualizar_pncp.py` para testes de integração real;
* refatoração dos testes automatizados;
* validação de 19 testes automatizados antes da alteração final do mecanismo de download.

**Problemas encontrados e soluções:**

* O PNCP rejeitou tamanhos de página incompatíveis em alguns endpoints. Ajustei os parâmetros de acordo com o comportamento observado na API.

* Durante consultas paginadas, o PNCP retornou `HTTP 429`. O código passou a identificar o rate limit e interromper a coleta preservando os registros já recuperados.

* O download realizado inicialmente pelo cliente das consultas JSON retornava `HTTP 422`. Separei o download binário das consultas JSON e passei a utilizar diretamente a URL de documento fornecida pelo PNCP.

* Após a alteração, o documento foi baixado corretamente e armazenado na pasta local de downloads.

**Ficou pendente:**

* executar novamente e, se necessário, adequar o teste automatizado do download após a última alteração do `service.py`;

* melhorar a estratégia de tratamento do `HTTP 429`, evitando consultas excessivas ao PNCP;

* avaliar intervalo entre páginas e estratégia de retry específica para rate limit;

* corrigir/normalizar casos pontuais de encoding encontrados nos títulos retornados pelo PNCP;

* implementar o download controlado dos demais documentos necessários;

* iniciar a extração do conteúdo textual dos PDFs;

* definir a estratégia de chunking dos documentos;

* preparar os documentos e metadados para indexação;

* implementar a recuperação híbrida utilizando FAISS e BM25;

* aplicar RRF para fusão dos resultados;

* integrar os documentos provenientes do PNCP ao pipeline RAG.

**Próximo passo:**

O próximo passo será concluir a validação automatizada da camada PNCP e iniciar a etapa de ingestão dos documentos obtidos.

O pipeline planejado é:

```text
PNCP
 ↓
Contratação
 ↓
Ata
 ↓
Documentos
 ↓
Download
 ↓
Extração de texto
 ↓
Normalização
 ↓
Chunks + metadados
 ↓
FAISS + BM25
 ↓
RRF
 ↓
Contexto recuperado
 ↓
LLM
 ↓
Resposta fundamentada
```

Essa etapa transforma o microprojeto de integração com o PNCP na fonte de dados para o pipeline RAG do projeto de Contratações Públicas.

### Uso de assistentes de IA

Utilizei assistentes de IA como apoio para análise dos retornos da API, investigação dos erros HTTP, organização da arquitetura, refatoração do código e elaboração dos testes.

O desenvolvimento foi validado progressivamente com chamadas reais ao PNCP e testes automatizados, permitindo comparar o comportamento esperado com as respostas efetivamente fornecidas pela API.

As decisões de separar `client.py` e `service.py`, utilizar os identificadores retornados pelo próprio PNCP e separar o download binário das consultas JSON foram tomadas a partir dos problemas observados durante os testes e da necessidade de manter o código organizado para a futura integração com o pipeline RAG.

---

