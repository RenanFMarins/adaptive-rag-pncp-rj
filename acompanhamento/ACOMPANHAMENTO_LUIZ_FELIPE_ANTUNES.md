# Acompanhamento — Grande Desafio IA Generativa e RAG

**Integrante:** Luiz Felipe Antunes

---

## Encontro 1 — 16/09/2026

## Atividades realizadas

Concluí a primeira definição do corpus do cenário de **Contratações Públicas do Estado do Rio de Janeiro**, considerando o ano-base de 2025.

Estruturei o arquivo `corpus_manifest.yaml`, utilizado como referência para declarar as fontes, os tipos de dados, as formas de acesso e os critérios de seleção do corpus.

Foram definidas as quatro bases previstas no cenário:

* **Normativa:** Lei 14.133/2021, decretos estaduais e editais de licitação, utilizando fontes oficiais do Planalto e do PNCP.
* **Estruturada:** contratos e contratações do Estado do RJ, utilizando a API de consulta do PNCP, com período fechado de 2025.
* **Conversacional:** atas de registro de preços do PNCP e trilha de e-mails de compras disponibilizada na base sintética do desafio.
* **Agregada:** Plano de Contratações Anual e valores homologados por item, utilizando dados do PNCP.

Também defini no Manifest os critérios de seleção determinística das bases, as fontes oficiais de consulta, os formatos esperados dos dados, informações de vigência e sensibilidade, sugestões iniciais de chunking e os metadados relevantes.

## Resultado

O `corpus_manifest.yaml` passou a concentrar a definição das quatro bases do cenário, permitindo que a seleção e a coleta dos dados sejam realizadas de forma padronizada e reproduzível.

Nesta etapa, o foco foi estabelecer a estrutura e os critérios do corpus. O detalhamento da coleta e a validação dos volumes serão realizados nas próximas etapas.

## Bloqueios em aberto

* Durante a definição das fontes, houve instabilidade no PNCP, dificultando algumas consultas e a validação inicial dos documentos.
* Ainda é necessário localizar e validar os decretos estaduais do RJ que farão parte da base normativa.
* Alguns detalhes da seleção e coleta das fontes ainda precisam ser confirmados durante os primeiros testes práticos do corpus.

## Próximo passo — início do Encontro 2

* Avançar na seleção e coleta das fontes que compõem o corpus definido no `corpus_manifest.yaml`.
* Completar a lista de decretos estaduais e editais que serão utilizados na base normativa.
* Acompanhar a coleta dos documentos e contribuir para a organização do `CORPUS_INVENTORY.md`.
* Validar se as fontes selecionadas estão de acordo com os critérios definidos no Manifest e com as perguntas das personas.
* Acompanhar a evolução do processamento das bases e ajustar a definição do corpus quando necessário.

## Uso de assistentes de IA

* Utilizei assistentes de IA como apoio na organização e revisão do `corpus_manifest.yaml`, principalmente para estruturar as informações das quatro bases, os critérios de seleção, as fontes e as formas de acesso.
* Também utilizei IA para esclarecer dúvidas sobre a organização do Manifest e conferir se a estrutura estava alinhada aos requisitos do desafio.
* As sugestões foram revisadas e ajustadas por mim de acordo com o enunciado, as fontes oficiais do PNCP e a definição das bases do projeto.


# Acompanhamento — Grande Desafio IA Generativa e RAG

**Integrante:** Luiz Felipe Antunes

---

## Encontro 2 — 18/09/2026

### Atividades realizadas

Dei continuidade à organização do corpus definido no `corpus_manifest.yaml`, acompanhando a evolução das fontes e dos materiais necessários para cada uma das quatro bases do cenário de Contratações Públicas do Estado do Rio de Janeiro.

Atuei principalmente na organização dos arquivos e da documentação do projeto, acompanhando a estrutura definida no repositório e verificando se os materiais produzidos pelo grupo estavam sendo organizados de acordo com o padrão estabelecido.

Também iniciei o acompanhamento mais próximo da **base agregada**, principalmente em relação aos dados de Plano de Contratações Anual (PCA) e aos valores homologados por item disponibilizados pelo PNCP.

### Resultado

A organização do projeto avançou junto com a definição mais detalhada das fontes e dos componentes necessários para a coleta das bases.

Também passei a acompanhar a parte de coleta e estruturação dos dados agregados, identificando os endpoints e informações necessários para essa etapa.

### Pendências e bloqueios

