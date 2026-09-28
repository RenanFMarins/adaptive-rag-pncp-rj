Resumo do dia - Encontro 1 - 2026-09-16 - (escrito em conjunto)

## Resumo do time no dia

**Entregamos hoje:**

* Criamos e configuramos o repositório da equipe, com os integrantes e o mentor.
* Estruturamos a arquitetura inicial do projeto e definimos a divisão de responsabilidades entre os integrantes.
* Criamos e revisamos os documentos iniciais de requisitos e Engenharia de Software.
* Configuramos a estrutura inicial do backend com FastAPI, SQLAlchemy, SQLite, Pydantic Settings e Uvicorn.
* Criamos o README.md, AGENTS.md, .gitignore e requirements.txt, deixando o ambiente inicial documentado e reproduzível.
* Criamos o PERSONAS.md, com três personas, nove perguntas de referência, rotas esperadas e tipos de consulta.
* Criamos a primeira versão do corpus_manifest.yaml, declarando as quatro bases: normativa, estruturada, conversacional e agregada, com suas fontes, formas de acesso e critérios iniciais de seleção.
* Iniciamos a definição e organização da base normativa, incluindo a seleção inicial das fontes e a estratégia de processamento dos documentos.
* Definimos a necessidade de coleta e processamento separado conforme a natureza de cada base.

**Ficou pendente:**

* Completar a seleção das fontes da base normativa, incluindo decretos estaduais e editais do RJ de 2025.
* Iniciar a coleta real dos documentos e dados das quatro bases.
* Criar o CORPUS_INVENTORY.md para registrar os documentos e dados efetivamente coletados.
* Implementar o fetch_corpus.py para automatizar a coleta, incluindo download, hash e registro de falhas.
* Iniciar o processamento dos documentos normativos, incluindo extração de texto, chunking e metadados.
* Implementar os Models SQLAlchemy e evoluir os módulos do backend.
* Iniciar a implementação da ingestão e preparação dos dados para o pipeline RAG.
* Preparar a estrutura de indexação e recuperação, incluindo busca semântica, BM25 e posterior fusão dos resultados.

**Bloqueios em aberto:**

* Instabilidade no PNCP durante a consulta e seleção das fontes.
* Ainda é necessário localizar e validar os decretos estaduais do RJ que serão utilizados na base normativa.
* Alguns detalhes da coleta das diferentes bases ainda precisam ser definidos durante os primeiros testes.

**Próximo passo (início do Encontro 2):**

* Começar a coleta real do corpus das quatro bases.
* Completar a lista de fontes da base normativa e iniciar o fetch_corpus.py.
* Criar e manter o CORPUS_INVENTORY.md com os documentos coletados.
* Iniciar a extração, processamento e chunking dos documentos normativos.
* Implementar os primeiros Models e módulos do backend conforme a arquitetura definida.
* Iniciar a preparação da ingestão para as demais bases e estruturar a futura indexação e recuperação híbrida.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na organização da documentação, estruturação do projeto, revisão da arquitetura, definição das personas e perguntas, organização do manifesto e esclarecimento de dúvidas técnicas.
* As sugestões foram revisadas e ajustadas pela equipe de acordo com o enunciado, as fontes do cenário e a arquitetura definida para o projeto.


# Resumo do dia - Encontro 2 - 2026-09-18

## Resumo do time no dia

**Entregamos hoje:**

* Iniciamos a coleta e validação dos dados reais das diferentes bases definidas no projeto.
* Evoluímos a integração com o PNCP, analisando os endpoints, formatos de resposta, paginação e formas de acesso aos dados e documentos.
* Iniciamos a implementação da coleta da base agregada, utilizando dados do Plano de Contratações Anual (PCA) e estruturando a camada de dados brutos (RAW).
* Definimos o fluxo inicial de coleta da base agregada: PNCP → coleta → controle de sincronização → detecção de alterações → RAW → banco de dados.

* Implementamos mecanismos de identificação de registros novos, atualizados e inalterados, mantendo o conteúdo original dos dados coletados.
* Avançamos na integração da base estruturada, realizando testes com contratos, contratações e documentos disponibilizados pelo PNCP.
* Iniciamos a implementação da autenticação da aplicação, com usuários, perfis de acesso, senha protegida e autenticação por JWT.
* Evoluímos a estrutura inicial do backend e a organização dos módulos de integração com o PNCP.
* Foram realizados testes automatizados e testes controlados com dados reais para validar a coleta, persistência e comportamento das integrações.

