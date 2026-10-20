## Encontro 1 - 2026-09-16

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade ao projeto realizando a criação das personas. Desenvolvi três personas diferentes e, para cada uma delas, elaborei três perguntas, totalizando nove perguntas para o sistema. Também detalhei o perfil de cada persona, as perguntas que ela faria e quais rotas seriam esperadas para atender a cada situação.

Além disso, analisei quais dessas perguntas poderiam apresentar algum problema ou resultado inesperado no sistema, explicando os possíveis motivos pelos quais isso poderia acontecer.

Na próxima etapa, vou dar continuidade ao trabalho com os documentos que foram coletados, iniciando a parte de estruturação desses documentos.

## Encontro 2 - 2026-09-18

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, realizei a criação das funções responsáveis por fazer as requisições de contratos, contratações e contratações em aberto. A implementação dessas funções foi concluída, porém ainda preciso realizar os testes das partes de contratos e contratações em aberto, pois a API aparentemente estava sobrecarregada e não foi possível executar os testes corretamente.

Na próxima etapa, vou continuar os testes dessas funções e verificar se as requisições estão retornando os dados esperados.

## Encontro 3 - 2026-09-21

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade à parte de contratações e contratos do projeto, contando também com o auxílio do Alisson nessa etapa. Ele realizou algumas implementações e me passou para que eu pudesse dar continuidade ao desenvolvimento. Trabalhei principalmente em alguns ajustes relacionados à estrutura das pastas e organização do projeto, além de continuarmos realizando os testes.

Durante o alinhamento com o professor, identificamos a necessidade de implementar mais algumas funcionalidades e analisar melhor como os dados serão armazenados no banco, avaliando se utilizaremos uma estrutura de banco estruturado ou outra abordagem.

Também conversamos bastante sobre a estrutura geral do projeto e o fluxo de funcionamento, buscando entender melhor como as partes irão se integrar. A partir disso, os próximos passos são revisar alguns endpoints, ajustar o que for necessário e buscar documentos adicionais para complementar a base do projeto.

## Encontro 4 - 2026-09-23

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade ao desenvolvimento da parte de contratos, realizando algumas alterações nas funções responsáveis pelas requisições, principalmente relacionadas ao tempo de espera das requisições. Também consegui montar uma base de testes com os contratos, que agora estão sendo salvos em arquivos JSON.

A partir dessa base, desenvolvi o fluxo para listar os documentos relacionados a cada contrato e realizar o download desses arquivos. Também criei um manifesto contendo informações dos contratos e os respectivos links dos documentos. Com esse JSON, consigo percorrer os registros e realizar o download dos arquivos automaticamente.

Como os documentos podem vir em formatos diferentes, como ZIP e PDF, também implementei uma função para realizar a extração do conteúdo dos arquivos PDF. Dessa forma, avancei na estrutura do fluxo de coleta dos contratos até a obtenção e preparação dos documentos que serão utilizados no projeto.

## Encontro 5 - 2026-09-25

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade ao desenvolvimento da parte de contratos, adaptando o que já havia sido implementado para trabalhar também com contratações. Busquei reaproveitar as funções existentes, realizando alguns ajustes necessários para adequá-las ao novo fluxo.

Também implementei a parte de filtros e uma pipeline para realizar testes de download dos documentos. Como existem 37 tipos diferentes de documentos, optei por aplicar um filtro para selecionar apenas os tipos relevantes para o projeto, evitando trabalhar inicialmente com todos eles. Dessa forma, conseguimos reduzir a quantidade de documentos processados e tornar a base de testes mais controlada, considerando o grande volume de dados disponível.

## Encontro 6 - 2026-09-28

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade ao desenvolvimento do projeto realizando os testes de download dos documentos de contratos e contratações, verificando se o fluxo implementado estava funcionando corretamente.

Também iniciei a etapa de tratamento dos documentos e extração dos textos. Atualmente, estou utilizando uma abordagem híbrida com PyPDF e Docling, sendo o PyPDF a opção prioritária. Porém, ainda estou avaliando se o Docling pode ser uma alternativa melhor como extrator principal. Para isso, estou realizando testes de desempenho, inclusive utilizando o Google Colab, para comparar os resultados e o tempo de processamento.

Com os documentos já extraídos, também comecei a trabalhar na etapa de criação dos chunks, preparando esses dados para posteriormente serem armazenados e utilizados no banco vetorial.

Além disso, durante o final de semana, aproveitei para realizar novas requisições e downloads de contratos e contratações, com o objetivo de aumentar as bases que serão utilizadas no projeto.

## Encontro 7 - 2026-09-30

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, trabalhei na preparação e ambientação do Google Colab para receber e processar os documentos utilizados no projeto. Para isso, refatorei algumas partes do código para adequar o fluxo ao processamento pelo Colab e realizei validações para verificar o funcionamento e o desempenho dessa abordagem.

Também comecei a estruturar uma documentação com orientações sobre esse processo, com o objetivo de compartilhar com os demais integrantes do grupo e facilitar a utilização do Colab na etapa de extração e processamento dos dados.

Além disso, dediquei parte do tempo à revisão da arquitetura do projeto, principalmente em relação ao fluxo de processamento da base que estou desenvolvendo. Fiz algumas modificações e testes buscando melhorar essa estrutura antes de integrar definitivamente as alterações ao projeto principal.

Dessa forma, o trabalho de hoje ficou concentrado principalmente na refatoração do código, validação do fluxo, análise de desempenho e organização da arquitetura para posteriormente implementar essas melhorias no projeto.

