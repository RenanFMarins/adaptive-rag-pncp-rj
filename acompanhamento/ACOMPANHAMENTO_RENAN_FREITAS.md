# Acompanhamento - grande desafio - contrataçoes do estado do Rio de janeiro

**Integrante 1:** José Renan Freita Marins - [@RenanFMarins](https://github.com/RenanFMarins)



**Repositório:** `rag-grande-desafio-grupo03-contratacoes-publicas`

---

## Encontro 1 - 2026-09-16

### Relato individual - José Renan freitas Marins (4h)

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

---

## Encontro 3 - 2026-09-21

### Relato individual — José Renan Freitas Marins (4h)

Hoje dei continuidade à implementação da **Base Agregada**, avançando da
coleta inicial do Plano de Contratações Anual para a segunda fonte
definida pelo professor: os **valores homologados por item**.

O primeiro trabalho foi compreender a diferença entre os itens existentes no
PCA e os itens de uma contratação. Apesar de ambos utilizarem o termo "item",
eles representam etapas diferentes do processo:

- o item do PCA registra o planejamento da futura contratação;
- o item da contratação representa aquilo que foi efetivamente licitado;
- o resultado do item registra quantidade e valores homologados, fornecedor e
  situação do resultado.

Foi confirmado que campos como `valorTotal` e `quantidadeEstimada`, presentes
no PCA, não podem ser interpretados como valores homologados. Os valores
homologados são obtidos por um endpoint específico do PNCP e possuem campos
como:

- `quantidadeHomologada`;
- `valorUnitarioHomologado`;
- `valorTotalHomologado`;
- `sequencialResultado`;
- `nomeRazaoSocialFornecedor`;
- `dataResultado`;
- `situacaoCompraItemResultadoNome`.

### Coleta hierárquica dos resultados

Foi implementado o `ItemResultCollector`, responsável por navegar pela
estrutura hierárquica da API:

```text
contratação
  → itens paginados
    → item com temResultado=true
      → resultados homologados do item
```

O coletor utiliza como identificadores:

- CNPJ do órgão;
- ano da compra;
- sequencial da compra;
- número do item.

### Validação com dados reais

Foi executada uma coleta real e controlada de uma contratação do Estado do
Rio de Janeiro. A API retornou:

- 42 itens da contratação;
- 38 itens com resultado homologado;
- 4 itens sem resultado;
- total homologado de R$ 317.227,64.

O total calculado a partir dos payloads RAW coincidiu com o valor total
homologado apresentado no portal do PNCP.

A carga foi executada novamente para validar a idempotência. Na segunda
execução, os 38 registros foram classificados como `UNCHANGED`, sem criação
de duplicatas.

Os resultados foram armazenados na tabela `raw_asset` utilizando:

```text
resource_type = resultado_item
natureza = agregada
processing_status = RAW
```

O JSON original continua preservado na coluna `payload`, sem transformação
dos nomes ou dos valores fornecidos pelo PNCP.

### Relação com a Base Estruturada

Durante a análise foi identificado que a Base Agregada depende de parte da
Base Estruturada para descobrir corretamente as contratações que deverão ter
seus resultados consultados.

A contratação estruturada fornece principalmente:

- `orgaoEntidade.cnpj`;
- `anoCompra`;
- `sequencialCompra`;
- `numeroControlePNCP`;
- modalidade, objeto, datas e situação da contratação.

Foi adicionada ao manifesto uma fonte piloto para contratações publicadas em
um período fechado e foi implementada a ligação para que o coletor agregado
priorize automaticamente os alvos existentes na RAW estruturada.

Quando existirem registros com `resource_type = contratacao`, o sistema
extrairá CNPJ, ano e sequencial desses payloads e os utilizará para buscar os
itens e resultados homologados. Um alvo manual foi mantido temporariamente
como fallback para permitir a validação da integração.

A consulta paginada de contratações apresentou timeout de leitura durante a
validação real. A falha foi registrada em `ingestion_run` com status `FAILED`,
sem avançar o checkpoint e sem afetar os resultados já armazenados.

### Modelagem de dados

Também foi estudada a modelagem futura da camada normalizada. Foram
identificadas como principais entidades:

- órgão;
- unidade administrativa;
- PCA;
- item do PCA;
- contratação;
- item da contratação;
- resultado do item;
- fornecedor;
- contrato ou empenho.

### Testes e organização do repositório

Foram adicionados testes para validar:

- paginação dos itens de uma contratação;
- preservação do payload de resultado;
- validação da chave composta;
- rejeição de CNPJ ou identificadores inválidos;
- substituição do alvo manual por contratações vindas da RAW;
- recuperação somente da versão mais recente de cada contratação;
- idempotência e versionamento.

Ao final, a suíte ficou com 23 testes offline executados com sucesso.

O banco local `app.db` também foi adicionado ao `.gitignore` e retirado do
controle de versão da branch, evitando o envio de dados coletados e arquivos
binários para o repositório.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:

- interpretar a diferença entre a documentação OpenAPI 3 e os endpoints
  operacionais `/v1`;
- discutir a modelagem relacional das entidades;
- revisar as regras de paginação, idempotência e versionamento;
- elaborar uma especificação visual da futura modelagem de dados.

### Resultado do encontro

Ao final do encontro, a Base Agregada passou a possuir duas fontes RAW
validadas conceitualmente:

```text
PCA → planejamento
resultado_item → homologação
```

A coleta real de resultados homologados foi concluída, paginada e validada
quanto à idempotência. Também foi preparada a integração com a Base
Estruturada para descoberta automática das contratações.

### Próximos passos

Os próximos passos serão:

- repetir a carga estruturada quando o endpoint de contratações estiver
  respondendo normalmente;
- substituir definitivamente o alvo piloto pelos registros estruturados;
- definir o recorte completo de órgãos, modalidades e período do RJ;
- implementar retry limitado para falhas transitórias;
- evoluir da RAW para as tabelas normalizadas;
- implementar inventário e versionamento imutável do corpus;
- manter os testes de contrato e integração separados da suíte offline.

---

## Encontro 4 - 2026-09-23

### Relato individual — José Renan Freitas Marins (4h)

A primeira etapa da camada RAW das bases Estruturada e Agregada do PNCP. O objetivo
foi completar o encadeamento entre contratação, item da contratação e resultado homologado, garantindo que os dados originais continuassem preservados antes do início da normalização.

O fluxo implementado e validado ficou organizado da seguinte forma:

```text
contratação RAW
  → item da contratação RAW
    → resultado homologado RAW
```

### Coleta das contratações do Rio de Janeiro

Foi ajustada a fonte piloto de contratações para realizar a consulta por
atualização, mantendo o filtro `uf=RJ` e retirando o CNPJ fixo que limitava a
coleta a um único órgão.

### Implementação de `contratacao_item`

Foi implementado o coletor responsável por utilizar as contratações já
existentes na RAW para consultar seus respectivos itens no PNCP.

O JSON devolvido pela API é armazenado sem inclusão, remoção ou alteração de
campos. Para manter o relacionamento com a contratação-pai sem modificar o
payload, foi adotado um identificador externo composto:

```text
numeroControlePNCP|numeroItem
```

Essa estratégia permite distinguir corretamente itens com o mesmo número em
contratações diferentes e fornece a chave necessária para a futura camada
normalizada.

### Refatoração da coleta de resultados homologados

O coletor de resultados foi refatorado para utilizar exclusivamente os itens
já existentes na RAW. Antes da alteração, o fluxo consultava novamente o
endpoint de listagem de itens para descobrir quais possuíam resultado.

Somente itens com indicação de resultado geram uma nova chamada ao PNCP. Os
itens com `temResultado=false` são processados localmente, sem requisição
desnecessária.

A execução real processou os 359 itens e coletou 26 resultados novos, sem
falhas. Todos os 26 resultados foram conferidos e estavam ligados aos seus
respectivos itens RAW. O banco de debug passou a possuir 64 resultados no
total, considerando os 38 registros da coleta piloto anterior.

Os payloads incluem informações necessárias à Base Agregada, como:

- `quantidadeHomologada`;
- `valorUnitarioHomologado`;
- `valorTotalHomologado`;
- `sequencialResultado`;
- fornecedor;
- situação e data do resultado.

### Correção dos checkpoints por alvo

Foi identificado que um alvo sem registros não avançava o checkpoint, pois o
controle dependia da existência de um payload para reconhecer o processamento.
Também existia o risco de uma execução sem novos alvos substituir o checkpoint
anterior por zero.

Na validação real, o checkpoint de resultados chegou ao alvo 359. Em seguida,
foi executado o comando de atualização novamente. A nova execução recebeu zero
registros e manteve corretamente o checkpoint em 359.

### Retry e tratamento de respostas da API

Foi implementado retry configurável para falhas transitórias do PNCP. O
cliente passa a repetir requisições nos seguintes casos:

- HTTP 429;
- HTTP 500;
- HTTP 502;
- HTTP 503;
- HTTP 504;
- timeout;
- falhas temporárias de conexão.

A espera entre tentativas utiliza crescimento progressivo. Também foi
adicionado o tratamento de HTTP 204, que agora é interpretado como uma
resposta válida sem registros, em vez de erro de JSON.

### Correção da contagem de falhas

Foi corrigida a contabilização de falhas em `ingestion_run`. Anteriormente, o
log indicava a falha, mas `records_failed` poderia permanecer com valor zero.

Agora uma execução interrompida registra corretamente:

- `status = FAILED`;
- `records_failed = 1`;
- mensagem do erro;
- quantidade de registros recebidos antes da falha;
- páginas ou alvos alcançados durante a execução.

O checkpoint continua avançando somente quando o run termina com sucesso.

### Testes

Foram adicionados e atualizados testes para validar:

- preservação do JSON original;
- identificador composto com a contratação-pai;
- uso dos itens RAW pelo coletor de resultados;
- ausência de chamada HTTP para `temResultado=false`;
- checkpoint de alvos sem registros;
- preservação do checkpoint quando não existem novos alvos;
- retry após erro HTTP transitório;
- tratamento de HTTP 204;
- persistência correta de `records_failed`;
- ligação de resultados ao item correspondente.

Ao final do encontro, a suíte completa ficou com 33 testes executados com
sucesso.

### Análise da relação entre PCA e contratação

Também foi analisada a futura ligação entre os itens do PCA e os itens das
contratações. Foi confirmado que os dados RAW recebidos de contratação e
`contratacao_item` não possuem uma chave direta para `idPcaPncp` ou
`numeroItemPca`.

Por esse motivo, a futura tabela `PCA_CONTRATACAO_LINK` deverá representar uma
associação construída na camada normalizada. Ela poderá registrar o método de
associação e seu nível de confiança, pois um item planejado pode originar
vários itens de contratação e vários itens planejados também podem ser
consolidados em uma única contratação.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:

- revisar a arquitetura da camada RAW;
- analisar os campos reais retornados pelo PNCP;
- discutir a modelagem entre PCA, contratação, item e resultado;
- revisar a estratégia de retry e HTTP 204;
- documentar o fluxo de ingestão e depuração.

As sugestões foram validadas por meio de testes offline, consultas somente
leitura ao SQLite e execuções reais controladas contra a API pública do PNCP.

### Resultado do encontro

Ao final do encontro, foi concluído o fluxo RAW previsto para as contratações,
seus itens e resultados homologados:

```text
10 contratações
  → 359 itens de contratação
    → 26 resultados novos ligados aos itens RAW
```

A coleta passou a possuir identificação do pai sem alteração do JSON, retry,
tratamento de ausência de conteúdo, checkpoints por alvo, contagem correta de
falhas e testes automatizados.

### Próximos passos

Os próximos passos serão:

- repetir a coleta do PCA, que ainda não possui registros no banco de debug
  devido ao timeout da tentativa anterior;
- analisar os campos reais dos itens do PCA;
- implementar as tabelas normalizadas de contratação, item e resultado;
- normalizar órgão, unidade administrativa e fornecedor;
- definir regras auditáveis para possíveis associações entre PCA e
  contratação;
- manter a referência de cada registro normalizado ao respectivo
  `source_raw_asset_id`;
- ampliar gradualmente o período, as modalidades e os órgãos consultados no
  Estado do Rio de Janeiro.
## Encontro 5 - 2026-09-25

### Relato individual — José Renan Freitas Marins (4h)

Hoje concentrei meu trabalho na definição da estratégia de expansão da coleta das bases Estruturada e Agregada do PNCP para contemplar o período de três anos solicitado no projeto.

A partir da arquitetura e da camada RAW já implementadas, revisei a ordem das próximas etapas para evitar misturar coleta. Foi definido que o fluxo deverá continuar respeitando a sequência:

PNCP
→ coleta
→ RAW_ASSET
→ validação
→ normalização
→ tabelas analíticas.

Com isso, os dados recebidos da API deverão ser inicialmente armazenados integralmente na camada RAW, preservando o JSON original, e somente depois serão distribuídos para entidades como ORGAO, UNIDADE, CONTRATACAO, PCA, PCA_ITEM e demais tabelas normalizadas.

Também foi definido o recorte temporal inicial do corpus, utilizando os anos de 2023, 2024 e 2025. Para facilitar checkpoint, auditoria, retomada de execução e tratamento de falhas, a coleta será dividida por trimestre:

2023:
T1 — janeiro a março;
T2 — abril a junho;
T3 — julho a setembro;
T4 — outubro a dezembro.

2024:
T1, T2, T3 e T4.

2025:
T1, T2, T3 e T4.

Dessa forma, o corpus poderá ser construído progressivamente em 12 janelas independentes, permitindo identificar exatamente qual período, modalidade ou página apresentou algum problema sem necessidade de repetir toda a coleta.

Inicialmente, a ideia era iniciar diretamente pela coleta de PCA e, a partir dos itens planejados, localizar as contratações relacionadas. Durante a análise, foi identificado que o endpoint de PCA permite filtros como CNPJ e código da unidade, porém não possui filtro direto por UF. Essa limitação dificulta uma coleta específica do Estado do Rio de Janeiro caso ainda não exista uma lista prévia de CNPJs dos órgãos pertencentes ao estado.

A estratégia foi reorganizada. Como a API de contratações permite utilizar diretamente o filtro `uf=RJ` e retorna dados do órgão e da unidade administrativa, foi definido que a coleta deverá começar pelas contratações do Rio de Janeiro.

O novo fluxo planejado ficou:
Contratações com UF = RJ
→ RAW_ASSET
→ identificação de órgãos e unidades
→ lista de CNPJs observados no RJ
→ consulta de PCA por CNPJ
→ PCA RAW.

Essa abordagem evita realizar uma coleta nacional de PCA apenas para depois identificar quais registros pertencem ao Rio de Janeiro.

Outro ponto importante definido foi que, mesmo que as contratações já tragam informações de órgão, unidade, município, UF e código IBGE, esses dados não serão imediatamente distribuídos para as tabelas normalizadas.
O fluxo deverá permanecer:
API PNCP
→ RAW_ASSET.

Somente em uma etapa posterior será realizado:
RAW_ASSET
→ ORGAO
→ UNIDADE
→ CONTRATACAO.

Essa decisão mantém a rastreabilidade dos dados, preserva o conteúdo original recebido da API e permite reprocessar a normalização futuramente sem precisar consultar novamente o PNCP.

Também foi planejada a primeira etapa de coleta das contratações. O endpoint utilizado será o de publicação de contratações, com filtro para o Estado do Rio de Janeiro e recorte trimestral.
O fluxo de execução será organizado por:

ano
+ trimestre
+ modalidade
+ página.

Por exemplo:

2023-T1
→ modalidade
→ página 1
→ página 2
→ ...
→ RAW_ASSET.

Como o endpoint exige `codigoModalidadeContratacao`, a coleta completa deverá posteriormente percorrer as modalidades definidas para o corpus.

Antes de realizar uma coleta extensa, foi decidido executar um smoke test controlado utilizando:
UF = RJ;
ano = 2023;
trimestre = T1;
uma modalidade válida;
página = 1;
10 registros.

O objetivo desse primeiro teste será comprovar o fluxo real:
PNCP
→ response["data"]
→ numeroControlePNCP
→ SHA-256
→ NEW / UPDATED / UNCHANGED
→ RAW_ASSET.

Cada contratação deverá ser armazenada com:

resource_type = contratacao
external_id = numeroControlePNCP
payload = objeto completo retornado pela API.
O payload deverá permanecer integralmente preservado, sem renomear, remover ou transformar campos.
A lógica de versionamento já implementada continuará sendo reutilizada:
external_id inexistente
→ NEW;
external_id existente com hash diferente
→ UPDATED;
external_id existente com mesmo hash
→ UNCHANGED.

Também foi definido que a infraestrutura existente deverá ser reutilizada para essa nova fonte. Não deverá ser criada uma segunda camada de ingestão específica para contratações. O mesmo fluxo já utilizado para PCA deverá ser generalizado para trabalhar com múltiplos tipos de recursos, como:
pca;
contratacao;
contratacao_item;
resultado_item.

A infraestrutura existente deverá continuar utilizando:
raw_asset;
ingestion_run;
sync_checkpoint;
fetch_corpus.py;
ingest.py;
schema.py;
obs.py;
hashing SHA-256;
controle de NEW, UPDATED e UNCHANGED.

Outro ponto analisado foi a estratégia de checkpoint. Como a coleta será dividida por trimestre, modalidade e página, o checkpoint deverá distinguir corretamente cada contexto de execução para evitar que uma coleta interfira em outra.
Por exemplo, o checkpoint de:

2023-T1 / modalidade A
não deverá interferir em:

2023-T1 / modalidade B
nem em:

2023-T2 / modalidade A.

Após a coleta RAW das contratações, a próxima etapa será utilizar os dados de `orgaoEntidade` e `unidadeOrgao` para popular as tabelas ORGAO e UNIDADE.
A ideia é obter uma lista de CNPJs observados nas contratações do Estado do Rio de Janeiro e utilizar esses CNPJs como filtro para a futura coleta de PCA.

O fluxo futuro deverá seguir:
RAW contratacao
→ ORGAO
→ UNIDADE
→ CNPJs observados
→ PCA por CNPJ
→ PCA 2023, 2024 e 2025.

Também foi reforçado que essa lista deverá ser tratada como “órgãos do RJ observados no corpus de contratações”, e não necessariamente como uma lista completa de todos os órgãos existentes no estado.

Posteriormente, após a coleta dos PCA, será possível construir o fluxo entre planejamento e execução:

PCA
→ PCA_ITEM
→ PCA_CONTRATACAO_LINK
→ CONTRATACAO_ITEM
→ RESULTADO_ITEM.

A relação entre PCA e contratação não deverá ser assumida como direta, pois os itens planejados e os itens efetivamente contratados são entidades diferentes. A futura associação poderá utilizar critérios como CNPJ, período, unidade administrativa, classificação, descrição dos itens, similaridade textual ou semântica e nível de confiança.



Utilizei o ChatGPT como apoio para revisar a estratégia de expansão do corpus, analisar a ordem correta entre coleta RAW e normalização, discutir a utilização de contratações para identificar órgãos do RJ, analisar as diferenças entre os filtros disponíveis nos endpoints de PCA e contratação, estruturar a coleta dos três anos por trimestre, definir a estratégia de checkpoint por período, modalidade e página e revisar a relação entre PCA, contratação, item e resultado homologado.

Ao final do encontro, foi definida a estratégia de expansão do corpus para o período de três anos, priorizando primeiro a coleta de contratações do Estado do Rio de Janeiro na camada RAW.
O fluxo consolidado ficou:

Contratações RJ — 2023 a 2025
→ coleta por trimestre
→ RAW_ASSET
→ validação e versionamento
→ ORGAO / UNIDADE
→ CNPJs observados
→ PCA 2023 a 2025
→ PCA_ITEM
→ associação futura com contratações.

Como próximo passo, será realizado o primeiro smoke test de contratação utilizando 2023-T1, `uf=RJ`, uma modalidade válida e uma página pequena. Após a validação da persistência RAW, idempotência, `ingestion_run` e `sync_checkpoint`, a coleta poderá ser expandida gradualmente para todas as páginas e demais trimestres de 2023, 2024 e 2025.


---

## Encontro 6 - 2026-09-28

### Relato individual — José Renan Freitas Marins (4h)

Neste encontro, concentrei o trabalho na ampliação, auditoria e distribuição
da camada RAW das bases Estruturada e Agregada do PNCP. O objetivo foi sair do
recorte piloto e consolidar um conjunto reproduzível de dados do Estado do Rio
de Janeiro, preservando os JSONs originais e mantendo rastreabilidade por
execução, fonte e checkpoint.

### Ampliação das contratações do Rio de Janeiro

Foi concluída a coleta das contratações publicadas no RJ entre 1º de janeiro
de 2023 e 26 de setembro de 2026, contemplando as 14 modalidades previstas
pela API do PNCP.

O primeiro trimestre de 2023 resultou em 2.024 contratações. Para o período de
1º de abril de 2023 até a data de corte, foram preservadas outras 174.457
contratações. Com isso, a camada RAW passou a possuir 176.481 contratações
únicas nesse recorte.

### Complementação do primeiro trimestre de 2023

Para formar um recorte fechado e compartilhável, foram concluídas e validadas
as fontes dependentes das contratações publicadas entre janeiro e março de
2023:

- 2.024 contratações;
- 4.804 itens de contratação;
- 3.669 resultados homologados;
- 1.378 contratos;
- consulta de empenhos para os 1.378 contratos.

A consulta de empenhos terminou com `SUCCESS`, mas o PNCP não retornou
registros para os contratos desse recorte. Essa ausência foi mantida de forma
auditável por meio de `ingestion_run` e `sync_checkpoint`.

### Coleta completa do PCA de 2023

Também foi concluída a descoberta dos PCAs de 2023 para os órgãos encontrados
nas contratações iniciais do RJ.

Foram preservados:

- 195 planos de contratação;
- 49.063 itens dentro dos JSONs dos planos;
- 61 órgãos consultados com checkpoint concluído.

Os itens de PCA permaneceram aninhados no payload original, respeitando a
responsabilidade da RAW. A futura tabela `pca_item` será produzida na camada
normalizada.

### Atas de Registro de Preços

Foi realizada uma coleta inicial de atas vigentes entre 2023 e setembro de
2026 para 233 unidades administrativas conhecidas no recorte inicial.

A execução recebeu 65.671 ocorrências e preservou 36.597 atas únicas. As
29.074 ocorrências restantes eram repetições identificadas pelo número de
controle da ata.

Após a coleta completa das contratações, foi identificado um universo de pelo
menos 2.097 unidades. Por isso, as atas atuais ainda representam um recorte
parcial. Foi decidido não incluí-las no snapshot trimestral e realizar
posteriormente uma coleta específica com todas as unidades descobertas.


### Snapshot RAW e distribuição para a equipe

Foi criado um snapshot imutável do primeiro trimestre de 2023, excluindo as
atas e incluindo o PCA anual como contexto de planejamento.

O snapshot foi validado com:

- `PRAGMA integrity_check = ok`;
- verificação de chaves estrangeiras;
- restauração completa do dump SQL;
- conferência das contagens;
- hashes SHA-256.

Foram gerados:

- banco SQLite compactado;
- dump SQL compactado;
- inventário CSV;
- arquivo de hashes.

Os artefatos foram publicados em uma Release privada do GitHub com a tag
`dados-raw-rj-2023-t1-v1`. A pasta local de exportações foi incluída no
`.gitignore` para evitar o versionamento acidental dos bancos.

### Qualidade e testes

A suíte automatizada passou a possuir 69 testes executados com sucesso. O
`corpus_manifest.yaml` foi validado com 27 fontes e nenhum erro.

Também foram reforçados:

- retry para falhas transitórias;
- tratamento de HTTP 204 e 404 conforme o endpoint;
- checkpoints por página ou alvo;
- coleta paralela com entrega ordenada;
- preservação do payload original;
- detecção de registros novos, atualizados e inalterados;
- auditoria das execuções com falha.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:

- analisar os endpoints e os payloads reais do PNCP;
- revisar a estratégia de coleta por trimestre e modalidade;
- diagnosticar timeouts e limites da API;
- revisar a modelagem entre contratação, item, resultado, contrato e PCA;
- estruturar os testes e as verificações de integridade;
- organizar o snapshot RAW e sua distribuição por GitHub Release;

### Resultado do encontro

Ao final do encontro, foi consolidado um recorte RAW auditável do primeiro
trimestre de 2023 e publicada uma versão imutável para compartilhamento com a
equipe.

### Próximos passos

Os próximos passos serão:

- retomar a coleta de `contratacao_item` a partir do checkpoint salvo;
- coletar `resultado_item` para os novos itens;
- coletar contratos do período complementar;
- consultar empenhos dos novos contratos;
- ampliar os PCAs para os anos de 2024, 2025 e 2026;
- refazer a coleta de atas com todas as unidades descobertas;
- iniciar a camada normalizada a partir do snapshot do primeiro trimestre;
- criar snapshots e Releases separados para os próximos trimestres.


---

## Encontro 8 - 2026-10-02

### Relato individual — José Renan Freitas Marins (4h)

Neste encontro, concentrei o trabalho na atualização do repositório e na
auditoria técnica dos dados necessários para preparar o snapshot RAW do segundo
trimestre de 2023. O objetivo foi confirmar o estado das branches, medir a
cobertura real do período de 1º de abril a 30 de junho de 2023 e identificar o
que ainda precisa ser coletado antes da próxima Release.

### Situação dos resultados homologados

A coleta histórica de `resultado_item` foi interrompida com checkpoint no alvo
61.918 de 540.791 itens, equivalente a 11,45% da fila histórica. Não havia
processo de coleta ativo durante a auditoria, embora a execução permanecesse
registrada como `RUNNING`.

Para o segundo trimestre, já foram preservados 2.460 registros de resultado,
pertencentes a 2.437 itens diferentes. Considerando os 10.122 itens marcados
como possuindo resultado, a cobertura atual é de aproximadamente 24,08%,
restando 7.685 itens a consultar.

### Recursos ainda necessários

Foi consolidado o seguinte diagnóstico para a futura Release do segundo
trimestre:

- contratações: coleta concluída;
- itens de contratação: coleta concluída;
- resultados homologados: coleta parcial;
- contratos formais: ainda não coletados para o segundo trimestre;
- empenhos: dependem da futura coleta dos contratos do segundo trimestre;
- PCA: já disponível como contexto anual de 2023;
- atas de registro de preços: continuam fora do snapshot trimestral, pois a
  coleta existente não cobre todas as unidades descobertas posteriormente.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:
- elaborar consultas de auditoria sobre o banco SQLite;
- calcular a cobertura do segundo trimestre por recurso e por mês;
- verificar integridade, duplicidades e relacionamentos entre contratações,
  itens e resultados;
- organizar a ordem segura das próximas coletas e da futura Release.

### Resultado do encontro

Ao final do encontro, a branch principal foi confirmada como sincronizada com
o GitHub e foi produzido um diagnóstico objetivo do segundo trimestre de 2023.
As contratações e seus itens estão completos, mas os resultados homologados
ainda precisam ser concluídos. Também será necessário coletar contratos e
empenhos do período caso a próxima Release mantenha o mesmo escopo do snapshot
do primeiro trimestre.

### Próximos passos

Os próximos passos definidos foram:

- retornar para a branch `feature/agregate-pncp-raw` antes de retomar a coleta;
- continuar `pncp_resultado_item_rj_2023_t2_ate_hoje` a partir do checkpoint;
- concluir e auditar os resultados homologados do segundo trimestre;
- configurar e executar a coleta de contratos entre 01/04/2023 e 30/06/2023;
- coletar os empenhos vinculados aos contratos encontrados;
- resolver de forma auditável a execução interrompida que permaneceu como
  `RUNNING`;
- gerar um snapshot filtrado e reproduzível do segundo trimestre;
- publicar os artefatos com inventário e hashes SHA-256 em uma nova Release.


---

## Encontro 9 - 2026-10-05

### Relato individual — José Renan Freitas Marins (4h)

Neste encontro, concentrei o trabalho no fechamento de lacunas da camada RAW
do segundo trimestre de 2023 e na preparação de uma coleta independente das
atas de registro de preços do primeiro trimestre. O objetivo foi consolidar
os dados agregados que dependem de contratações e organizar uma atividade que
possa ser executada por outro integrante sem perder rastreabilidade ou alterar
o banco original publicado na Release.

### Fechamento dos resultados homologados do segundo trimestre

Foi executada uma coleta direcionada para os itens do segundo trimestre que
ainda não possuíam `resultado_item` na camada RAW. Os 101 alvos pendentes
foram consultados e produziram 102 novos registros, pois um dos itens possuía
mais de um resultado.

Após a execução, a auditoria confirmou:

- 10.122 itens do segundo trimestre marcados como possuindo resultado;
- 10.122 itens com resultado coletado;
- zero itens pendentes nesse recorte;
- cobertura de 100% dos resultados esperados para o T2.

### Ampliação do PCA para os novos órgãos do T2

Também foi executada a coleta de PCA para 49 novos órgãos identificados nas
contratações do segundo trimestre.

O processamento foi concluído com sucesso para todos os alvos:

- 49 órgãos consultados;
- 12 órgãos com PCA retornado pelo PNCP;
- 37 órgãos sem PCA disponível, tratados corretamente como resposta vazia;
- 57 novos planos preservados na camada RAW;
- 9.506 itens mantidos dentro dos payloads originais dos planos;
- 252 PCAs distintos no conjunto acumulado.

### Preparação da coleta de atas de registro de preços

Foi criada e publicada a branch
`feature/coleta-atas-registro-precos` para permitir que outro integrante
execute a coleta das atas sem depender do banco principal de desenvolvimento.

Inicialmente, foi preparado um fluxo ampliado capaz de descobrir as unidades
do RJ a partir das contratações RAW. Para tornar a execução reproduzível,
foram definidos:

- seleção determinística de órgãos e unidades administrativas;
- consulta ao endpoint `/api/consulta/v1/atas`;
- preservação integral do JSON recebido;
- `resource_type = ata_registro_preco`;
- checkpoints por unidade e janela temporal;
- retomada segura com o comando `update`;
- logs JSONL específicos para acompanhamento da coleta.

Para a atividade imediata, o escopo foi reduzido corretamente ao primeiro
trimestre de 2023. Foi criado o perfil `t1-2023`, que utiliza:

- data inicial em 01/01/2023;
- data final em 31/03/2023;
- as 233 unidades do RJ encontradas nas contratações do banco T1;
- checkpoint independente `pncp_atas_rj_2023_t1`;
- uma janela trimestral por unidade, totalizando 233 alvos.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:

- organizar a coleta de PCA para os novos órgãos;
- revisar o isolamento dos checkpoints por período;
- estruturar a coleta delegada das atas;
- revisar os comandos de restauração, execução e monitoramento;
- documentar o procedimento de entrega para outro integrante.

### Resultado do encontro

Ao final do encontro, os resultados homologados do segundo trimestre estavam
com cobertura completa e os PCAs dos novos órgãos haviam sido processados. A
branch de atas também ficou publicada, testada e documentada para que outro
integrante possa adicionar ao banco da Release as atas vigentes no primeiro
trimestre de 2023.

### Próximos passos

Os próximos passos definidos foram:

- acompanhar a execução das 233 consultas de atas do primeiro trimestre;
- auditar checkpoint, falhas e quantidade de atas distintas ao final;
- validar a integridade do banco atualizado recebido do colega;
- gerar um novo artefato compactado com as atas acrescentadas;
- concluir a coleta de contratos e empenhos necessários ao snapshot T2;
- gerar o inventário e a Release do segundo trimestre;
- iniciar a normalização dos dados preservados na camada RAW.
- 
## Encontro 10 - 2026-10-09

### Relato individual — José Renan Freitas Marins (4h)

Neste encontro, concentrei meu trabalho na evolução da arquitetura de ingestão da camada RAW das bases Estruturada e Agregada do Portal Nacional de Contratações Públicas (PNCP), com foco na preparação do sistema para realizar coletas incrementais e identificar alterações em registros históricos sem comprometer os dados já armazenados.

Inicialmente, foi realizada uma auditoria técnica da implementação existente, identificando limitações no mecanismo de identificação das entidades, no versionamento dos registros e no controle de checkpoints. A partir dessa análise, foi estruturada uma abordagem para separar a coleta histórica da futura coleta incremental, preservando a compatibilidade com o fluxo atual do projeto.

Uma das principais melhorias foi a correção da identidade canônica dos registros RAW. Anteriormente, a identificação dependia da fonte de coleta, o que poderia fazer uma mesma contratação aparecer como uma nova entidade ao ser encontrada por outro coletor. A identificação passou a considerar a combinação `base_id`, `resource_type` e `external_id`, permitindo reconhecer o mesmo registro independentemente da origem da execução.

Também foi aprimorado o mecanismo de versionamento, mantendo a preservação imutável dos payloads originais e a detecção de alterações por SHA-256. O sistema passou a considerar a versão corrente do registro, evitando que informações antigas recebidas fora de ordem substituam indevidamente versões mais recentes.

Para validar essas alterações, foi utilizada uma cópia isolada do banco SQLite referente ao primeiro trimestre de 2023, anteriormente disponibilizado em uma Release do GitHub. Foi aplicada exclusivamente nessa cópia uma migração responsável pela criação de um índice para otimizar as consultas por identidade canônica.

Outra atividade importante foi a reformulação da arquitetura de checkpoints. O modelo anterior utilizava posições numéricas em listas dinâmicas, o que poderia ocasionar a perda de alvos quando novos registros fossem inseridos durante o processo de coleta.

Para solucionar esse problema, foram implementadas quatro novas estruturas:

- `sync_job`: identificação da configuração e do tipo de coleta;
- `sync_window`: controle das janelas temporais de processamento;
- `sync_target_progress`: acompanhamento individual dos alvos por identidade estável;
- `sync_watermark`: registro do progresso temporal confirmado.

O novo modelo também incorporou controle de concorrência por lease, recuperação de execuções interrompidas, separação entre checkpoints históricos e incrementais e confirmação do progresso somente após a persistência bem-sucedida dos registros RAW.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para analisar os problemas identificados na arquitetura de ingestão, estruturar as etapas de correção, discutir estratégias de versionamento, planejar a separação entre coleta histórica e incremental e elaborar instruções técnicas para implementação e validação.

As alterações foram acompanhadas por verificações de integridade e testes, mantendo a preocupação com a preservação dos dados históricos.

### Resultado do encontro

Ao final do encontro, foram concluídas e validadas as melhorias de identidade canônica, versionamento RAW e controle de checkpoints v2. A migração do índice foi testada com sucesso no snapshot do primeiro trimestre de 2023, preservando todos os registros originais.

A arquitetura passou a contar com mecanismos mais seguros para identificar atualizações, acompanhar janelas de processamento, controlar execuções concorrentes e retomar coletas interrompidas.

Nenhum banco operacional foi modificado durante essas validações, e a coleta histórica existente permaneceu preservada.

### Próximos passos

Os próximos passos serão:

- implementar o novo ponto de entrada `fetch_incremental.py`, separado do coletor histórico;
- integrar o novo coletor aos checkpoints v2;
- implementar e validar a renovação de lease durante execuções prolongadas;
- realizar simulações offline de atualizações e retomadas;
- analisar as datas de atualização fornecidas pelo PNCP;
- preparar a futura integração dos endpoints incrementais para PCA, contratações, contratos e atas;
- definir estratégias de reconciliação para itens, resultados homologados e demais recursos dependentes;
- manter a preservação e a rastreabilidade dos dados RAW antes do início da normalização.


## Encontro 11 - 2026-10-14

### Relato individual — José Renan Freitas Marins (4h)

Neste encontro, concentrei as atividades na análise e no planejamento da evolução da ingestão incremental dos dados do Portal Nacional de Contratações Públicas (PNCP). O objetivo foi avaliar a segurança da arquitetura implementada, identificar possíveis problemas de integridade e recuperação de falhas e organizar as correções necessárias antes de iniciar a integração com os endpoints reais do PNCP.

### Auditoria da arquitetura de ingestão incremental

Foi realizada uma análise técnica da branch `feature/ingestao-incremental-pncp`, verificando os componentes responsáveis pelo versionamento dos registros RAW, controle de checkpoints, watermark, concorrência, paginação e tratamento de atualizações.

A auditoria identificou problemas importantes:

- possibilidade de gravações concorrentes não atômicas na camada RAW;
- risco de um processo continuar gravando após perder o controle do lease;
- avanço do watermark mesmo com janelas anteriores pendentes;
- tratamento inadequado de timestamps inválidos ou atualizações fora de ordem;
- possibilidade de conclusão de janelas sem garantir todos os alvos esperados;
- riscos de perda de registros durante a retomada de páginas;
- geração de versões artificiais em registros PCA distribuídos entre diferentes páginas.

Esses problemas foram classificados de acordo com sua gravidade e impacto na confiabilidade da ingestão.

### Validação dos testes e integridade do projeto

Também foi realizada a verificação do estado atual do repositório e da suíte automatizada de testes.

Os resultados apresentados foram:

- 117 testes executados e aprovados;
- nenhuma falha ou teste ignorado;
- validação de sintaxe com `compileall`;
- verificação de integridade das alterações com `git diff --check`;
- nenhuma modificação nos bancos operacionais;
- nenhuma chamada HTTP real durante a auditoria.

Apesar dos testes aprovados, a análise demonstrou a necessidade de ampliar a cobertura de cenários relacionados à concorrência, consistência temporal e recuperação de falhas.

### Organização do backlog e planejamento das correções

Com base nos problemas identificados, foi elaborado um backlog técnico contendo 20 tarefas, classificadas por prioridade, dependências e esforço estimado.

As correções críticas foram concentradas na integridade da persistência RAW, no controle de concorrência, na consistência temporal, no congelamento dos alvos esperados e no avanço seguro do watermark.

Também foi definido um procedimento de execução por tarefa, dividido em investigação, reprodução do problema, proposta de solução, implementação controlada e testes de regressão.

Como primeira atividade, foi priorizada a regularização dos arquivos de migração e documentação necessários para tornar a branch incremental reproduzível em outros ambientes.

### Documentação e preservação do ambiente de desenvolvimento

Foram preparados três documentos técnicos:

- `DIAGNOSTICO_ATUAL_INCREMENTAL.md`;
- `BACKLOG_PRIORIZADO_INCREMENTAL.md`;
- `PLANO_EXECUCAO_INCREMENTAL.md`.

Os documentos registram o estado atual da implementação, os riscos encontrados e a sequência recomendada para as próximas atividades.

Também foi revisado o procedimento de utilização do Git stash para preservar os arquivos locais da auditoria e as migrações SQL antes da mudança de contexto para outras atividades do projeto.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como apoio para:

- estruturar a auditoria técnica da ingestão incremental;
- investigar riscos relacionados ao versionamento e à persistência RAW;
- organizar os problemas encontrados por nível de criticidade;
- elaborar um backlog com dependências e critérios de aceite;
- revisar os cuidados necessários para preservar os bancos e checkpoints existentes.

### Resultado do encontro

Ao final do encontro, a arquitetura incremental estava documentada e avaliada.

Foram identificados cinco problemas críticos que precisam ser corrigidos antes da integração HTTP real. A análise foi realizada sem modificar os dados operacionais ou executar novas coletas.

A implementação das correções ficou planejada para as próximas atividades, priorizando a integridade dos registros RAW e a segurança do processamento incremental.

### Próximos passos

Os próximos passos definidos foram:

- regularizar e versionar os arquivos de migração e documentação da branch incremental;
- validar as entradas e o tratamento de registros anômalos;
- corrigir a interpretação de timestamps e atualizações fora de ordem;
- garantir atomicidade nas operações de versionamento RAW;
- implementar proteção contra gravações após a expiração do lease;
- impedir o avanço do watermark quando houver janelas pendentes;
- corrigir os mecanismos de paginação e retomada;
- revisar a consolidação dos registros PCA;
- implementar e testar os adaptadores HTTP incrementais em ambiente isolado, após a estabilização da arquitetura.

## Encontro 12 - 2026-10-16

### Relato individual — José Renan Freitas Marins (4h)

Continuidade às atividades de desenvolvimento e estabilização da arquitetura de ingestão incremental dos dados do Portal Nacional de Contratações Públicas (PNCP). O objetivo foi iniciar a execução das tarefas definidas no backlog técnico, corrigir problemas de reprodutibilidade identificados na auditoria anterior e organizar o versionamento das alterações realizadas na branch `feature/ingestao-incremental-pncp`.

### Implementação da tarefa INC-001 — Migrações e documentação

A primeira atividade foi a execução da tarefa INC-001, relacionada à ausência de arquivos essenciais de migração e documentação no repositório.

Durante a investigação, foi identificado que determinados arquivos haviam sido desenvolvidos localmente e preservados no Git stash, mas não estavam incluídos no histórico da branch. Essa situação provocava falhas em testes automatizados e impedia que um clone limpo do repositório reproduzisse corretamente o ambiente de ingestão incremental.

Foram recuperados e incorporados ao versionamento os seguintes arquivos:

- `migrations/001_raw_canonical_identity_index.sql`, responsável pela criação do índice de identidade canônica dos registros RAW;
- `migrations/002_sync_window_checkpoint.sql`, responsável pelas estruturas de controle de sincronização incremental;
- `docs/PNCP_INCREMENTAL_ENDPOINTS.md`, contendo a documentação dos endpoints e das regras de processamento incremental.

A recuperação foi realizada seletivamente, sem aplicar integralmente os stashes e sem alterar os bancos operacionais existentes.

### Validação das migrações e integridade dos dados

Após a recuperação dos arquivos, foram executados testes específicos para verificar a compatibilidade das migrações com a estrutura atual do SQLite.
- preservação dos registros existentes na camada RAW;
- preservação dos checkpoints legados;
- criação correta do índice de identidade canônica;
- criação das tabelas de checkpoint v2;
- execução idempotente das migrações;
- resultado `ok` na verificação de integridade do SQLite;
- ausência de violações de chaves estrangeiras.

Também foram executados os testes automatizados do projeto, com os seguintes resultados:

- 2 testes específicos de migração aprovados;
- 117 testes da suíte completa aprovados;
- validação de sintaxe Python aprovada;
- verificação `git diff --check` aprovada;
- nenhuma modificação nos bancos operacionais;
- nenhuma chamada HTTP real durante a validação.

Com esses resultados, a INC-001 foi considerada implementada e validada.

### Organização e versionamento das alterações no Git

Em seguida, concentrei as atividades na organização do histórico de desenvolvimento da branch incremental.
Entre os componentes identificados estavam:
- identidade canônica e versionamento dos registros RAW;
- persistência e controle de atomicidade;
- checkpoints e execução incremental;
- proteção de leases e concorrência;
- continuidade do watermark;
- paginação e recuperação de falhas nos coletores;
- testes automatizados de integridade e sincronização.

### Revisão da documentação incremental

Durante a organização das alterações, também foi revisada a documentação técnica dos endpoints incrementais.

Foram identificadas atualizações relacionadas às condições necessárias para confirmar uma janela de sincronização e avançar o watermark, considerando a existência de janelas anteriores pendentes e a continuidade da cobertura temporal.

A documentação também passou a descrever estratégias de recuperação de paginação, incluindo a repetição de janelas desde a primeira página quando não houver garantia de estabilidade na ordenação dos registros, além do tratamento de páginas intermediárias vazias e inconsistências nas respostas da API.

Essas definições contribuem para estabelecer critérios mais rigorosos de recuperação e confirmação das coletas incrementais.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como ferramentas de apoio para:

- investigar a ausência dos arquivos necessários à reprodução do ambiente incremental;
- analisar a estrutura das migrações SQL e seus impactos;
- validar os resultados dos testes e verificações de integridade;
- analisar as alterações pendentes na branch;
- revisar as regras de sincronização, paginação e continuidade do watermark.

### Resultado do encontro

Ao final do encontro, a tarefa INC-001 estava implementada, validada e registrada no histórico local da branch incremental.
Foram recuperados os arquivos essenciais de migração e documentação, eliminando as falhas de reprodutibilidade identificadas nos testes específicos. A suíte completa de 117 testes foi executada com sucesso durante a validação dessa tarefa.
Também foi realizada a organização dos commits referentes às alterações da ingestão incremental, preparando o projeto para dar continuidade às correções de integridade, concorrência e recuperação de falhas.
As atividades de validação da INC-001 ocorreram sem alterações nos bancos operacionais e sem execução de requisições HTTP reais.

### Próximos passos

Os próximos passos definidos foram:

- verificar e validar individualmente as correções já desenvolvidas na branch incremental;
- concluir o tratamento de timestamps inválidos, ausentes e fora de ordem;
- garantir atomicidade nas operações de persistência e versionamento RAW;
- validar a proteção contra gravações após a perda ou expiração do lease;
- assegurar o avanço contíguo do watermark;
- revisar os mecanismos de paginação, retomada e reconciliação de alvos;
- ampliar os testes de regressão para cenários de concorrência e falhas;
- preparar a integração com os endpoints HTTP reais do PNCP em ambiente isolado;
- após a estabilização da ingestão incremental, avançar na integração com a camada de normalização dos dados.

- ## Encontro 13 - 2026-10-19

### Relato individual — José Renan Freitas Marins (4h)

Neste encontro, com foco na conclusão da auditoria da camada RAW e na implementação da camada normalizada. O objetivo foi garantir a integridade dos dados coletados, estabelecer uma estrutura relacional independente e preparar o projeto para as futuras etapas de consultas estruturadas, indicadores e integração com Inteligência Artificial Generativa.

### Camada RAW

responsável pela auditoria e preparação da base RAW para a normalização.

Foram verificadas as condições de execução dos coletores, a integridade do banco SQLite, o histórico das ingestões e a cobertura dos recursos coletados.

As principais atividades realizadas foram:
- verificação da ausência de coletores Python e bloqueios SQLite ativos;
- criação de backup consistente antes das alterações administrativas;
- regularização de quatro execuções antigas que permaneciam com status `RUNNING`, classificadas como `FAILED`;
- preservação integral dos registros RAW;
- atualização do inventário de órgãos e unidades;
- verificação da integridade do SQLite e das chaves estrangeiras.

Ao final dessa etapa, a RAW permaneceu com **1.391.174 registros**, nenhuma execução em andamento e nenhuma violação de integridade referencial.
Também foram documentadas ressalvas relacionadas à cobertura parcial de empenhos, contratos sem contratação-pai no recorte, datas suspeitas em resultados homologados e limitações na cobertura das atas de registro de preços.

A Fase 0 foi concluída e aprovada com ressalvas documentadas, após a execução bem-sucedida de 225 testes automatizados.

### Modelagem da camada normalizada

Na sequência, foi desenvolvida a modelagem relacional da camada normalizada, mantendo sua independência em relação ao banco RAW original. A proposta foi organizar os dados provenientes das APIs do PNCP em entidades estruturadas, preservando a rastreabilidade até os registros originais.

Foi elaborado um modelo contendo **16 tabelas normalizadas**, incluindo entidades relacionadas a:
- órgãos e unidades administrativas;
- fornecedores;
- contratações e itens;
- resultados homologados;
- contratos e empenhos;
- atas de registro de preços;
- Planos de Contratações Anuais (PCA) e seus respectivos itens;
- controle e auditoria da normalização.

Também foram definidos os relacionamentos, chaves primárias e estrangeiras, regras de integridade e mecanismos de rastreabilidade por identificador RAW, hash e execução.
A modelagem considerou situações específicas encontradas nos dados reais, como contratos sem contratação-pai no recorte temporal, cobertura parcial de empenhos e diferenças entre formatos de payload das APIs.

A associação entre itens do PCA e itens de contratação foi mantida como uma relação que exige evidências e validação, evitando estabelecer vínculos não garantidos pelo PNCP.

O DDL foi validado em um banco SQLite temporário, com 16 tabelas criadas, integridade confirmada e **232 testes automatizados aprovados**.

### Implementação e validação da normalização

Após a definição do modelo relacional, foi realizada a implementação e execução do processamento de normalização dos dados RAW.
O processamento contemplou a seleção das versões vigentes dos registros, a transformação dos payloads JSON em entidades relacionais, a preservação da proveniência e o tratamento de inconsistências conhecidas.

A execução utilizou a base RAW completa, com os seguintes resultados:
- 1.391.174 registros RAW processados;
- 1.664.131 entidades normalizadas;
- 180.151 contratações;
- 557.211 itens de contratação;
- 417.675 resultados homologados;
- 151.898 contratos;
- 1.900 empenhos;
- 80.761 atas de registro de preços;
- 567 PCAs pertencentes ao escopo RJ;
- 228.469 itens de PCA.

Foram tratados casos específicos, incluindo 3.672 contratos cuja contratação-pai não estava presente no recorte, quatro contratos sem identificação de fornecedor, 72 resultados com datas suspeitas e quatro lacunas conhecidas na cobertura de empenhos.
Também foram identificados 1.011 PCAs fora do inventário do Rio de Janeiro, que não foram incluídos no conjunto normalizado do escopo RJ.
A implementação contemplou o tratamento de versões RAW recebidas fora de ordem e a reexecução idempotente, evitando a duplicação de entidades normalizadas.

### Validação da integridade e reconciliação financeira
Após o processamento, foram executadas verificações de integridade estrutural, consistência dos relacionamentos e reconciliação dos valores financeiros entre a RAW e a camada normalizada.

Os resultados apresentados foram:
- zero registros rejeitados;
- zero violações de chaves estrangeiras;
- `PRAGMA integrity_check` com resultado `ok`;
- 247 testes automatizados aprovados;
- reexecução idempotente validada;
- reconciliação financeira exata entre os valores de origem e os valores normalizados.

Os valores reconciliados foram:

- resultados homologados: R$ 533.771.492.800,03;
- contratos: R$ 787.533.670.110,70;
- empenhos: R$ 131.953.649,08;
- PCA no escopo RJ: R$ 191.389.328.133,31.

Esses valores representam diferentes estágios das contratações públicas e foram mantidos separados para evitar interpretações incorretas entre planejamento, homologação, contratação e execução orçamentária.

O banco normalizado gerado possui aproximadamente 2,18 GB e foi validado sem modificar a RAW oficial.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como ferramentas de apoio para:
- estruturar o planejamento e os critérios de validação das fases de normalização;
- analisar a integridade da RAW e os riscos associados à preparação dos dados;
- apoiar a definição das entidades, chaves e relacionamentos;
- revisar a modelagem relacional e as regras de rastreabilidade;
- orientar o tratamento de inconsistências e versões recebidas fora de ordem;
- analisar os resultados dos testes automatizados;
- avaliar a reconciliação financeira entre RAW e normalizada;
- planejar a futura integração da camada normalizada com consultas SQL, agentes de IA e RAG.

### Resultado do encontro
A camada normalizada passou a disponibilizar **1.664.131 entidades estruturadas**, com relacionamentos definidos, rastreabilidade até a RAW, integridade referencial e reconciliação financeira validada.
O processamento foi realizado em um banco independente, preservando integralmente a base RAW operacional e sem executar novas coletas ou chamadas HTTP ao PNCP.
A implementação representa um avanço na preparação dos dados para a construção de indicadores, consultas SQL e mecanismos de recuperação de informações com Inteligência Artificial Generativa.

### Próximos passos
Os próximos passos definidos foram:

- revisar a privacidade e a proteção dos dados de fornecedores pessoa física;
- preparar o banco normalizado para distribuição em uma release independente;
- compactar o artefato e gerar checksum SHA-256;
- documentar a proveniência, cobertura e limitações da base normalizada;
- organizar os commits e o versionamento das implementações;
- desenvolver indicadores e consultas SQL canônicas;
- investigar e implementar associações auditáveis entre PCA e contratações;
- estruturar a camada semântica para interpretação de perguntas;
- implementar agentes de IA para consultas estruturadas;
- integrar a recuperação documental com RAG, preservando as evidências utilizadas nas respostas.

## Encontro 14 - 2026-10-21

### Relato individual — José Renan Freitas Marins (4h)
om foco na homologação operacional da API integrada à camada normalizada, na identificação e correção de problemas relacionados à segurança e à recuperação documental e no planejamento da arquitetura de processamento de PDFs sob demanda.

O objetivo foi validar a utilização da base normalizada em consultas reais, verificar o funcionamento dos fluxos Structured, RAG e Hybrid e preparar o sistema para responder perguntas em linguagem natural com informações confiáveis, rastreáveis e fundamentadas em evidências.

### Integração operacional da API com a base normalizada

Inicialmente, foram consolidadas as implementações relacionadas à integração da API com a base normalizada SQLite, disponibilizadas nos PRs #60 e #61.
A homologação confirmou que a conexão utiliza `mode=ro` e `PRAGMA query_only=1`, impedindo alterações no banco normalizado.
Também foram verificadas as seguintes quantidades de registros:
- 180.419 contratações;
- 151.898 contratos;
- 567 Planos de Contratações Anuais (PCA);
- 228.469 itens de PCA;
- 44.689 contratações referentes a 2026.

A integridade do banco foi confirmada por meio de `PRAGMA integrity_check`, com resultado `ok`.

### Homologação das rotas e consultas da API

Na sequência, foi realizada a homologação operacional da API utilizando a base normalizada real em modo somente leitura e uma cópia temporária do banco operacional da aplicação.

Foram avaliadas as rotas:

- `/docs`, para acesso à documentação Swagger;
- `/openapi.json`, para validação dos contratos da API;
- `/auth/register`, `/auth/login` e `/auth/me`, para autenticação;
- `/query/structured`, para consultas estruturadas;
- `/query/ask`, para roteamento das perguntas;
- `/query/generate`, para geração de respostas com recuperação documental;
- `/query/catalog/documents`, para consulta ao catálogo de documentos.

Os testes confirmaram o funcionamento do startup, da autenticação, da validação das entradas e da execução direta da SQL Tool sobre dados reais.

Uma consulta relacionada a contratos de licenciamento de software em 2025, com valor superior a R$ 500 mil, retornou cinco registros compatíveis com os filtros disponíveis, incluindo informações dos fornecedores.

Entretanto, foram identificadas limitações na execução completa das perguntas em linguagem natural, principalmente devido à instabilidade do provedor ECOA e à ausência de funcionalidades analíticas necessárias para responder integralmente às perguntas das personas.

### Avaliação do Adaptive RAG e identificação de limitações

Durante os testes, foram analisados os mecanismos de interpretação de perguntas, consultas SQL e recuperação documental.

As principais limitações identificadas foram:

- ausência do índice FAISS operacional;
- instabilidade do provedor ECOA, com ocorrência de timeouts;
- corpus operacional contendo apenas dois documentos e 55 chunks;
- ausência de suporte a determinados filtros e relacionamentos necessários às perguntas oficiais;
- necessidade de ampliar a proveniência estruturada das respostas;
- impossibilidade de executar integralmente o fluxo Hybrid;
- possibilidade de uma consulta retornar HTTP 200 sem responder corretamente à pergunta original.

Também foram avaliadas as três personas do desafio.

Na pergunta de Marina, relacionada ao preço médio por quilograma de arroz, foi identificada a necessidade de integrar itens de contratação, resultados homologados, quantidades e unidades de medida.

Na pergunta de Rodrigo, relacionada a contratos estaduais de licenciamento de software, foi identificada a ausência de um filtro específico para esfera governamental.

Na pergunta de Cláudia, relacionada à participação de MEI em pregões eletrônicos, foram identificadas necessidades de integração entre informações normativas, situação das oportunidades e recuperação documental.

Essas verificações demonstraram que a camada SQL normalizada está operacional, mas que o Adaptive RAG ainda necessita de melhorias para responder integralmente às perguntas do desafio.

### Implementação de segurança e minimização dos logs

Após a homologação, foi realizada uma análise dos mecanismos de observabilidade e armazenamento de logs.

Foi identificado que determinados eventos persistiam perguntas completas, prompts, respostas geradas e saídas brutas do Query Analyzer, representando um risco de exposição de informações sensíveis.

Para corrigir esse comportamento, foi implementada uma política de minimização baseada em uma lista explícita de campos permitidos.

As principais melhorias foram:

- remoção de perguntas e respostas completas dos logs operacionais;
- impedimento do armazenamento de prompts e saídas brutas dos modelos;
- descarte de campos adicionais não autorizados;
- preservação de métricas de latência, tokens, status e modelo utilizado;
- manutenção da correlação entre requisições por `run_id`;
- registro de quantidades e identificadores técnicos sem armazenar linhas completas das consultas SQL;
- tratamento de exceções sem persistir mensagens que possam conter dados sensíveis.

O histórico funcional das conversas, armazenado nas tabelas `queries` e `responses`, foi preservado, por possuir finalidade distinta dos logs operacionais.

A implementação foi validada com dados sintéticos, incluindo CPF, e-mail, tokens e informações bancárias fictícias.

Após essa etapa, foram registrados **612 testes e 107 subtestes aprovados**.

### Tratamento seguro de indisponibilidade do FAISS

Em seguida, foi realizada a correção do tratamento de erros relacionados ao carregamento do índice FAISS.

Durante a homologação, foi identificado que a ausência do índice provocava erros HTTP 500 nas rotas de recuperação documental.

Foi implementado um contrato específico para classificar três situações:

- `faiss_index_missing`: índice inexistente;
- `faiss_index_corrupt`: arquivos corrompidos ou inconsistentes;
- `faiss_index_incompatible`: incompatibilidade de modelo ou dimensão dos embeddings.

A API passou a retornar HTTP 503 quando a recuperação documental necessária estiver indisponível, utilizando mensagens controladas e sem exposição de caminhos locais, credenciais ou informações internas.

Também foi preservada a independência das rotas Structured e Catalog, permitindo que continuem funcionando mesmo quando o índice FAISS não estiver disponível.

O fluxo Hybrid passou a tratar a indisponibilidade de evidências obrigatórias sem apresentar respostas parciais como se fossem completas.

Erros inesperados de programação continuam sendo tratados separadamente, evitando que falhas não relacionadas à infraestrutura sejam mascaradas.

Após a implementação da H2, os resultados foram:

- **624 testes automatizados aprovados;**
- **110 subtestes aprovados;**
- compilação dos módulos alterados aprovada;
- `git diff --check` aprovado;
- preservação das alterações anteriores da H1;
- nenhuma alteração nos bancos operacionais.

As implementações H1 e H2 permaneceram sem commit, aguardando revisão técnica.

### Planejamento da arquitetura de processamento documental sob demanda

Também foi retomada a discussão sobre o processamento dos documentos PDF associados às contratações públicas do PNCP.

Considerando o grande volume potencial de editais, contratos, atas e anexos, foi definida como proposta a utilização de uma arquitetura híbrida, combinando **pré-processamento seletivo, processamento sob demanda e cache persistente**.

A proposta busca evitar o download, a extração de texto, o OCR e a geração antecipada de embeddings para todo o acervo documental.

O fluxo planejado contempla:

- identificação dos documentos disponíveis por meio de um catálogo documental;
- associação dos documentos às respectivas contratações e entidades do PNCP;
- verificação da existência de conteúdo previamente processado;
- recuperação direta de documentos já indexados;
- download sob demanda de documentos ainda não processados;
- extração de texto nativo dos PDFs;
- utilização seletiva de OCR em páginas digitalizadas, imagens e tabelas;
- divisão do conteúdo em chunks com preservação de página e proveniência;
- geração de embeddings e indexação no FAISS;
- integração com busca lexical FTS5/BM25 e fusão RRF;
- armazenamento em cache para evitar processamento repetido;
- controle de versões e integridade por hash SHA-256.

Foi preparado um roteiro de auditoria técnica para verificar quais desses componentes já existem no repositório, identificar lacunas e definir um plano de implementação incremental.

Essa arquitetura ainda está em fase de análise e planejamento, não tendo sido implementada neste encontro.

### Uso de Inteligência Artificial

Utilizei o ChatGPT como ferramentas de apoio para:

- estruturar o planejamento da homologação operacional da API;
- definir critérios de validação para consultas utilizando a base normalizada;
- analisar os resultados dos testes Structured, RAG e Hybrid;
- identificar limitações do Query Analyzer e da recuperação documental;
- orientar a implementação da política de minimização de dados nos logs;
- apoiar a definição do contrato de erros do FAISS;
- estruturar testes automatizados de segurança e tratamento de falhas;
- discutir a arquitetura de processamento de PDFs sob demanda;
- planejar a integração entre catálogo documental, OCR, FAISS, FTS5 e Adaptive RAG;

### Resultado do encontro

A homologação confirmou que a API consegue acessar a base normalizada real em modo somente leitura, executar consultas estruturadas e preservar a integridade dos bancos operacionais.

Foram implementadas melhorias de segurança e observabilidade, além de mecanismos de tratamento controlado para indisponibilidade do índice FAISS.

A suíte automatizada alcançou **624 testes e 110 subtestes aprovados**, sem execução de novas coletas, migrations ou alterações nos bancos RAW e normalizado.

Também foram identificadas as limitações que impedem a homologação completa do Adaptive RAG e estruturada uma proposta de processamento documental seletivo e sob demanda.

As alterações H1 e H2 permaneceram locais, sem commit, push ou merge, aguardando revisão. Os PRs existentes também permaneceram sem integração à branch principal.

### Próximos passos

Os próximos passos definidos foram:

- realizar a revisão técnica conjunta das implementações H1 e H2;
- organizar as alterações em commits independentes após aprovação;
- manter os PRs existentes sem merge até a validação da equipe;
- avaliar a configuração de um provedor OpenAI como alternativa ao ECOA;
- estabilizar a interpretação de perguntas em linguagem natural;
- implementar validações para impedir respostas semanticamente incompletas;
- ampliar os filtros e relacionamentos da SQL Tool para atender às três personas;
- aprimorar a proveniência das respostas estruturadas;
- auditar a arquitetura existente de catálogo e processamento documental;
- definir o pipeline de extração de PDFs e OCR seletivo;
- construir e validar o primeiro índice FAISS operacional;
- integrar a recuperação híbrida com FTS5, FAISS e RRF;
- implementar cache e processamento documental sob demanda;
- realizar novos testes ponta a ponta nas rotas Structured, RAG e Hybrid;
- avançar na homologação do Adaptive RAG com respostas fundamentadas e auditáveis.