**Ficou pendente:**

* Ampliar a coleta real dos dados do PNCP para o recorte definido do projeto.
* Continuar a coleta e organização dos documentos das bases estruturada e agregada.
* Validar completamente os endpoints do PCA e demais recursos que apresentaram instabilidade.
* Continuar a integração entre os dados coletados e a estrutura definitiva do banco de dados.
* Avançar no processamento dos documentos, incluindo extração de texto, metadados e preparação para chunking.
* Continuar a implementação dos módulos de ingestão e preparação para o pipeline RAG.

**Bloqueios em aberto:**

* Instabilidade e respostas de erro do PNCP durante algumas consultas.
* Limitações e oscilações nos endpoints utilizados para coleta dos dados.
* Algumas fontes ainda precisam ser validadas com dados reais antes de serem incorporadas definitivamente ao corpus.

**Próximo passo (início do Encontro 3):**

* Continuar a coleta real das bases estruturada e agregada.
* Avançar na coleta dos valores homologados por item.
* Integrar os dados coletados com a estrutura persistente do projeto.
* Continuar a organização e processamento dos documentos obtidos no PNCP.
* Evoluir a integração entre coleta, banco de dados e futura ingestão no pipeline RAG.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na análise dos endpoints do PNCP, organização da arquitetura de coleta, modelagem dos dados, autenticação, tratamento de erros e criação dos testes.
* As sugestões foram analisadas, adaptadas e validadas pela equipe por meio de testes locais e consultas controladas às fontes oficiais.


# Resumo do dia - Encontro 3 - 2026-09-21

## Resumo do time no dia

**Entregamos hoje:**

* Continuamos a coleta e organização dos dados reais do PNCP, com foco na evolução das bases estruturada e agregada.
* Avançamos na base agregada, diferenciando os dados de planejamento do PCA dos dados efetivamente resultantes das contratações públicas.
* Implementamos a coleta de resultados homologados por item, incluindo quantidade homologada, valor unitário, valor total, fornecedor, situação e data do resultado.
* Realizamos uma coleta controlada de contratação do Estado do RJ, obtendo itens com resultados homologados e validando os valores diretamente com os dados disponibilizados pelo PNCP.
* Implementamos mecanismos de versionamento, identificação de registros inalterados e prevenção de duplicidades durante novas coletas.
* Avançamos na integração entre a base estruturada e a base agregada, utilizando as contratações coletadas para localizar os itens e seus respectivos resultados.

* Evoluímos a integração do PNCP com a aplicação, incluindo consultas de contratações, contratos, atas e documentos.

* Foram realizados downloads controlados de documentos oficiais disponibilizados pelo PNCP, preparando os arquivos para posterior extração e processamento.
* Avançamos na persistência dos dados coletados e na estruturação dos relacionamentos entre registros do PNCP e documentos utilizados pelo RAG.
* Continuamos a evolução da autenticação e da estrutura do backend da aplicação.
* Foram realizados testes automatizados para validar paginação, preservação dos dados originais, versionamento, integração e idempotência das coletas.

**Ficou pendente:**

* Ampliar o recorte da coleta para o conjunto definitivo de órgãos, modalidades e período do Estado do RJ.
* Continuar a validação dos endpoints do PNCP que apresentaram instabilidade.
* Completar a integração entre os dados estruturados e agregados.
* Continuar o processamento dos documentos baixados, incluindo extração de texto e preparação dos chunks.
* Definir e implementar as estruturas normalizadas a partir dos dados RAW.
* Continuar a preparação da indexação e recuperação híbrida para o pipeline RAG.

**Bloqueios em aberto:**

* Algumas consultas do PNCP apresentaram timeout e limitação de requisições.
* A disponibilidade dos endpoints varia conforme o tipo de consulta, exigindo tratamento específico para respostas paginadas, documentos e dados agregados.
* Ainda é necessário validar o relacionamento entre os dados do PCA e as contratações efetivamente realizadas.

**Próximo passo (início do Encontro 4):**

