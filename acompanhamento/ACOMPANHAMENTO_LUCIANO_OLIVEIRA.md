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