* Necessidade de validar os endpoints e formatos disponibilizados pelo PNCP.
* Necessidade de definir com maior precisão o recorte temporal da base agregada.
* Continuidade da organização dos documentos e materiais produzidos pelo grupo.

### Próximo passo

* Continuar a investigação da base agregada.
* Validar as fontes e endpoints do PNCP.
* Organizar os materiais da coleta no repositório.
* Acompanhar a integração das contribuições dos demais integrantes.

### Uso de assistentes de IA

Utilizei IA como apoio para compreender a documentação das APIs, organizar informações técnicas e revisar estruturas de documentação e arquivos do projeto. As informações foram conferidas e adaptadas ao contexto do desafio.

---

# Encontro 3 — 21/09/2026

### Atividades realizadas

Continuei atuando na organização técnica do projeto e no acompanhamento das bases, com maior atenção à **base agregada**.

Realizei pesquisas sobre as possibilidades de acesso aos dados de PCA e de valores homologados por item no PNCP, buscando identificar as consultas e endpoints que poderiam ser utilizados no processo de coleta.

Também acompanhei a organização do repositório GitHub, auxiliando na estruturação dos arquivos e na integração das atividades desenvolvidas pelos integrantes.

### Resultado

A base agregada passou a ter uma definição técnica mais clara, principalmente em relação às informações que precisariam ser coletadas e armazenadas.

Também avancei na documentação das fontes e na organização do material utilizado pelo grupo.

### Pendências e bloqueios

* Validação prática das consultas do PNCP.
* Definição do período histórico necessário para a base.
* Continuidade da coleta e armazenamento dos dados.

### Próximo passo

* Prosseguir com os testes das consultas do PNCP.
* Acompanhar a implementação da coleta.
* Organizar os resultados e documentos gerados no repositório.
* Continuar apoiando a integração das atividades do grupo.

### Uso de assistentes de IA

Utilizei IA para auxiliar na interpretação da documentação técnica do PNCP, investigação de endpoints, organização das informações e revisão dos arquivos do projeto.

---

# Encontro 4 — 23/09/2026

### Atividades realizadas

Dei continuidade ao trabalho relacionado à **base agregada**, acompanhando a implementação da coleta de PCA e dos valores homologados por item.

Trabalhei em conjunto com o Renan na investigação das fontes e na organização do processo de coleta, buscando entender como os dados poderiam ser obtidos, armazenados e posteriormente utilizados pelo pipeline de RAG.

Também continuei contribuindo para a organização do GitHub e dos arquivos de acompanhamento do projeto, mantendo os materiais produzidos pelo grupo estruturados e documentados.

### Resultado

Foi possível avançar na definição do processo de coleta da base agregada e no entendimento das informações retornadas pelas consultas do PNCP.

A documentação e a organização do repositório também foram atualizadas conforme a evolução do projeto.

### Pendências e bloqueios

* Continuidade dos testes com os dados reais do PNCP.
* Validação do volume e da consistência dos dados coletados.
* Definição dos próximos passos para integração da base ao pipeline.

### Próximo passo

* Acompanhar a consolidação da coleta da base agregada.
* Validar os dados obtidos.
* Apoiar a organização dos arquivos RAW e da documentação.
* Continuar auxiliando na integração das atividades do grupo.

### Uso de assistentes de IA

Utilizei IA como apoio à análise das respostas das APIs, interpretação de estruturas JSON e organização da documentação técnica. As informações foram revisadas antes de serem incorporadas ao projeto.

---

# Encontro 5 — 25/09/2026

### Atividades realizadas

Continuei acompanhando o desenvolvimento das bases e passei a atuar mais diretamente na **organização e padronização dos materiais do projeto**.

Auxiliei na organização do GitHub, dos documentos de acompanhamento e dos arquivos relacionados à coleta, buscando manter uma estrutura consistente para que as contribuições dos integrantes pudessem ser integradas posteriormente.

Também continuei acompanhando, junto ao Renan, a evolução da base agregada e a definição do processo de ingestão dos dados do PNCP.

### Resultado

O repositório passou a ter uma organização mais consistente entre código, documentação e materiais de coleta.

Também avancei no entendimento do fluxo necessário para que os dados agregados coletados pudessem posteriormente fazer parte da estrutura de ingestão do projeto.

### Pendências e bloqueios

* Continuidade da coleta histórica.
* Validação dos dados provenientes das diferentes consultas.
* Integração definitiva das partes produzidas pelos integrantes.

### Próximo passo

