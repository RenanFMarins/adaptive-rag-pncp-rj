# Acompanhamento - Mini Desafio RAG VendeFácil

**Integrante 1:** José Renan Freita Marins - [@RenanFMarins](https://github.com/RenanFMarins)



**Repositório:** `rag-grande-desafio-grupo03-contratacoes-publicas`

---

## Encontro 1 - 2026-09-16



### Relato individual - José Renan freitas Marins (4h)

## Relato individual — José Renan Freitas Marins (4h)

Hoje concentrei meu trabalho na análise e estruturação da arquitetura do novo projeto de Inteligência Artificial Generativa com RAG, referente ao **Cenário 1 — Contratações Públicas do Estado do Rio de Janeiro**.

Inicialmente, analisei o documento oficial disponibilizado pelo professor para compreender os requisitos técnicos, os entregáveis e as restrições do projeto. A partir disso, confirmei que o sistema deverá trabalhar com quatro bases de naturezas diferentes:

- normativa;
- estruturada;
- conversacional;
- agregada.

Também identifiquei que o projeto deverá utilizar uma abordagem de **Adaptive RAG**, na qual o sistema precisa decidir qual tipo de evidência deve ser consultado antes de realizar a recuperação das informações.

Durante a análise, trabalhei na definição da arquitetura completa do sistema. A arquitetura foi organizada em grandes etapas:

1. fontes de dados;
2. coleta e versionamento do corpus;
3. ingestão e processamento;
4. indexação;
5. processamento da pergunta;
6. recuperação híbrida;
7. geração e segurança;
8. interface e feedback.

Também foram consideradas como camadas transversais:

- observabilidade;
- testes;
- avaliação;
- configuração.

Foi definido que a organização das informações não deverá ser feita apenas pelo formato dos arquivos, como PDF, JSON ou CSV. A arquitetura deverá considerar principalmente a **natureza da evidência**. Dessa forma, documentos diferentes poderão ser classificados como base normativa, estruturada, conversacional ou agregada.

Outro ponto analisado foi o fluxo de recuperação das informações. Foi planejado o uso de:

- Dense Retrieval;
- BM25;
- filtros por metadados;
- RRF;
- rerank por cross-encoder;
- seleção Top-K.

Também foi discutida a função do **Adaptive Router**, responsável por decidir qual ou quais bases deverão ser consultadas para responder uma pergunta. Foi identificado que algumas consultas poderão exigir múltiplas rotas simultaneamente.

Um exemplo analisado foi:

“Sou MEI, posso participar de pregão eletrônico? Tem algum aberto para material de escritório?”

Nesse caso, o sistema deverá consultar tanto a base normativa quanto a base estruturada.

Também trabalhei na organização da arquitetura em etapas menores para permitir que o projeto seja desenvolvido progressivamente e dividido entre os integrantes da equipe.

A arquitetura foi transformada em módulos de responsabilidade, como:

- corpus e coleta;
- ingestão;
- indexação;
- Adaptive Router;
- retrieval;
- RRF;
- rerank;
- geração;
- guardrails;
- observabilidade;
- avaliação;
- interface.

Essa divisão foi pensada para facilitar a distribuição das tarefas entre os integrantes e reduzir dependências entre os trabalhos.

Também foi elaborado um diagrama visual da arquitetura completa, utilizando como referência a estrutura visual do projeto anterior de RAG, porém adaptando o fluxo para o novo desafio de Contratações Públicas.

Após isso, analisei novamente o documento oficial do professor para separar claramente:

- requisitos obrigatórios do desafio;
- decisões arquiteturais propostas pela equipe.

Essa análise mostrou que alguns módulos são explicitamente esperados pelo projeto, como:

- `fetch_corpus.py`;
- `ingest.py`;
- `index.py`;
- `router.py`;
- `retrieve.py`;
- `generate.py`;
- `schema.py`;
- `obs.py`.

Também identifiquei a importância do `corpus_manifest.yaml`, que deverá funcionar como fonte única de verdade do corpus, e do versionamento dos dados através de versões imutáveis como `v1`, `v2`, etc.

Outro ponto importante estudado foi a necessidade de observabilidade desde o início do desenvolvimento, utilizando logs estruturados com informações como:

- `run_id`;
- `query_id`;
- `stage`;
- latência;
- tokens;
- modelo utilizado;
- filtros;
- resultados das etapas.

Além disso, foram analisados os três níveis de testes previstos:

- testes unitários;
- testes de contrato;
- testes de integração.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:

- analisar o documento oficial do desafio;
- estruturar a arquitetura do sistema;
- organizar o projeto em módulos;
- definir o fluxo do Adaptive RAG;
- discutir estratégias de divisão de responsabilidades;
- gerar uma representação visual da arquitetura;

As sugestões foram analisadas e adaptadas ao cenário de **Contratações Públicas do Estado do Rio de Janeiro**, mantendo como referência principal os requisitos definidos pelo professor.

### Resultado do encontro

Ao final do trabalho, consegui ter uma visão mais completa da arquitetura que o projeto deverá seguir e de como ela pode ser dividida entre os integrantes da equipe.

O principal resultado foi transformar os requisitos do desafio em uma arquitetura técnica organizada, modular e preparada para ser apresentada ao grupo antes da divisão das tarefas.

### Próximos passos

Os próximos passos serão:
- iniciar a implementação das primeiras etapas relacionadas ao corpus e à coleta dos dados.

**Uso de assistentes de IA:**

A IA foi utilizada principalmente para:

- interpretar os requisitos do desafio;
- organizar a arquitetura geral do sistema;
- estruturar o fluxo do Adaptive RAG;
- separar as responsabilidades dos módulos;
- discutir a divisão das tarefas entre os integrantes da equipe;
---

## Encontro 2 - 2026-09-18

### Relato individual — José Renan Freitas Marins (4h)

Hoje concentrei meu trabalho na implementação da primeira etapa técnica sob minha responsabilidade no projeto: a **Base Agregada**, com foco inicial na coleta e preservação dos dados provenientes do **Portal Nacional de Contratações Públicas (PNCP)**.

A partir da arquitetura definida no encontro anterioriniciando pela seguinte etapa:

PNCP → Coleta → Controle de sincronização → Detecção de alterações → RAW → SQLite.

### Estruturação da Base Agregada

Dentro da divisão de responsabilidades da equipe, fiquei responsável pela **base de natureza agregada**.

Foi definido que essa base trabalhará inicialmente com informações relacionadas ao:

- Plano de Contratações Anual — PCA;
- valores e indicadores provenientes das contratações públicas;
- dados quantitativos que posteriormente poderão ser utilizados em operações como média, soma, contagem, agrupamentos e comparação de valores.

Antes de implementar cálculos e agregações, decidi priorizar a construção de uma camada de ingestão confiável, capaz de preservar integralmente os dados recebidos da fonte.

### Análise da API do PNCP

Analisei a especificação OpenAPI do PNCP para entender a estrutura dos endpoints e das respostas.

Para esta primeira etapa, o escopo foi reduzido apenas para o recurso de **PCA**, utilizando como referência o endpoint de atualização:

`/api/consulta/v1/pca/atualizacao`

A configuração dessa fonte foi centralizada no arquivo:

`corpus_manifest.yaml`

Foram definidos inicialmente:

- `resource_type: pca`;
- endpoint do PCA;
- caminho dos registros dentro da resposta: `data`;
- identificador do registro: `idPcaPncp`.

### Implementação da camada RAW

Foi implementado o fluxo de ingestão para que cada registro recebido do PNCP seja armazenado preservando o payload original.

A arquitetura implementada ficou organizada da seguinte forma:

PNCP API  
↓  
PCA Collector  
↓  
Ingestion Run  
↓  
Sync Checkpoint  
↓  
Hash SHA-256  
↓  
Change Detector  
↓  
NEW / UPDATED / UNCHANGED  
↓  
RAW  
↓  
SQLite

O projeto utiliza **SQLite**, portanto a implementação foi adaptada ao banco já existente no repositório.

A camada RAW foi pensada como uma área de preservação dos dados originais. Sua responsabilidade é manter exatamente aquilo que foi recebido da fonte, permitindo que as etapas seguintes sejam refeitas sem necessidade de consultar novamente o PNCP.

### Controle das execuções de ingestão

Foi implementado o conceito de `ingestion_run`, responsável por registrar cada execução da coleta.

A execução permite acompanhar informações como:

- início e fim da coleta;
- status da execução;
- quantidade de páginas processadas;
- quantidade de registros recebidos;
- quantidade de registros novos;
- quantidade de registros atualizados;
- quantidade de registros sem alteração;
- quantidade de falhas.

Isso permite auditar posteriormente como determinada versão dos dados chegou ao sistema.

### Checkpoint de sincronização

Também foi implementado o controle de `sync_checkpoint`.

O checkpoint registra até qual ponto a fonte foi sincronizada com sucesso.

Uma regra importante definida foi:

**o checkpoint só pode avançar quando toda a execução terminar com sucesso.**


### Detecção de alterações

Foi implementado um mecanismo de hash utilizando **SHA-256**.

O objeto completo recebido da API é serializado de forma determinística e utilizado para gerar o hash.

Com isso, cada registro pode ser classificado em três estados:

- `NEW`: o registro ainda não existia;
- `UPDATED`: o registro já existia, mas o conteúdo foi alterado;
- `UNCHANGED`: o registro já existe e o conteúdo permanece igual.

No caso de `UNCHANGED`, uma nova cópia RAW não precisa ser criada.

No caso de `UPDATED`, uma nova versão é preservada sem substituir a versão anterior.

### Preservação do payload

Outro ponto importante da implementação foi garantir que o conteúdo recebido da API seja armazenado integralmente.

A regra definida foi:

**RAW = representação original recebida da fonte.**

Por exemplo, se um PCA possuir uma coleção `itens`, essa coleção permanece dentro do payload original.

Posteriormente será criada uma camada de normalização responsável por transformar esse conteúdo em entidades como:

- órgão;
- unidade administrativa;
- PCA;
- item do PCA.

### Paginação

Foi implementada a coleta página a página da resposta do PNCP.

O `PCACollector` utiliza o envelope paginado da API e processa os objetos presentes dentro de `data`.

Cada registro utiliza `idPcaPncp` como identificador externo para permitir comparação entre diferentes execuções.

### Observabilidade

Também foi implementada observabilidade estruturada para a ingestão.

Os logs registram informações como:

- `run_id`;
- `stage`;
- `resource_type`;
- página processada;
- quantidade de registros;
- contadores de `NEW`, `UPDATED` e `UNCHANGED`;
- tempo de resposta das requisições HTTP.

Os logs foram integrados à estrutura de observabilidade já existente no projeto, evitando a criação de um segundo sistema de logging.

### Integração com a arquitetura existente

Durante a implementação, procurei reutilizar a estrutura já existente no repositório.

Foram utilizados e adaptados principalmente os seguintes arquivos:

- `schema.py`;
- `fetch_corpus.py`;
- `ingest.py`;
- `obs.py`;
- `corpus_manifest.yaml`.

O `fetch_corpus.py` foi preservado como ponto de entrada do processo de coleta, evitando a criação de outro fluxo paralelo.

### Testes realizados

Foram implementados testes offline para validar a camada de ingestão.

Entre os cenários testados estão:

- PCA paginado utilizando o envelope `data`;
- preservação integral do payload recebido;
- validação do `idPcaPncp`;
- geração determinística do SHA-256;
- classificação `NEW`;
- classificação `UPDATED`;
- classificação `UNCHANGED`;
- versionamento dos registros RAW;
- checkpoint atualizado somente após sucesso;
- comportamento em falhas HTTP;
- comportamento em falhas de transporte.

### Limitação encontrada

A consulta real ao endpoint do PNCP não foi concluída durante a sessão porque a documentação/OpenAPI oficial apresentou timeout.

Por esse motivo, a lógica da aplicação foi validada utilizando testes offline e respostas simuladas compatíveis com a estrutura esperada da API.

O endpoint foi mantido isolado no `corpus_manifest.yaml`, permitindo que sua configuração seja alterada sem modificar a implementação caso seja identificada alguma variação na rota oficial.

### Uso de Inteligência Artificial

Utilizei o ChatGPT  como apoio durante o desenvolvimento.

O ChatGPT foi utilizado principalmente para:

- organizar o desenvolvimento da Base Agregada em etapas menores;
- discutir a arquitetura da camada RAW;
- analisar a relação entre coleta, RAW, normalização e processamento futuro;
- definir estratégias de versionamento e detecção de alterações;
- discutir o funcionamento de checkpoint e retomada;
- estruturar a futura utilização de eventos e Observer;
- analisar a modelagem inicial dos dados.

As sugestões geradas pelas ferramentas de IA foram revisadas e adaptadas antes de serem incorporadas ao projeto.

### Resultado do encontro

Ao final do encontro, foi concluída a primeira versão da camada:

**PNCP → RAW.**

O sistema já possui a estrutura necessária para:

- iniciar uma execução de ingestão;
- consultar uma fonte PNCP paginada;
- identificar cada PCA através de `idPcaPncp`;
- preservar o payload original;
- gerar hash do conteúdo;
- identificar registros novos, atualizados ou inalterados;
- manter histórico das alterações;
- registrar métricas da execução;
- controlar checkpoint;
- evitar avanço do checkpoint em caso de falha;
- registrar logs estruturados.

Essa etapa cria a base necessária para que os dados possam ser processados nas próximas fases sem perder a informação original recebida da fonte.

### Próximos passos

O próximo passo será finalizar a validação da camada RAW utilizando uma consulta real ao PNCP quando o serviço estiver disponível.

Também será revisado o armazenamento dos metadados da resposta da API, como:

- página de origem;
- posição do registro dentro da página;
- metadados do envelope paginado;
- parâmetros utilizados na consulta.

Após a conclusão dessa validação, o planejamento é iniciar a próxima etapa da arquitetura:

RAW  
↓  
eventos / observação  
↓  
processamento  
↓  
normalização

Nessa etapa será estudada a implementação de um mecanismo de eventos para que novos registros ou atualizações na camada RAW possam disparar automaticamente os próximos processamentos.

Posteriormente será iniciada a normalização específica do PCA, distribuindo as informações RAW para estruturas como:

- órgão;
- unidade administrativa;
- PCA;
- item do PCA.