* Continuar a coleta integrada de contratação, itens e resultados homologados.
* Melhorar o tratamento de falhas, tentativas e checkpoints da coleta.
* Continuar a organização dos documentos coletados para o processamento do RAG.
* Avançar na normalização dos dados e na criação dos relacionamentos entre órgãos, contratações, itens, fornecedores e resultados.
* Continuar a preparação da estrutura de documentos, chunks e metadados para recuperação.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na análise da documentação do PNCP, definição do modelo de dados, organização da coleta, versionamento, tratamento de erros e criação dos testes.
* As sugestões foram revisadas e adaptadas pela equipe, sendo validadas por testes automatizados, análise dos dados retornados e consultas controladas às fontes oficiais.

# Resumo do dia - Encontro 4 - 2026-09-23

## Resumo do time no dia

**Entregamos hoje:**

* Evoluímos a coleta das bases estruturada e agregada, consolidando o fluxo de contratação → item → resultado homologado.
* Implementamos a coleta dos itens das contratações utilizando os dados já armazenados na camada RAW.
* Ajustamos a coleta dos resultados homologados para utilizar os itens previamente coletados, evitando consultas desnecessárias ao PNCP.
* Foram processados dados reais de contratações do Estado do RJ, incluindo centenas de itens e novos resultados homologados.
* Evoluímos o controle de checkpoints, permitindo acompanhar o progresso das coletas mesmo quando determinada consulta não retorna novos registros.
* Implementamos tratamento de tentativas e novas requisições para erros temporários do PNCP, incluindo respostas de limite de requisições, erros de servidor e timeout.
* Melhoramos o tratamento de respostas sem conteúdo e o registro de falhas durante a coleta.
* Avançamos na estrutura de persistência dos dados do PNCP, mantendo os registros originais e seus relacionamentos com os documentos.
* Avançamos também no processamento da base normativa, realizando a extração e organização dos documentos coletados.
* Foram processados 13 documentos normativos, sendo 1 lei, 7 decretos e 5 editais, gerando 784 pedaços para utilização no pipeline RAG.
* A Lei 14.133/2021 foi processada por artigo, os decretos por artigo e os editais por cláusula, mantendo os metadados necessários para identificação e rastreabilidade.
* Foram criados testes para validar o processamento da base normativa, com 9 testes passando.
* Continuamos a organização da arquitetura necessária para transformar os dados coletados em informações estruturadas e posteriormente utilizá-las no pipeline RAG.

**Ficou pendente:**

* Continuar a coleta e validação dos dados do PCA.
* Ampliar o recorte de contratações do Estado do RJ para o período e conjunto de órgãos definidos pelo projeto.
* Implementar a camada de normalização dos dados coletados.
* Estruturar os relacionamentos entre PCA, contratações, itens, resultados e fornecedores.
* Continuar o processamento dos documentos normativos e das demais bases, conforme necessário.
* Criar o CORPUS_INVENTORY.md com os documentos e dados efetivamente coletados.
* Avançar na indexação e recuperação híbrida dos documentos.

**Bloqueios em aberto:**

* O PNCP continua apresentando instabilidade e timeout em algumas consultas.
* Ainda existem pontos a validar no relacionamento entre os dados do PCA e as contratações efetivamente realizadas.
* Durante o processamento da base normativa, foi necessário ajustar as bibliotecas do ambiente e tratar diferenças de codificação em arquivos utilizados nos testes.
* A ampliação da coleta exige controle de volume, paginação, limites de requisição e tratamento de falhas.

**Próximo passo (início do próximo encontro):**

* Retomar a coleta do PCA e validar os dados obtidos.
* Ampliar gradualmente o corpus de contratações e resultados do Estado do RJ.
* Iniciar a normalização dos dados armazenados na camada RAW.
* Continuar o processamento e validação dos documentos da base normativa.
* Criar o CORPUS_INVENTORY.md e organizar o inventário dos documentos coletados.
* Definir os relacionamentos necessários para manter a rastreabilidade entre a fonte original e os dados processados.
* Continuar a transformação dos documentos coletados em documentos processáveis pelo pipeline RAG.
* Avançar na implementação da recuperação e preparação do contexto para geração das respostas.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na revisão da arquitetura de coleta, análise dos dados retornados pelo PNCP, modelagem dos relacionamentos, tratamento de erros, implementação de retries, processamento dos documentos e criação dos testes.
* As sugestões foram revisadas e adaptadas pela equipe, com validação por meio de testes automatizados, análise dos registros coletados e consultas controladas às fontes oficiais.