* Continuar a organização do repositório.
* Acompanhar a evolução da ingestão da base agregada.
* Auxiliar na documentação das decisões técnicas.
* Preparar os materiais necessários para a próxima etapa do projeto.

### Uso de assistentes de IA

Utilizei IA para apoio na revisão de documentação, organização de arquivos, esclarecimento de dúvidas técnicas e análise das estruturas utilizadas no processo de ingestão.

---

# Encontro 6 — 28/09/2026

### Atividades realizadas

Continuei atuando principalmente na **organização técnica e documental do projeto**, acompanhando a evolução das bases e a integração das atividades desenvolvidas pelo grupo.

Mantive o acompanhamento da base agregada junto ao Renan, especialmente em relação à coleta dos dados do PNCP, ao armazenamento dos dados RAW e à estrutura utilizada para controle das execuções.

Também acompanhei a organização do GitHub e a integração das alterações realizadas pelos integrantes, buscando manter o repositório organizado para as próximas etapas do desenvolvimento.

### Resultado

Avançamos na organização do processo de coleta e armazenamento dos dados da base agregada.

Também foi possível manter uma estrutura mais organizada para documentação, acompanhamento das atividades e integração das contribuições do grupo.

### Pendências e bloqueios

* Continuidade da coleta dos períodos históricos necessários.
* Validação completa dos dados coletados.
* Integração das bases ao fluxo posterior de processamento e RAG.

### Próximo passo

* Continuar acompanhando a coleta da base agregada.
* Validar os dados e arquivos gerados.
* Auxiliar na organização da documentação.
* Preparar a estrutura para as próximas etapas de processamento e RAG.

### Uso de assistentes de IA

Utilizei IA como apoio para análise técnica, revisão dos arquivos, organização da documentação e esclarecimento de dúvidas relacionadas ao processo de coleta e ingestão.

---

# Encontro 7 — 30/09/2026

### Atividades realizadas

Continuei acompanhando a evolução das bases e atuando na **organização geral do projeto, documentação e integração das contribuições do grupo**.

Mantive o trabalho relacionado à base agregada em conjunto com o Renan, acompanhando a coleta e organização dos dados de PCA e valores homologados por item.

Também realizei atividades de organização do GitHub e dos materiais do projeto, contribuindo para manter os arquivos, documentação e alterações dos integrantes estruturados e preparados para a continuidade do desenvolvimento.

Além da parte técnica, continuei auxiliando na orientação e organização das atividades do grupo, acompanhando o andamento das diferentes frentes e ajudando a alinhar as entregas.

### Resultado

O projeto avançou na organização das bases e na estruturação do processo de coleta e ingestão.

A documentação e o repositório permaneceram organizados para permitir a continuidade do trabalho nas próximas etapas, especialmente a preparação das bases para processamento, indexação e RAG.

### Pendências e bloqueios

* Finalização da coleta dos períodos históricos necessários.
* Validação dos volumes e da consistência das bases.
* Continuidade da integração das bases ao pipeline.
* Evolução das etapas de processamento, indexação e RAG.

### Próximo passo

* Continuar o trabalho da base agregada.
* Acompanhar a consolidação das demais bases.
* Finalizar e revisar a documentação do corpus e da ingestão.
* Apoiar a organização do repositório e a integração das contribuições do grupo.
* Preparar as bases para as próximas etapas de processamento e RAG.

### Uso de assistentes de IA

Utilizei IA como ferramenta de apoio durante a investigação das APIs, análise dos dados, organização da documentação, revisão dos arquivos e esclarecimento de dúvidas técnicas. As sugestões foram analisadas e ajustadas de acordo com os requisitos do projeto e as fontes oficiais utilizadas.


# Encontro 8 — 02/10/2026

### Atividades realizadas

Continuei acompanhando a evolução das diferentes frentes do projeto e atuando na **organização do planejamento, documentação e integração das contribuições do grupo**.

Com o avanço das implementações de ingestão, processamento, retrieval e geração de respostas, comecei a organizar melhor a estrutura geral do projeto e entender como essas partes poderiam se conectar em um fluxo único.

Também acompanhei as atividades relacionadas às bases e ao RAG, ajudando a identificar as próximas etapas e organizar as responsabilidades necessárias para a continuidade do desenvolvimento.

A partir dessa análise, comecei a estruturar a ideia do **Query Analyzer**, pensando em uma etapa capaz de interpretar a pergunta do usuário antes de definir qual caminho do sistema deveria ser utilizado.

