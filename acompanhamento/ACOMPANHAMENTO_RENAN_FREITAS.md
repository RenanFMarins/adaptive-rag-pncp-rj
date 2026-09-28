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
