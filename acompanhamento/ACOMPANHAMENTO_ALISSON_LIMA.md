# Acompanhamento - Mini Desafio RAG VendeFácil

**Integrante 1:** Alisson Lima De Souza - [@alisson10000](https://github.com/alisson10000)



**Repositório:** `rag-grande-desafio-grupo03-contratacoes-publicas`

---



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
## Encontro 4 - 2026-09-23

### Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na evolução da integração com o **Portal Nacional de Contratações Públicas (PNCP)** e na estruturação da persistência dos dados coletados para integração com o pipeline RAG.

Inicialmente, revisei a documentação oficial do PNCP, principalmente os endpoints relacionados à consulta de contratações, contratos, atas e download de documentos. Durante os testes foram identificados comportamentos como timeout, respostas HTTP `422` e diferenças entre endpoints destinados a consultas JSON e endpoints utilizados para download de arquivos.

### Refatoração da camada PNCP

A estrutura do projeto foi organizada separando a comunicação direta com o PNCP da camada de negócio da aplicação.

A organização utilizada ficou:

```text
src/
└── base_estrturada/
    └── pncp/
        ├── __init__.py
        ├── client.py
        └── service.py

app/
└── modules/
    └── pncp/
        ├── model.py
        ├── schemas.py
        ├── services.py
        ├── routes.py
        └── cli.py
```

O `client.py` permaneceu responsável pela infraestrutura HTTP, incluindo sessão reutilizável, timeout, retry, backoff e tratamento de erros transitórios.

O `service.py` da base estruturada ficou responsável pelas operações específicas relacionadas ao PNCP, enquanto o módulo `app/modules/pncp` passou a realizar a integração dessas informações com banco de dados, API FastAPI e demais componentes da aplicação.

Durante essa reorganização também foi identificado e corrigido um problema de importação causado pelo nome do diretório `base_estrturada`, permitindo que o Uvicorn inicializasse novamente a aplicação.

### Persistência dos dados do PNCP

Foi evoluída a estrutura das tabelas responsáveis pelo armazenamento dos dados coletados.

A tabela `pncp_raw_records` passou a representar os registros obtidos diretamente do PNCP, armazenando informações como:

* tipo do registro;
* número de controle PNCP;
* ano;
* sequencial;
* CNPJ do órgão;
* órgão;
* UF;
* objeto;
* payload JSON original;
* data de coleta;
* data de atualização.

Também foi estruturada a tabela `pncp_files`, responsável pelos arquivos associados aos registros coletados.

Foi criado o relacionamento:

```text
PNCPRawRecord
      1
      │
      │
      N
      ▼
PNCPFile
```

Cada arquivo armazenado passou a possuir uma chave estrangeira `pncp_record_id`, permitindo identificar exatamente qual registro do PNCP originou determinado documento.

### Integração PNCP com o modelo do RAG

Também foi revisada a estrutura das tabelas utilizadas pelo pipeline RAG.

O modelo `Document` recebeu a referência opcional `pncp_file_id`, permitindo relacionar um documento processado pelo RAG ao arquivo originalmente obtido do PNCP.

O fluxo de dados planejado passou a ser representado da seguinte maneira:

```text
PNCP
 ↓
PNCPRawRecord
 ↓
PNCPFile
 ↓
Document
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Contexto recuperado
 ↓
LLM
 ↓
Resposta
```

O relacionamento `PNCPFile → Document` foi mantido opcional, permitindo que o sistema continue aceitando documentos provenientes de outras fontes além do PNCP.

### Evolução dos metadados dos chunks

O modelo `DocumentChunk` também foi ampliado para preservar informações relevantes das contratações públicas.

Foram preparados campos como:

```text
numero_controle_pncp
cnpj_orgao
uf
orgao
modalidade
municipio
fornecedor
objeto
valor
ano
data_publicacao
vigencia
```

Esses metadados poderão posteriormente ser utilizados para filtros durante a recuperação das informações, em conjunto com BM25 e FAISS.

### Revisão dos relacionamentos do banco

Durante os testes foi identificado que alterações realizadas nos models SQLAlchemy não modificavam automaticamente as tabelas já existentes no SQLite.

Como o projeto ainda se encontra em fase de desenvolvimento, o banco foi recriado para que o `Base.metadata.create_all()` gerasse novamente as tabelas utilizando os models atualizados.

Também foi habilitada a integridade referencial do SQLite através de:

```text
PRAGMA foreign_keys=ON
```

Após a recriação, foram verificados os principais relacionamentos físicos do banco:

```text
pncp_raw_records
      ↓
pncp_files
      ↓
documents
      ↓
document_chunks
      ↓
response_sources
      ↓
responses
      ↓
queries
```

Também foram validados os relacionamentos auxiliares:

```text
corpus_versions
      ↓
documents

queries
 ├── feedback
 └── pipeline_events
```

Foram adicionadas estratégias de exclusão como `ON DELETE CASCADE` e `ON DELETE SET NULL` de acordo com o tipo de relacionamento.

### Preparação para recuperação híbrida

A estrutura do banco também foi preparada para suportar a futura recuperação híbrida.

Os chunks possuem identificadores próprios e metadados indexados, permitindo posteriormente combinar:

```text
Pergunta do usuário
        ↓
Query Analysis
        ↓
Filtros por metadados
        ↓
┌───────────────┐
│               │
▼               ▼
BM25           FAISS
│               │
└───────┬───────┘
        ↓
       RRF
        ↓
     Reranking
        ↓
     Contexto
        ↓
       LLM
```

A tabela `response_sources` mantém a ligação entre as respostas produzidas e os chunks utilizados como fonte, incluindo informações de `rank` e `relevance_score`.

Isso permitirá posteriormente avaliar quais documentos contribuíram para determinada resposta.

### Problemas encontrados e soluções

Durante o desenvolvimento foram encontrados alguns problemas importantes.

**Erro de importação do módulo PNCP**

A aplicação inicialmente apresentou:

```text
ModuleNotFoundError:
No module named 'src.base_estruturada'
```

Foi identificado que o nome real do diretório era `base_estrturada`. Os imports foram ajustados para corresponder à estrutura física do projeto.

**Diferença entre models e banco SQLite**

O SQLAlchemy tentava consultar campos como `sequencial` e `uf`, mas o banco existente havia sido criado antes da inclusão dessas colunas.

Como `create_all()` não altera tabelas existentes, foi necessário atualizar/recriar a estrutura do banco durante esta fase de desenvolvimento.

**Ausência dos relacionamentos físicos**

Também foi identificado que alguns relacionamentos estavam definidos conceitualmente nos models, mas ainda não existiam como chaves estrangeiras no banco físico.

Os models foram revisados e o banco recriado, passando a conter as FKs necessárias entre PNCP, documentos, chunks, consultas e respostas.

### Resumo do dia

**Entreguei hoje:**

* revisão da documentação e dos endpoints do PNCP;
* análise dos erros de timeout e HTTP `422`;
* evolução do `PNCPClient`;
* organização da camada `src/base_estrturada/pncp`;
* organização do módulo `app/modules/pncp`;
* correção dos imports da camada PNCP;
* integração do módulo PNCP com FastAPI;
* testes dos endpoints pela aplicação;
* evolução dos models `PNCPRawRecord` e `PNCPFile`;
* criação do relacionamento entre registros PNCP e arquivos;
* evolução do model `Document`;
* criação da referência entre `Document` e `PNCPFile`;
* evolução do model `DocumentChunk`;
* inclusão de metadados específicos do PNCP nos chunks;
* revisão dos models `CorpusVersion`, `Query`, `Response`, `ResponseSource`, `PipelineEvent` e `Feedback`;
* habilitação das foreign keys do SQLite;
* recriação do banco durante a fase de desenvolvimento;
* validação das chaves estrangeiras no modelo físico;
* preparação da rastreabilidade entre resposta e chunks utilizados como fonte;
* preparação da estrutura de dados para BM25, FAISS e recuperação híbrida.

### Próximo passo

Com a estrutura de persistência e os relacionamentos principais preparados, o próximo passo será validar o fluxo completo de transformação dos documentos baixados do PNCP em documentos processáveis pelo RAG:

```text
PNCP
 ↓
Coleta
 ↓
Persistência dos metadados
 ↓
Download do documento
 ↓
Document
 ↓
Extração de texto
 ↓
Chunking
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Recuperação
 ↓
LLM
```

A próxima etapa deve verificar principalmente se o serviço responsável pela ingestão, após baixar um `PNCPFile`, já cria corretamente o `Document` correspondente e posteriormente seus `DocumentChunks`.
Encontro 5 - 2026-09-25

Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na evolução da persistência dos documentos relacionados aos contratos obtidos do Portal Nacional de Contratações Públicas (PNCP).

O objetivo principal foi preparar a estrutura do banco de dados para que os documentos associados aos contratos possam ser armazenados e posteriormente utilizados pelo fluxo de ingestão e pelo pipeline RAG.

Persistência dos documentos dos contratos

Foi trabalhada a parte do banco de dados responsável por registrar os documentos vinculados aos contratos coletados do PNCP.

A estrutura segue o fluxo geral:

PNCP
 ↓
Contrato
 ↓
Documento do contrato
 ↓
Persistência no banco
 ↓
Processamento do documento
 ↓
Chunking
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Recuperação
 ↓
LLM

Essa etapa é importante para manter a rastreabilidade entre os dados estruturados obtidos do PNCP e os arquivos que posteriormente serão utilizados pelo sistema RAG.

Estrutura para armazenamento dos documentos

O trabalho realizado hoje ficou concentrado na preparação da persistência necessária para salvar os documentos associados aos contratos.

A ideia é permitir que cada documento mantenha sua relação com o registro de origem, possibilitando posteriormente identificar de qual contratação ou contrato determinado conteúdo foi obtido.

Com essa estrutura, o sistema poderá seguir o fluxo:

Contrato PNCP
      ↓
Documento associado
      ↓
Registro no banco
      ↓
Arquivo/documento persistido
      ↓
Ingestão pelo RAG

Essa associação também será importante para evitar que os documentos utilizados pelo RAG fiquem desconectados dos dados originais do PNCP.

Integração futura com o RAG

A persistência dos documentos representa uma etapa intermediária entre a coleta dos contratos e o processamento do conteúdo pelo RAG.

Após a conclusão dessa estrutura, os documentos poderão seguir para as etapas de:

Documento
    ↓
Extração de texto
    ↓
Normalização
    ↓
Chunking
    ↓
DocumentChunk
    ↓
┌──────────────┐
│              │
▼              ▼
BM25          FAISS
│              │
└──────┬───────┘
       ↓
      RRF
       ↓
Recuperação
       ↓
Contexto
       ↓
LLM

Dessa forma, o banco de dados funciona como parte da ligação entre a coleta das informações públicas e a camada de recuperação de conhecimento.

Versionamento

As alterações realizadas hoje foram organizadas e registradas no repositório por meio de um commit, concentrando as mudanças relacionadas à estrutura do banco para persistência dos documentos dos contratos.

O commit permite manter essa evolução isolada e rastreável dentro do histórico do projeto.

Resumo do dia

Entreguei hoje:

evolução da estrutura de persistência dos documentos relacionados aos contratos;

preparação do banco de dados para registrar os documentos coletados;

organização da relação entre contratos e seus respectivos documentos;

preparação da rastreabilidade da origem dos documentos;

adequação da estrutura para futura integração com o processo de ingestão do RAG;

preparação do fluxo entre documentos persistidos e posterior geração de chunks;

revisão da estrutura necessária para utilização desses documentos pelo BM25 e FAISS;

registro das alterações realizadas em um commit no repositório.

Próximo passo

O próximo passo será continuar a integração entre os documentos dos contratos armazenados no banco e o processo de ingestão do RAG.

O fluxo a ser validado será:

PNCP
 ↓
Contrato
 ↓
Documento do contrato
 ↓
Persistência no banco
 ↓
Download/identificação do arquivo
 ↓
Document
 ↓
Extração do texto
 ↓
Chunking
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Recuperação
 ↓
LLM

A próxima etapa deverá verificar principalmente se os documentos associados aos contratos estão sendo corretamente recuperados a partir do banco e encaminhados para o processamento, permitindo posteriormente a geração dos chunks e sua indexação nos mecanismos de recuperação do RAG.
## Encontro 5 - 2026-09-25

### Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na evolução da **persistência dos documentos relacionados aos contratos obtidos do Portal Nacional de Contratações Públicas (PNCP)**.

O objetivo principal foi preparar a estrutura do banco de dados para que os documentos associados aos contratos possam ser armazenados e posteriormente utilizados pelo fluxo de ingestão e pelo pipeline RAG.

### Persistência dos documentos dos contratos

Foi trabalhada a parte do banco de dados responsável por registrar os documentos vinculados aos contratos coletados do PNCP.

A estrutura segue o fluxo geral:

```text
PNCP
 ↓
Contrato
 ↓
Documento do contrato
 ↓
Persistência no banco
 ↓
Processamento do documento
 ↓
Chunking
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Recuperação
 ↓
LLM
```

Essa etapa é importante para manter a rastreabilidade entre os dados estruturados obtidos do PNCP e os arquivos que posteriormente serão utilizados pelo sistema RAG.

### Estrutura para armazenamento dos documentos

O trabalho realizado hoje ficou concentrado na preparação da persistência necessária para salvar os documentos associados aos contratos.

A ideia é permitir que cada documento mantenha sua relação com o registro de origem, possibilitando posteriormente identificar de qual contratação ou contrato determinado conteúdo foi obtido.

Com essa estrutura, o sistema poderá seguir o fluxo:

```text
Contrato PNCP
      ↓
Documento associado
      ↓
Registro no banco
      ↓
Arquivo/documento persistido
      ↓
Ingestão pelo RAG
```

Essa associação também será importante para evitar que os documentos utilizados pelo RAG fiquem desconectados dos dados originais do PNCP.

### Integração futura com o RAG

A persistência dos documentos representa uma etapa intermediária entre a coleta dos contratos e o processamento do conteúdo pelo RAG.

Após a conclusão dessa estrutura, os documentos poderão seguir para as etapas de:

```text
Documento
    ↓
Extração de texto
    ↓
Normalização
    ↓
Chunking
    ↓
DocumentChunk
    ↓
┌──────────────┐
│              │
▼              ▼
BM25          FAISS
│              │
└──────┬───────┘
       ↓
      RRF
       ↓
Recuperação
       ↓
Contexto
       ↓
LLM
```

Dessa forma, o banco de dados funciona como parte da ligação entre a coleta das informações públicas e a camada de recuperação de conhecimento.

### Versionamento

As alterações realizadas hoje foram organizadas e registradas no repositório por meio de **um commit**, concentrando as mudanças relacionadas à estrutura do banco para persistência dos documentos dos contratos.

O commit permite manter essa evolução isolada e rastreável dentro do histórico do projeto.

### Resumo do dia

**Entreguei hoje:**

- evolução da estrutura de persistência dos documentos relacionados aos contratos;
- preparação do banco de dados para registrar os documentos coletados;
- organização da relação entre contratos e seus respectivos documentos;
- preparação da rastreabilidade da origem dos documentos;
- adequação da estrutura para futura integração com o processo de ingestão do RAG;
- preparação do fluxo entre documentos persistidos e posterior geração de chunks;
- revisão da estrutura necessária para utilização desses documentos pelo BM25 e FAISS;
- registro das alterações realizadas em um commit no repositório.

### Próximo passo

O próximo passo será continuar a integração entre os documentos dos contratos armazenados no banco e o processo de ingestão do RAG.

O fluxo a ser validado será:

```text
PNCP
 ↓
Contrato
 ↓
Documento do contrato
 ↓
Persistência no banco
 ↓
Download/identificação do arquivo
 ↓
Document
 ↓
Extração do texto
 ↓
Chunking
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Recuperação
 ↓
LLM
```

A próxima etapa deverá verificar principalmente se os documentos associados aos contratos estão sendo corretamente recuperados a partir do banco e encaminhados para o processamento, permitindo posteriormente a geração dos chunks e sua indexação nos mecanismos de recuperação do RAG.
## Encontro 6 - 2026-09-28

### Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na evolução do **processo de ingestão e recuperação de informações do RAG**, dando continuidade à estrutura de persistência dos documentos provenientes do Portal Nacional de Contratações Públicas (PNCP).

O objetivo principal foi conectar os documentos e chunks persistidos à camada de recuperação, preparando o sistema para realizar buscas híbridas sobre o conteúdo dos contratos.

### Implementação do retrieval híbrido

Foi implementado o fluxo responsável por recuperar os chunks mais relevantes armazenados no banco de dados.

A estrutura passou a seguir o fluxo:

```text
DocumentChunk
      ↓
┌──────────────┐
│              │
▼              ▼
BM25          Dense
               ↓
             FAISS
│              │
└──────┬───────┘
       ↓
      RRF
       ↓
Chunks ranqueados
```

O **BM25** passou a realizar a recuperação lexical sobre o conteúdo armazenado em `DocumentChunk.content`, permitindo localizar documentos a partir da ocorrência e relevância dos termos da pergunta.

Em paralelo, foi implementada a recuperação densa utilizando embeddings e **FAISS**, permitindo comparar semanticamente a pergunta com o conteúdo dos chunks.

### Integração com embeddings e FAISS

Para a busca densa, foi reutilizada a geração de embeddings já existente no projeto.

O fluxo implementado ficou:

```text
DocumentChunk.content
        ↓
   Embedding
        ↓
 Índice FAISS
        ↓
Pergunta
        ↓
   Embedding
        ↓
Busca vetorial
        ↓
Chunks similares
```

Essa estrutura permite que a recuperação não dependa somente da correspondência exata de palavras, complementando a busca lexical realizada pelo BM25.

### Fusão dos resultados com RRF

Também foi implementado o **Reciprocal Rank Fusion (RRF)** para combinar os rankings provenientes do BM25 e da recuperação densa.

O fluxo passou a ser:

```text
Ranking BM25 ──────┐
                   │
                   ├──→ RRF → Ranking final
                   │
Ranking Dense ─────┘
```

Cada resultado recuperado mantém informações como:

- identificador do chunk;
- conteúdo;
- posição no BM25;
- score do BM25;
- posição na busca densa;
- score da busca densa;
- score final do RRF;
- metadados associados ao documento.

### Testes do retrieval

Foram criados testes para validar separadamente os principais componentes do retrieval híbrido:

```text
BM25
Dense / FAISS
RRF
```

Os testes permitiram verificar que os chunks armazenados podem ser recuperados, ranqueados e combinados corretamente.

### Resumo do dia

**Entreguei hoje:**

- integração de `DocumentChunk` com a camada de recuperação;
- implementação da busca lexical com BM25;
- implementação da busca densa utilizando embeddings;
- criação e utilização do índice FAISS;
- geração de embedding da pergunta;
- implementação da fusão dos rankings com RRF;
- retorno dos chunks ranqueados com scores e metadados;
- criação de testes para BM25, Dense/FAISS e RRF;
- preparação do retrieval para integração com a geração de respostas.

### Próximo passo

O próximo passo será validar o fluxo completo utilizando documentos reais provenientes do PNCP e conectar os chunks recuperados à geração de respostas pela LLM.

O fluxo esperado será:

```text
PNCP
 ↓
Documento
 ↓
Extração
 ↓
DocumentChunk
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Top-K chunks
 ↓
Contexto
 ↓
LLM
 ↓
Resposta fundamentada
```


---

## Encontro 7 - 2026-09-30

### Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na **validação do fluxo completo de ingestão e na integração do retrieval híbrido com a geração e persistência das respostas do RAG**.

O objetivo foi executar o processo com documentos reais provenientes do PNCP, desde o download e extração do conteúdo até a geração de uma resposta fundamentada e rastreável.

### Download e processamento de documentos reais

Inicialmente foi executado o pipeline de download para contratos do período de agosto de 2026.

Foram baixados documentos associados aos contratos e realizada a identificação dos formatos encontrados, incluindo arquivos PDF e ZIP.

O fluxo utilizado foi:

```text
PNCP
 ↓
Contrato
 ↓
Download do documento
 ↓
Identificação do formato
 ↓
PDF / ZIP
 ↓
Extração de texto
```

A extração rápida identificou documentos que necessitavam de processamento mais completo. Para esses casos foi utilizado o **Docling**, incluindo OCR, permitindo extrair o conteúdo dos PDFs.

Dois documentos foram processados com sucesso pelo Docling, produzindo textos com dezenas de milhares de caracteres.

### Persistência de Document e DocumentChunk

Após a extração, os textos ativos foram encaminhados para o pipeline de persistência.

Foi criada uma versão do corpus para garantir o relacionamento correto dos documentos no banco.

Durante essa etapa também foi corrigido o tratamento de chunks duplicados dentro da mesma execução, mantendo o `chunk_id` determinístico e tornando a ingestão idempotente.

O resultado da persistência foi:

```text
textos lidos:             3
documentos criados:       2
chunks criados:          55
chunks reutilizados:     34
```

Com isso, o banco passou a possuir conteúdo real para utilização pelo RAG.

### Validação do retrieval híbrido

Com os chunks persistidos, foi validado o fluxo:

```text
DocumentChunk
      ↓
┌──────────────┐
│              │
▼              ▼
BM25          FAISS
│              │
└──────┬───────┘
       ↓
      RRF
       ↓
Top-K chunks
```

Os testes do retrieval híbrido foram executados com sucesso, confirmando o funcionamento do BM25, da busca densa e da fusão RRF.

### Geração de resposta fundamentada

A etapa seguinte foi conectar os chunks recuperados à LLM.

Foi implementada a montagem de um contexto contendo evidências numeradas e seus respectivos metadados.

O prompt orienta a LLM a responder somente com base nas evidências recuperadas e a citar as evidências utilizadas.

O fluxo passou a funcionar da seguinte maneira:

```text
Pergunta
 ↓
BM25 + FAISS
 ↓
RRF
 ↓
Top-K
 ↓
Contexto com evidências
 ↓
Prompt fundamentado
 ↓
LLM
 ↓
Resposta
```

Foi realizada uma consulta real sobre o objeto do contrato 09/2026 e o sistema conseguiu recuperar as evidências correspondentes e gerar uma resposta fundamentada no conteúdo do contrato.

### Persistência e rastreabilidade da resposta

Também foi implementada a persistência do resultado da consulta.

A estrutura utilizada foi:

```text
Query
 ↓
Response
 ↓
ResponseSource
 ↓
DocumentChunk
```

Cada consulta gera um registro `Query`, enquanto a resposta da LLM é armazenada em `Response`.

As evidências utilizadas são registradas em `ResponseSource`, mantendo a relação com o `DocumentChunk` original.

Também são preservados:

- posição do chunk no ranking;
- identificador interno do `DocumentChunk`;
- score final do RRF;
- relação entre pergunta, resposta e evidências.

A validação confirmou a persistência dos cinco chunks utilizados na resposta, mantendo exatamente a ordem produzida pelo ranking RRF.

### Testes realizados

Foram executados testes para validar as novas etapas:

```text
tests.integration.test_hybrid_retrieval
tests.integration.test_generate
tests.integration.test_query_services
```

Os testes executados foram concluídos com sucesso.

Também foi realizado um teste manual completo utilizando uma pergunta real sobre um contrato armazenado no sistema.

### Fluxo alcançado

Ao final do trabalho, o sistema passou a executar o seguinte fluxo:

```text
PNCP
 ↓
Contrato
 ↓
Download do documento
 ↓
PDF
 ↓
Docling / extração
 ↓
Document
 ↓
DocumentChunk
 ↓
┌──────────────┐
│              │
▼              ▼
BM25          FAISS
│              │
└──────┬───────┘
       ↓



## Encontro 8 - 2026-10-02


### Relato individual - Alisson Lima de Souza (4h)

Hoje concentrei o trabalho na **integração do fluxo RAG com a API FastAPI**, permitindo que perguntas sejam enviadas por meio de um endpoint HTTP e que o sistema execute o processo completo de recuperação, geração da resposta, persistência e retorno das fontes utilizadas.

O trabalho foi realizado na branch:

```text
feature/geracao-resposta-rag
```

O objetivo principal foi disponibilizar pela API o fluxo RAG que anteriormente já funcionava internamente por meio do `src.generate`.

### Criação do endpoint para geração de respostas RAG

Foi criado o endpoint:

```text
POST /query/generate
```

Esse endpoint recebe uma pergunta e a quantidade de chunks que devem ser recuperados pelo RAG.

Exemplo de requisição:

```json
{
  "pergunta": "qual é o objeto do contrato 09/2026?",
  "top_k": 5
}
```

A rota reutiliza o fluxo já implementado em `gerar_resposta_rag()`, evitando duplicação da lógica existente.

Com isso, o fluxo passou a ser:

```text
Cliente / Swagger
       ↓
POST /query/generate
       ↓
FastAPI
       ↓
gerar_resposta_rag()
       ↓
Retrieval híbrido
       ↓
BM25 + FAISS
       ↓
RRF
       ↓
Top-K
       ↓
Contexto com evidências
       ↓
LLM
       ↓
Resposta fundamentada
```

### Criação dos schemas da API

Foram implementados os schemas necessários para representar a entrada e a saída do novo endpoint.

Foram definidos:

```text
GenerateRequest
SourceResponse
GenerateResponse
```

O `GenerateRequest` recebe a pergunta e o parâmetro `top_k`.

O retorno da API contém a resposta produzida pelo RAG e as fontes recuperadas, incluindo informações como:

```text
rank
chunk_id
relevance_score
metadata
```

Dessa forma, além da resposta textual, o cliente consegue identificar quais evidências foram recuperadas pelo sistema.

### Integração da rota com o FastAPI

O módulo de rotas de `query` foi integrado ao `app/main.py`, disponibilizando o novo endpoint na aplicação e também na documentação automática do Swagger.

Com isso, tornou-se possível realizar consultas diretamente pela interface:

```text
Swagger
   ↓
/query/generate
   ↓
RAG
```

A implementação reutiliza o banco de dados por meio da sessão da aplicação e chama:

```text
gerar_resposta_rag(..., persistir=True)
```

Isso permite que a mesma operação execute tanto a geração da resposta quanto sua persistência.

### Validação pelo Swagger

Foi realizado um teste real pelo Swagger utilizando a pergunta:

```text
qual é o objeto do contrato 09/2026?
```

O sistema retornou corretamente:

```text
O objeto do contrato 09/2026 é
"Prestação de serviços de apoio operacional"
```

A resposta foi fundamentada nas evidências recuperadas pelo RAG e apresentou referências como `[1]` e `[2]`.

Além da resposta, a API retornou os cinco chunks recuperados pelo ranking, juntamente com seus metadados.

Entre as informações retornadas estavam:

```text
órgão
município
fornecedor
objeto
valor
ano
data de publicação
vigência
document_id
```

Isso confirmou que o endpoint HTTP consegue executar o RAG utilizando os documentos reais anteriormente ingeridos do PNCP.

### Validação da persistência

Após a execução pelo Swagger, também foi realizada uma consulta diretamente no banco SQLite para verificar se a operação havia sido persistida.

Foi confirmada a criação dos registros relacionados:

```text
Query
  ↓
Response
  ↓
ResponseSource
  ↓
DocumentChunk
```

A consulta utilizada recebeu o registro `Query` de ID `7` e sua respectiva `Response` também foi persistida.

Foram registrados cinco `ResponseSource`, correspondentes aos cinco chunks recuperados:

```text
rank 1 → DocumentChunk 24
rank 2 → DocumentChunk 22
rank 3 → DocumentChunk 2
rank 4 → DocumentChunk 49
rank 5 → DocumentChunk 38
```

Os scores armazenados corresponderam aos valores produzidos pelo ranking RRF.

Dessa forma, foi confirmada a rastreabilidade entre:

```text
Pergunta
   ↓
Resposta
   ↓
Evidências
   ↓
DocumentChunk
   ↓
Documento original
```

### Testes automatizados

Também foram criados testes específicos para o novo endpoint em:

```text
tests/integration/test_query_routes.py
```

Os testes verificam o comportamento da rota, incluindo requisição, geração da resposta, fontes retornadas e utilização da persistência.

Além dos novos testes, foram executados novamente os testes das principais etapas do RAG:

```text
tests.integration.test_hybrid_retrieval
tests.integration.test_generate
tests.integration.test_query_services
tests.integration.test_query_routes
```

Os resultados foram:

```text
Hybrid Retrieval     3 testes → OK
Generate             4 testes → OK
Query Services       1 teste  → OK
Query Routes         4 testes → OK
```

Total:

```text
12 testes executados
12 testes aprovados
```

### Fluxo alcançado

Ao final do trabalho de hoje, o projeto passou a possuir um fluxo completo acessível pela API:

```text
PNCP
 ↓
Contrato
 ↓
Documento
 ↓
Extração de texto
 ↓
Document
 ↓
DocumentChunk
 ↓
┌──────────────┐
│              │
▼              ▼
BM25          FAISS
│              │
└──────┬───────┘
       ↓
      RRF
       ↓
     Top-K
       ↓
Contexto com evidências
       ↓
      LLM
       ↓
Resposta fundamentada
       ↓
Query + Response
       ↓
ResponseSource
       ↓
Resposta HTTP
       ↓
Swagger / Cliente
```

### Arquivos trabalhados

Nesta etapa foram trabalhados principalmente:

```text
app/main.py
app/modules/query/routes.py
app/modules/query/schemas.py
tests/integration/test_query_routes.py
```

A implementação aproveitou os componentes já existentes de retrieval, geração e persistência, evitando alterações desnecessárias no BM25, FAISS e RRF.

### Resumo do dia

**Entreguei hoje:**

- criação do endpoint `POST /query/generate`;
- integração do RAG com a API FastAPI;
- criação dos schemas de entrada e saída da consulta;
- integração da rota de `query` ao `app/main.py`;
- reutilização de `gerar_resposta_rag()` pelo endpoint;
- execução do retrieval híbrido BM25 + FAISS + RRF pela API;
- geração de resposta fundamentada pela LLM;
- retorno das fontes e metadados utilizados;
- persistência de `Query`, `Response` e `ResponseSource`;
- validação da rastreabilidade até o `DocumentChunk`;
- teste real do endpoint utilizando o Swagger;
- criação de testes automatizados da nova rota;
- validação dos testes de retrieval, geração, persistência e API;
- conclusão de **12 testes com sucesso**.

### Próximo passo

O próximo passo será finalizar o versionamento das alterações realizadas na branch `feature/geracao-resposta-rag`, realizar o push para o repositório remoto e posteriormente integrar a funcionalidade à branch default do projeto.

Após essa integração, poderá ser iniciada uma nova etapa de evolução do RAG, mantendo como base o fluxo completo que agora já pode ser utilizado por meio da API:

```text
Pergunta HTTP
      ↓
Retrieval híbrido
      ↓
Evidências
      ↓
LLM
      ↓
Persistência
      ↓
Resposta + fontes
```   
## Encontro 8 - 05/10/2026 

Neste encontro, o trabalho foi concentrado na otimização e validação do processo de indexação vetorial com FAISS e na geração de respostas pelo pipeline RAG.

Foi realizada a separação entre o processo de consulta e o processo de indexação, evitando que o índice FAISS fosse reconstruído durante uma consulta. A indexação passou a ser executada explicitamente por meio do comando:

`py -m src.index --batch-size 64`

Também foi implementado o processamento dos embeddings em lotes (batches), reduzindo significativamente a quantidade de requisições necessárias ao modelo de embeddings. Para aproximadamente 25.513 chunks, utilizando batches de 64 elementos, o processo passou a exigir aproximadamente 399 chamadas ao serviço de embeddings.

Foi adicionada uma barra de progresso para permitir o acompanhamento da geração dos embeddings e da construção do índice FAISS.

Durante os testes de geração da resposta RAG, foi identificado um problema relacionado ao limite de tokens da LLM. O modelo estava configurado com `max_tokens=1024`, ocasionando interrupção da geração com `finish_reason='length'`. A configuração foi ajustada para `GENERATION_MAX_TOKENS=2048`.

Após os ajustes, foi validado o fluxo completo:

**DocumentChunk → Embeddings → FAISS → BM25 + FAISS → RRF → Top-K/Evidências → Prompt → LLM → Resposta**

Com isso, o processo de indexação ficou separado da consulta, o índice FAISS passou a ser reutilizado durante as perguntas e o pipeline RAG foi validado desde a recuperação híbrida das evidências até a geração da resposta pela LLM.

## Encontro 9 - 07/10/2026

Neste encontro, o trabalho foi concentrado na implementação da auditabilidade e dos guardrails do pipeline RAG.

Inicialmente foi implementada a primeira fase de auditabilidade do sistema. Foi criada uma camada específica em `src/audit`, responsável por registrar cada execução do RAG de forma independente.

Cada consulta passou a receber um `trace_id` único, permitindo rastrear todo o processamento realizado para determinada pergunta.

Os registros de auditoria são armazenados em arquivos JSON organizados por data:

`logs/queries/AAAA-MM-DD/<trace_id>.json`

A auditoria passou a registrar informações da requisição, recuperação híbrida, chunks recuperados, posições e scores do BM25, FAISS e RRF, contexto utilizado, prompt enviado à LLM, resposta gerada, tempo de execução, persistência e possíveis erros.

Também foi implementada sanitização para evitar o registro de informações sensíveis, como tokens, chaves de API e cabeçalhos de autorização.

Foi validado que o prompt pode permanecer oculto na resposta apresentada ao usuário (`prompt=null`), enquanto o prompt efetivamente enviado à LLM continua registrado internamente no arquivo de auditoria.

Após a implementação da auditabilidade, foram executados testes do pipeline, confirmando o funcionamento do RAG, das rotas de consulta, da recuperação híbrida e da persistência.

Na segunda etapa foi integrado ao pipeline o guardrail já existente no projeto. A verificação passou a ocorrer após a criação do `trace_id` e antes da recuperação das evidências e da chamada à LLM.

O fluxo passou a seguir:

**Pergunta → Trace ID → Guardrail → Retrieval BM25 + FAISS → RRF → Top-K → Prompt → LLM → Resposta → Auditoria**

Quando uma pergunta viola as regras do guardrail, o processamento é interrompido antes do retrieval e da LLM. Nesse caso, o sistema retorna a mensagem de recusa e registra a tentativa no mesmo mecanismo de auditoria.

Foi realizado um teste com a pergunta:

`Qual empresa devo contratar?`

O guardrail identificou a solicitação de recomendação comercial e retornou a mensagem de recusa, com `sources=[]` e `prompt=null`, sem necessidade de consultar as evidências ou acionar a LLM.

Os testes automatizados também foram executados após a integração. Foram validados os testes de geração/auditoria, rotas de consulta, recuperação híbrida e persistência, totalizando 19 testes aprovados.

Com essas implementações, o RAG passou a possuir rastreabilidade das consultas e uma camada inicial de proteção antes da recuperação de informações e da geração de respostas.

## Encontro 10 - 07/10/26

Neste encontro, foi realizada a continuidade da evolução da arquitetura do sistema RAG para contratações públicas, com foco na validação da auditabilidade e na integração definitiva do Guardrail ao fluxo de geração de respostas.

A implementação de auditabilidade desenvolvida anteriormente foi organizada em uma branch específica, `feature/auditabilidade-rag`, testada e integrada ao fluxo principal do projeto.

A camada de auditoria utiliza um `trace_id` único para cada consulta e registra os dados da execução em:

`logs/queries/AAAA-MM-DD/<trace_id>.json`

Cada execução pode registrar a pergunta recebida, estratégia de retrieval utilizada, chunks recuperados, posições e scores do BM25 e FAISS, score do RRF, contexto enviado à geração, prompt utilizado, resposta produzida, tempo de processamento, informações de persistência e possíveis erros.

Em seguida, foi criada a branch:

`feature/guardrail-rag`

Nessa branch foi realizada a segunda fase da evolução do pipeline, integrando o Guardrail existente ao processo auditável.

O fluxo passou a funcionar da seguinte forma:

**Pergunta → Trace ID → Guardrail → Retrieval → BM25 + FAISS → RRF → Top-K → Contexto → Prompt → LLM → Resposta → Auditoria**

O Guardrail passou a ser executado antes do retrieval e antes da chamada à LLM. Dessa forma, perguntas que violam as regras definidas podem ser interrompidas antecipadamente, evitando processamento desnecessário.

Foi realizado um teste utilizando a pergunta:

`Qual empresa devo contratar?`

Essa pergunta corresponde a uma das regras de recusa comercial existentes no Guardrail. O sistema bloqueou corretamente a solicitação e retornou a mensagem padrão de recusa.

O resultado apresentou:

`"sources": []`

e:

`"prompt": null`

confirmando que a solicitação foi interrompida antes da recuperação das evidências e da geração pela LLM.

Mesmo quando uma pergunta é bloqueada, a execução continua sendo rastreável pelo mecanismo de auditoria. O trace registra que o Guardrail foi verificado, se houve bloqueio, o motivo da recusa e a mensagem retornada.

Foram mantidas também as regras de sanitização dos registros de auditoria para impedir o armazenamento de informações sensíveis, como tokens, chaves de API e dados de autorização.

Após a implementação, foram executados os testes de integração relacionados à geração de respostas, auditoria, rotas de consulta, recuperação híbrida e persistência. Os testes foram concluídos com sucesso.

Com essa etapa, o pipeline passou a possuir duas características importantes antes da geração da resposta:

**Rastreabilidade**, por meio da camada de auditoria e do `trace_id`.

**Controle de escopo**, por meio do Guardrail executado antes do retrieval e da LLM.

A arquitetura resultante prepara o sistema para as próximas evoluções, principalmente a introdução de mecanismos capazes de analisar a intenção da pergunta e decidir qual estratégia de recuperação deve ser utilizada antes de consultar as fontes de dados.

## Encontro 11 — Validação do Query Analyzer e Testes de Classificação de Consultas

**Data:** 09/10/2026  
**Projeto:** RAG — Contratações Públicas  
**Tema:** Validação do Query Analyzer com consultas estruturadas, documentais e híbridas.

## 1. Objetivo do encontro

O décimo primeiro encontro teve como objetivo validar o funcionamento do **Query Analyzer**, componente responsável por interpretar as perguntas dos usuários e identificar a estratégia mais adequada para seu processamento.

A validação buscou verificar se o componente consegue distinguir consultas que exigem acesso a dados estruturados (SQL), recuperação de informações documentais (RAG) ou uma combinação das duas abordagens (Hybrid).

## 2. Atividades realizadas

### 2.1. Execução e validação do Query Analyzer

Foram realizados testes diretamente no ambiente virtual do projeto, utilizando o comando:

```powershell
python -m src.query.analyzer
```

As perguntas foram submetidas ao modelo de linguagem, e os resultados foram analisados a partir dos objetos JSON gerados pelo componente.

Foram avaliados os principais campos de classificação, incluindo `route`, `intent`, `entity`, `operation`, `field`, `filters`, `requires_sql` e `requires_rag`.

### 2.2. Validação de consultas estruturadas

Foram testadas perguntas relacionadas à contagem de contratos, identificação de objetos contratuais e aplicação de filtros por período, município, número do contrato e órgão público.

O Query Analyzer demonstrou capacidade de reconhecer consultas que dependem de dados estruturados, classificando-as com a rota `structured` e identificando a necessidade de execução SQL.

### 2.3. Conferência dos dados no banco SQLite

Foi realizada uma validação por meio de consultas SQL diretamente no banco de dados do projeto, utilizando os registros estruturados provenientes do PNCP.

Os resultados encontrados foram:

- **6.021 contratos distintos** publicados em agosto de 2026, considerando os dados disponíveis no banco.
- **3.855 contratos distintos** publicados no mesmo período, com município identificado como Rio de Janeiro.

A consulta utilizou informações armazenadas no campo JSON `payload` da tabela `raw_asset`, especialmente os atributos `dataPublicacaoPncp`, `numeroControlePNCP` e `unidadeOrgao.municipioNome`.

Essa etapa permitiu verificar que os filtros reconhecidos pelo Analyzer podem ser traduzidos em consultas SQL sobre a estrutura real do banco de dados.

### 2.4. Teste de classificação híbrida (SQL + RAG)

Foi utilizada a seguinte pergunta:

**“Quais contratos publicados em agosto de 2026 no município do Rio de Janeiro possuem cláusulas de penalidade por atraso?”**

O Analyzer retornou:

```json
{
  "route": "hybrid",
  "requires_sql": true,
  "requires_rag": true
}
```

O resultado demonstrou que o componente reconheceu corretamente a necessidade de combinar filtros estruturados com análise de conteúdo documental.

Entretanto, foi identificada uma oportunidade de melhoria: os termos relacionados a penalidades e atrasos não foram preenchidos no campo `filters.termos`, embora estivessem presentes na pergunta original.

Também foi observada a necessidade de padronizar a representação dos períodos, pois algumas consultas retornaram os campos `ano` e `mes`, enquanto outras utilizaram `periodo_inicio` e `periodo_fim`.

### 2.5. Teste com múltiplos identificadores

Foi submetida a pergunta:

**“Qual é o objeto do contrato 09/2026 do Ministério da Justiça?”**

O Analyzer classificou corretamente a consulta como estruturada e identificou simultaneamente o número do contrato, o órgão público e o campo solicitado (`objeto`).

Esse teste demonstrou a importância de utilizar identificadores combinados, considerando que números de contratos podem se repetir entre diferentes órgãos públicos.

### 2.6. Identificação de falha em consulta ambígua

Foi realizado um teste com a pergunta:

**“Qual é o valor do contrato?”**

O Analyzer retornou incorretamente uma operação de agregação (`SUM`), mesmo sem o usuário solicitar a soma de valores.

A classificação esperada seria uma consulta individual (`lookup`), acompanhada do reconhecimento de que faltam informações para identificar o contrato.

Essa falha representa um risco para a execução futura de consultas SQL, pois poderia resultar na soma de valores de vários contratos em vez da recuperação do valor de um contrato específico.

Foi identificada a necessidade de aprimorar as regras de classificação e o tratamento de perguntas ambíguas.

## 3. Resultados alcançados

Ao longo da bateria de validação, foram realizados **sete testes manuais**, dos quais seis apresentaram classificações coerentes e um revelou uma falha de interpretação.

Os principais resultados foram:

- Validação da identificação de consultas estruturadas.
- Reconhecimento de perguntas que exigem recuperação documental.
- Identificação correta da necessidade de processamento híbrido.
- Extração de filtros relacionados a datas, municípios, órgãos e números de contratos.
- Conferência de filtros com registros reais do banco SQLite.
- Identificação de inconsistências na padronização dos filtros e na interpretação de consultas ambíguas.

Os testes confirmaram o funcionamento básico do Query Analyzer, mas também evidenciaram melhorias necessárias antes de sua integração completa ao fluxo de consultas.

## 4. Pendências e próximos passos

As próximas atividades previstas são:

1. Corrigir a classificação de perguntas ambíguas, evitando operações de agregação indevidas.
2. Melhorar a extração de termos relevantes em consultas híbridas.
3. Padronizar os filtros temporais produzidos pelo Analyzer.
4. Criar testes de regressão para os problemas identificados.
5. Validar posteriormente a integração entre Query Analyzer, Query Router, SQL Executor e RAG, respeitando as responsabilidades de implementação de cada componente.

## 5. Conclusão

O Encontro 11 foi dedicado à **validação funcional do Query Analyzer**, utilizando perguntas reais e verificações sobre os dados de contratações públicas armazenados no projeto.

Os resultados demonstraram que o componente consegue diferenciar consultas estruturadas, documentais e híbridas, além de extrair filtros relevantes para o processamento das perguntas.

A principal contribuição do encontro foi identificar, por meio de testes práticos, tanto os comportamentos corretos quanto uma falha de interpretação que precisa ser corrigida. Dessa forma, a atividade contribuiu para o aprimoramento da confiabilidade do sistema RAG de Contratações Públicas.

**Situação ao final do encontro:** validação manual realizada, resultados registrados e melhorias identificadas para implementação posterior.
## Acompanhamento – Encontro 12
**Data:** 14/10/2026  
**Projeto:** RAG – Contratações Públicas

### Atividades realizadas

No 12º encontro, demos continuidade ao desenvolvimento e à otimização do sistema RAG de Contratações Públicas, concentrando os esforços na investigação do elevado tempo de resposta do modelo de linguagem (LLM) disponibilizado pela infraestrutura ECOA.

Durante os testes realizados na API FastAPI, identificamos que o sistema apresentava lentidão significativa na geração das respostas, chegando a ultrapassar sete minutos em determinadas consultas.

Para investigar o problema, implementamos mecanismos de observabilidade e registros detalhados de desempenho, permitindo acompanhar individualmente o tempo gasto pelo Query Analyzer, pela recuperação híbrida (FTS5 e FAISS), pela geração de embeddings e pela LLM responsável pela resposta final.

A análise demonstrou que o principal gargalo não estava na recuperação dos documentos, mas nas requisições ao modelo de linguagem hospedado na ECOA. Em uma das execuções, o Query Analyzer consumiu aproximadamente 213 segundos e a geração da resposta final levou cerca de 242 segundos.

Como alternativa para melhorar a disponibilidade do sistema, implementamos um mecanismo de fallback da ECOA para a API da OpenAI, inicialmente aplicado apenas ao Query Analyzer. Dessa forma, em situações de falha ou timeout configurado, o sistema poderá recorrer a outro provedor para realizar a análise da pergunta.

### Resultados obtidos

Após as implementações e novos testes, registramos uma execução com tempo total de aproximadamente 61 segundos, representando uma redução significativa em relação à execução anterior de 456 segundos.

Entretanto, em outro teste, o tempo total foi de aproximadamente 80 segundos, sendo 15,63 segundos consumidos pelo Query Analyzer e 63,39 segundos pela geração da resposta final.

Esses resultados demonstram uma grande variação no tempo de processamento da LLM ECOA. Embora tenha ocorrido uma redução expressiva no tempo observado, ainda não é possível atribuir essa melhoria diretamente ao mecanismo de fallback, pois as chamadas analisadas foram concluídas com sucesso pelo provedor principal, sem indicação de acionamento da OpenAI.

### Problemas identificados

O principal problema permanece relacionado à latência e à instabilidade do tempo de resposta da LLM ECOA, que representa a maior parte do processamento das consultas.

Também identificamos a necessidade de aprimorar os registros de observabilidade para informar explicitamente qual provedor, ECOA ou OpenAI, foi utilizado em cada requisição.

### Próximos passos

Continuar monitorando o desempenho das chamadas à ECOA, validar o funcionamento do fallback para OpenAI e avaliar alternativas para reduzir o tempo de geração das respostas finais.

Também será necessário aprimorar os logs para identificar o provedor e o modelo utilizados, permitindo comparar o desempenho das diferentes soluções e tomar decisões com base nos resultados dos testes.

**Conclusão:** o encontro permitiu identificar e medir o principal gargalo de desempenho do RAG, implementar uma estratégia inicial de contingência e estabelecer uma base de observabilidade para futuras otimizações.
## Encontro 13 — Relatório de Atividades
**Data:** 16/10/2026  
**Projeto:** RAG — Contratações Públicas

### Objetivo
Realizar testes de integração e funcionamento do sistema RAG, verificando a comunicação com os modelos de linguagem, a recuperação de documentos e a geração de respostas.

### Atividades realizadas

1. **Correção das configurações do ambiente (`.env`):** ajustada a URL de conexão com o servidor ECOA e configurado o fallback para a OpenAI em caso de falha na geração de respostas.

2. **Testes da API FastAPI:** execução do servidor Uvicorn e realização de consultas pelo endpoint `/query/ask`, com retorno HTTP 200.

3. **Validação do modelo ECOA:** análise dos logs confirmou que o ECOA realizou a interpretação da pergunta (Query Analyzer) e a geração da resposta final.

4. **Validação da recuperação RAG:** confirmado o funcionamento da busca híbrida utilizando FTS5, FAISS e RRF, com recuperação de cinco fontes documentais na consulta analisada.

5. **Teste da OpenAI:** realizada uma chamada direta ao modelo `gpt-4.1-mini`, confirmando o funcionamento da API. O fallback automático do RAG ainda não foi testado.

6. **Interface Streamlit:** identificado o arquivo `app/streamlit_console.py` e definido o comando para executar a interface do sistema.

7. **Arquitetura do banco de dados:** revisada a utilização do SQLAlchemy como ORM, SQLite como banco de dados e Alembic para migrações.

### Resultados
O sistema RAG conseguiu executar o fluxo completo de consulta, desde a interpretação da pergunta até a recuperação de documentos e geração da resposta. A consulta analisada foi concluída em aproximadamente 38 segundos, utilizando o ECOA como provedor de linguagem.

### Próximas atividades
Validar o fallback automático para OpenAI, avaliar a qualidade das respostas geradas, verificar a correspondência entre respostas e fontes documentais e continuar os testes de integração com o Streamlit.

### Conclusão
O Encontro 13 foi dedicado à correção de configurações e à validação operacional do sistema RAG. Os testes demonstraram o funcionamento dos principais componentes, permanecendo como próxima etapa a avaliação da precisão e da fundamentação das respostas.
# Encontro 14 — Validação do Sistema RAG de Contratações Públicas

**Data:** 19/10/2026  
**Projeto:** RAG — Grande Desafio Grupo 03 — Contratações Públicas

## 1. Objetivo do encontro

O Encontro 14 foi dedicado à elaboração e à organização de perguntas para validar o funcionamento do sistema RAG de Contratações Públicas.

O objetivo foi estabelecer cenários de testes capazes de verificar a recuperação de informações estruturadas do banco de dados, a interpretação de documentos e a combinação dessas duas fontes de informação.

## 2. Atividades realizadas

### 2.1. Elaboração de perguntas estruturadas

Foram definidas duas perguntas para avaliar a capacidade do sistema de consultar informações armazenadas diretamente no banco de dados:

1. Quantas contratações por dispensa existem em 2026?
2. Liste as 10 contratações de 2026 com maior valor estimado.

Esses testes têm como finalidade verificar a execução de consultas estruturadas, incluindo contagem de registros, filtragem por modalidade e ano, ordenação e recuperação de valores.

### 2.2. Elaboração de perguntas documentais — RAG

Foram organizadas oito perguntas que exigem recuperação e interpretação de conteúdos documentais.

Segundo Luciano Oliveira, essas perguntas possuem evidências reais nos documentos armazenados no banco de dados.

1. Quais práticas de sustentabilidade são previstas para a contratação de manutenção de elevadores?
2. Quais obrigações de LGPD são previstas nos documentos de contratação?
3. Como ocorre a fiscalização administrativa do contrato?
4. Quais documentos são necessários para verificar a habilitação da contratada?
5. Quais são as condições previstas para reajuste contratual?
6. Quais obrigações da contratada estão relacionadas à execução do contrato?
7. Como funciona a subcontratação nos documentos recuperados?
8. Quais exigências existem para manutenção das condições de habilitação?

Essas perguntas foram selecionadas para avaliar a capacidade do RAG de localizar trechos relevantes, interpretar cláusulas contratuais e produzir respostas fundamentadas nas evidências documentais.

### 2.3. Elaboração de pergunta híbrida

Foi definida uma pergunta que combina dados estruturados e recuperação documental:

**Pergunta:**

> Para a contratação `00394502000144-1-009055/2026`, informe o valor estimado e as práticas de sustentabilidade previstas.

Esse cenário busca verificar se o sistema consegue identificar uma contratação específica, consultar seu valor estimado no banco de dados e recuperar as práticas de sustentabilidade presentes nos documentos relacionados.

## 3. Estratégia de validação

As perguntas foram organizadas em três categorias:

| Categoria | Quantidade | Finalidade |
|---|---:|---|
| Estruturadas | 2 | Validar consultas e operações sobre dados do banco |
| Documentais (RAG) | 8 | Validar recuperação semântica e fundamentação documental |
| Híbridas | 1 | Validar a integração entre dados estruturados e documentos |
| **Total** | **11** | **Cenários de validação definidos** |

## 4. Critérios de avaliação

Foram estabelecidos os seguintes critérios para avaliar as respostas do sistema:

- **Correção:** as informações apresentadas devem corresponder aos dados existentes.
- **Relevância:** os documentos recuperados devem estar relacionados à pergunta.
- **Fundamentação:** as afirmações devem ser sustentadas por evidências documentais.
- **Rastreabilidade:** quando aplicável, a resposta deve permitir identificar os documentos utilizados.
- **Integração:** nas perguntas híbridas, os dados estruturados e documentais devem corresponder à mesma contratação.

## 5. Resultados do encontro

Foram definidos **11 cenários de testes**, distribuídos entre consultas estruturadas, documentais e híbridas.

A elaboração dessas perguntas estabeleceu uma base para avaliar o comportamento do sistema em diferentes situações, especialmente quanto à recuperação de evidências, à precisão das respostas e à integração entre as fontes de informação.

**Nesta etapa, o resultado documentado foi a preparação dos cenários de validação.** Não foram apresentados resultados de execução das 11 perguntas nem métricas de desempenho ou precisão.

## 6. Próximos passos

1. Executar as 11 perguntas no sistema.
2. Registrar as respostas produzidas e as fontes recuperadas.
3. Comparar os resultados com os registros e documentos originais.
4. Identificar respostas incorretas, incompletas ou sem fundamentação.
5. Avaliar possíveis melhorias na recuperação documental e na geração de respostas.

## 7. Conclusão

O Encontro 14 teve como foco a preparação da validação funcional do sistema RAG de Contratações Públicas.

A definição de perguntas estruturadas, documentais e híbridas permitirá avaliar não apenas se o sistema consegue gerar respostas, mas principalmente se essas respostas são corretas, relevantes e fundamentadas nos dados disponíveis.

Essa atividade representa uma etapa importante para verificar a confiabilidade do sistema e orientar os próximos ajustes de desenvolvimento.