### Resultado

O planejamento do projeto ficou mais organizado em relação às próximas etapas de integração.

Também foi iniciada a estruturação do Query Analyzer, com a ideia de separar a interpretação da pergunta da execução da consulta e da geração da resposta.

### Pendências e bloqueios

* Continuar a evolução do Query Analyzer.

* Integrar as diferentes partes do fluxo de consulta.

* Definir melhor o roteamento entre dados estruturados, RAG e consultas híbridas.

* Continuar a consolidação das bases e do pipeline.

### Próximo passo

* Continuar o desenvolvimento do Query Analyzer.

* Acompanhar a integração das bases e do RAG.

* Organizar as próximas etapas da arquitetura de consultas.

* Continuar a documentação e os acompanhamentos do projeto.

### Uso de assistentes de IA

Utilizei IA como apoio para entender e estruturar a arquitetura de consultas, revisar possibilidades de implementação, esclarecer dúvidas técnicas e organizar a documentação. As sugestões foram analisadas e adaptadas de acordo com a estrutura e os requisitos definidos pelo grupo.


# Encontro 9 — 05/10/2026

### Atividades realizadas

Continuei trabalhando na **organização da arquitetura de consultas, documentação e integração das diferentes partes do projeto**, acompanhando também a evolução das atividades realizadas pelos demais integrantes.

Avancei no desenvolvimento do **Query Analyzer**, criando uma estrutura para interpretar as perguntas e identificar qual tipo de consulta seria necessária.

Foram realizados testes com perguntas estruturadas, perguntas relacionadas a documentos e normas e perguntas que precisam combinar informações estruturadas com o conteúdo documental.

Também continuei organizando o planejamento das próximas etapas, principalmente a integração entre o Query Analyzer, o futuro Router e os componentes de RAG e consulta estruturada.

### Resultado

O Query Analyzer conseguiu identificar corretamente os principais tipos de perguntas testados, classificando os cenários como **structured, rag e hybrid**.

Com isso, ficou mais clara a separação entre a etapa de interpretação da pergunta e as etapas responsáveis pela busca, consulta e geração da resposta.

### Pendências e bloqueios

* Integrar o Query Analyzer ao fluxo principal.

* Estruturar o Router responsável pelo direcionamento das consultas.

* Definir a ferramenta de consulta dos dados estruturados.

* Continuar a integração entre as diferentes partes do sistema.

### Próximo passo

* Continuar a evolução do Query Analyzer.

* Iniciar a integração com o Router.

* Acompanhar a evolução do RAG e das bases estruturadas.

* Continuar organizando a documentação e o planejamento das próximas entregas.

### Uso de assistentes de IA

Utilizei IA como apoio no desenvolvimento e validação do Query Analyzer, principalmente para revisar estruturas, testar diferentes tipos de perguntas, esclarecer dúvidas de implementação e analisar possíveis soluções. As sugestões foram avaliadas e adaptadas conforme os requisitos do projeto.


# Encontro 10 — 07/10/2026

### Atividades realizadas

Continuei trabalhando na **organização da arquitetura, documentação e planejamento das próximas etapas do projeto**, acompanhando a evolução das diferentes frentes desenvolvidas pelo grupo.

A partir dos testes realizados com o Query Analyzer, avancei na definição de como a análise da pergunta poderá ser integrada ao restante do sistema.

Organizei o fluxo pensando em três possibilidades principais: **structured, rag e hybrid**, permitindo que cada pergunta seja encaminhada para o tipo de consulta mais adequado.

Também comecei a estruturar as próximas etapas relacionadas ao Router e à integração com os componentes que já foram desenvolvidos, buscando aproveitar o RAG existente sem duplicar funcionalidades.

Continuei ainda acompanhando e organizando as atividades do grupo, ajudando na definição dos próximos papéis, tarefas e pontos que precisam ser desenvolvidos.

### Resultado

A arquitetura de consultas ficou mais organizada, com uma separação mais clara entre interpretação, roteamento, execução e geração da resposta.

Também ficaram definidas as principais próximas etapas para integrar o Query Analyzer ao fluxo principal do projeto.

### Pendências e bloqueios

* Integração do Query Analyzer ao fluxo principal.

* Desenvolvimento do Router.

* Estruturação da consulta aos dados estruturados.

* Integração entre SQL, RAG e fluxo híbrido.

* Continuidade da documentação e organização do projeto.

### Próximo passo