## Encontro 8 - 2026-10-02

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade à coleta e à extração dos documentos, utilizando o Google Colab para realizar o processamento. Também trabalhei na persistência dos dados de contratos e contratações referentes ao período de janeiro a agosto no banco estruturado.

Com base na estrutura e nos códigos que já haviam sido desenvolvidos pela equipe, criei a tabela raw_asset e desenvolvi uma pipeline para realizar a persistência desses dados no banco. Para isso, adaptei e integrei o que já havia sido implementado pelos demais integrantes ao fluxo de contratos e contratações que estou desenvolvendo.

Dessa forma, o trabalho de hoje ficou concentrado na continuidade da coleta e extração dos documentos e na estruturação do fluxo para armazenamento dos dados no banco estruturado.

## Encontro 9 - 2026-10-05

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade ao processamento dos dados e à etapa de ingestão nos bancos. Trabalhei com a ingestão no banco vetorial utilizando o FAISS para testes e também criei um arquivo de teste para realizar buscas e verificar se os dados estavam sendo recuperados corretamente. Esse arquivo ainda é inicial e provavelmente passará por alterações conforme o desenvolvimento do projeto avançar.

Além disso, junto com a equipe, apresentamos o andamento do projeto ao professor e discutimos o que já foi desenvolvido até o momento.

Também continuei o processamento dos documentos em lotes, preparando esses dados para posteriormente realizar a ingestão completa no banco. Dessa forma, o trabalho de hoje ficou concentrado principalmente no processamento, ingestão e nos primeiros testes de recuperação das informações.

## Encontro 10 - 2026-10-05

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, realizei a implementação do FTS5 para complementar o processo de busca e recuperação das informações no projeto. Após a implementação, fiz testes para verificar o funcionamento da busca e analisar os resultados retornados pelo sistema.

Também realizei alguns ajustes no prompt utilizado pela LLM. Limitei o tamanho das respostas, padronizei as citações para o formato `[1]`, `[2]` e adicionei uma instrução para evitar que evidências de processos diferentes sejam misturadas na mesma resposta.

Além disso, melhorei as informações enviadas no contexto para a LLM, incluindo identificadores mais claros sobre a origem de cada evidência, como o `numeroControlePNCP`, o título do documento e a URL de origem.

O trabalho de hoje ficou concentrado principalmente na implementação do FTS5 e nos ajustes e testes do fluxo de recuperação e geração das respostas.

## Encontro 11 - 2026-10-09

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade ao desenvolvimento e, principalmente, aos testes das funcionalidades que comecei a implementar ontem, envolvendo a análise das perguntas (Query Analysis), o roteamento das buscas (Router), a integração com o banco estruturado (Structured DB) e a aplicação dos filtros.

Também trabalhei na criação e nos testes de endpoints para verificar o funcionamento das diferentes rotas de busca, avaliando se as perguntas estão sendo direcionadas corretamente para SQL, RAG ou busca híbrida.

Durante os testes, identifiquei que alguns cenários apresentaram os resultados esperados, enquanto outros ainda precisam de ajustes. Por isso, dediquei boa parte do dia à análise desses comportamentos, buscando identificar possíveis problemas e melhorias no fluxo.

Dessa forma, o trabalho de hoje ficou concentrado principalmente na validação das funcionalidades implementadas, na identificação de falhas e nos ajustes necessários para melhorar o funcionamento das buscas.

## Encontro 12 - 2026-10-14

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade aos testes do projeto, criando um fallback para auxiliar na validação do Query Analysis e dos filtros. Realizei testes diretamente pelo console para verificar se as perguntas estão sendo interpretadas e processadas corretamente, fazendo ajustes e refinamentos conforme os resultados apresentados.

Também trabalhei na análise dos retornos das buscas, buscando identificar possíveis falhas e melhorar o comportamento do sistema antes de avançar para as próximas etapas.

Além disso, realizei o download de novos documentos para complementar a base do projeto e fiz a ingestão de parte desses arquivos no banco de dados.

Dessa forma, o trabalho de hoje ficou concentrado principalmente nos testes e ajustes do Query Analysis e dos filtros, além da ampliação e atualização da base de documentos utilizada pelo sistema.

## Encontro 13 - 2026-10-16

### Relato individual - Luciano Oliveira da Costa (4h)

Hoje, dei continuidade aos testes e ajustes do Query Analysis e dos filtros, buscando melhorar a interpretação das perguntas e o direcionamento das buscas. Tenho realizado várias baterias de testes, nas quais algumas perguntas apresentam os resultados esperados, enquanto outras ainda precisam de ajustes e refinamentos.

Também continuei a coleta de contratos e contratações, além da listagem dos documentos relacionados a esses registros, com o objetivo de ampliar a base de dados do projeto.

Além disso, comecei a implementar um fluxo para tratar documentos que ainda não estão indexados no sistema. A ideia é permitir que o usuário visualize esses documentos e tenha a opção de solicitar sua indexação. Para isso, desenvolvi endpoints para acompanhar o processamento, consultar o status e realizar novas tentativas em caso de falhas.

Essa implementação ainda está em desenvolvimento, pois falta integrar os diferentes fluxos e complementar a base com mais informações e documentos. Dessa forma, o trabalho de hoje ficou concentrado nos testes e refinamentos das buscas, na continuidade da coleta de dados e no desenvolvimento do fluxo de indexação de documentos ainda não disponíveis na base.