* Avançar na implementação do Router.
* Integrar o Query Analyzer ao fluxo principal.
* Continuar a evolução das consultas estruturadas e híbridas.
* Acompanhar a integração das diferentes contribuições do grupo.
* Manter a documentação e o planejamento atualizados conforme o projeto evolui.

### Uso de assistentes de IA

Utilizei IA como apoio para analisar a arquitetura, esclarecer dúvidas técnicas, revisar as possibilidades de integração entre os componentes e organizar as próximas etapas do projeto. As sugestões foram avaliadas e adaptadas de acordo com o que já havia sido desenvolvido pelo grupo.


# Encontro 11 — 09/10/2026

### Atividades realizadas

Continuei trabalhando na **organização da arquitetura, documentação e planejamento das próximas etapas do projeto**, acompanhando a evolução dos componentes desenvolvidos pelo grupo e contribuindo para a definição do fluxo de consultas do sistema RAG de Contratações Públicas.

Dei continuidade ao trabalho relacionado ao **Query Analyzer**, responsável por interpretar as perguntas dos usuários e identificar a estratégia mais adequada para cada consulta. Avancei na organização dessa etapa, considerando as possibilidades de consultas estruturadas (*structured*), recuperação documental (*RAG*) e consultas híbridas (*hybrid*), que combinam informações estruturadas com conteúdo documental.

Também acompanhei a evolução da arquitetura com a integração do planejador, do executor e da rota híbrida, buscando manter uma separação clara entre interpretação da pergunta, definição da estratégia de busca, execução e geração da resposta. Continuei contribuindo com a organização técnica e a documentação para facilitar a compreensão do fluxo e a integração das diferentes partes desenvolvidas pelo grupo.

Outro ponto importante foi a participação nas discussões com o time sobre o **conjunto de buscas que o sistema deverá oferecer**. Debatemos que não seria necessariamente preciso manter toda a base de dados previamente armazenada e processada no projeto para responder às perguntas dos usuários. Também podemos considerar consultas sob demanda a APIs e arquivos externos que ainda não estejam incorporados ao sistema, conforme a necessidade de cada pergunta e a disponibilidade das fontes.

Essa discussão contribuiu para ampliar as possibilidades da arquitetura, considerando diferentes fontes de informação e estratégias de recuperação, sem limitar o funcionamento do sistema exclusivamente aos dados já ingeridos. A proposta é avaliar como essas consultas podem ser direcionadas de acordo com a pergunta, mantendo a organização do fluxo e a confiabilidade das informações utilizadas nas respostas.

Além disso, continuei auxiliando o time na organização das atividades, no debate sobre as decisões técnicas e no planejamento dos próximos passos, acompanhando as dependências entre os componentes e as necessidades de integração.

### Resultado

A arquitetura do sistema avançou com a evolução do Query Analyzer e a integração dos componentes de planejamento, execução e consulta híbrida.

As discussões sobre o conjunto de buscas também ampliaram a visão do grupo sobre as possibilidades de recuperação de informações, considerando não apenas as bases já integradas, mas também consultas sob demanda a APIs e arquivos externos.

Com isso, contribuí para a organização do fluxo de consultas, o alinhamento técnico entre as frentes de desenvolvimento e o planejamento das próximas etapas do projeto.

### Pendências e bloqueios

* Continuidade da evolução e validação do fluxo de consultas.
* Aprimoramento da interpretação das perguntas e da identificação dos filtros necessários.
* Evolução das consultas estruturadas e híbridas.
* Avaliação das possibilidades de consulta sob demanda a APIs e arquivos externos.
* Definição de critérios para selecionar as fontes de informação adequadas a cada pergunta.
* Continuidade da documentação e do alinhamento entre os componentes desenvolvidos pelo grupo.

### Próximo passo

* Acompanhar a evolução e a validação do fluxo completo de consultas.
* Contribuir para o planejamento das estratégias de busca e recuperação de informações.
* Aprofundar a discussão sobre consultas sob demanda a APIs e arquivos externos.
* Continuar apoiando a integração das diferentes contribuições do grupo.
* Manter a documentação e o planejamento atualizados conforme a arquitetura evoluir.

### Uso de assistentes de IA

Utilizei assistentes de IA como apoio à análise da arquitetura, à compreensão das possibilidades de integração entre os componentes, à organização da documentação e ao planejamento das próximas etapas. As sugestões foram avaliadas em conjunto com o contexto real do projeto e adaptadas conforme as decisões técnicas e o que já havia sido desenvolvido pelo grupo.
