# Resumo do dia - Encontro 1 - 2026-09-16 - (escrito em conjunto)

## Resumo do time no dia

**Entregamos hoje:**

* Criamos e configuramos o repositório da equipe, com os integrantes e o mentor.
* Estruturamos a arquitetura inicial do projeto e definimos a divisão de responsabilidades entre os integrantes.
* Criamos e revisamos os documentos iniciais de requisitos e Engenharia de Software.
* Configuramos a estrutura inicial do backend com FastAPI, SQLAlchemy, SQLite, Pydantic Settings e Uvicorn.
* Criamos o README.md, AGENTS.md, .gitignore e requirements.txt, deixando o ambiente inicial documentado e reproduzível.
* Criamos o PERSONAS.md, com três personas, nove perguntas de referência, rotas esperadas e tipos de consulta.
* Criamos a primeira versão do corpus_manifest.yaml, declarando as quatro bases: normativa, estruturada, conversacional e agregada, com suas fontes, formas de acesso e critérios iniciais de seleção.
* Definimos a arquitetura inicial do fluxo RAG, incluindo coleta e versionamento do corpus, ingestão, indexação, roteamento, recuperação híbrida e geração.
* Iniciamos a definição e organização da base normativa, incluindo a seleção inicial das fontes e a estratégia de processamento dos documentos.
* Definimos a necessidade de coleta e processamento separado conforme a natureza de cada base.
* Iniciamos a análise das necessidades de coleta das bases estruturada e agregada e dos recursos disponibilizados pelo PNCP.

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
* Avançamos na definição das fontes da base normativa, incluindo a substituição da fonte da Lei 14.133/2021 para o Planalto e a identificação dos decretos estaduais do RJ.
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
* Algumas fontes oficiais apresentaram restrições a downloads automatizados, exigindo alternativas de coleta e validação.

**Próximo passo (início do Encontro 3):**

* Continuar a coleta real das bases estruturada e agregada.
* Avançar na coleta dos valores homologados por item.
* Integrar os dados coletados com a estrutura persistente do projeto.
* Continuar a organização e processamento dos documentos obtidos no PNCP.
* Evoluir a integração entre coleta, banco de dados e futura ingestão no pipeline RAG.
* Avançar na coleta e processamento da base normativa.

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
* Avançamos na coleta da base normativa, obtendo a Lei 14.133/2021, cinco editais e sete decretos estaduais, totalizando 13 documentos.
* Foram estruturados os primeiros módulos específicos para coleta e processamento da base normativa.
* Foram realizados testes automatizados para validar paginação, preservação dos dados originais, versionamento, integração e idempotência das coletas.

**Ficou pendente:**

* Ampliar o recorte da coleta para o conjunto definitivo de órgãos, modalidades e período do Estado do RJ.
* Continuar a validação dos endpoints do PNCP que apresentaram instabilidade.
* Completar a integração entre os dados estruturados e agregados.
* Continuar o processamento dos documentos baixados, incluindo extração de texto e preparação dos chunks.
* Definir e implementar as estruturas normalizadas a partir dos dados RAW.
* Continuar a preparação da indexação e recuperação híbrida para o pipeline RAG.
* Finalizar a validação e o processamento dos documentos da base normativa.

**Bloqueios em aberto:**

* Algumas consultas do PNCP apresentaram timeout e limitação de requisições.
* A disponibilidade dos endpoints varia conforme o tipo de consulta, exigindo tratamento específico para respostas paginadas, documentos e dados agregados.
* Ainda é necessário validar o relacionamento entre os dados do PCA e as contratações efetivamente realizadas.
* Durante a coleta e processamento foram identificadas questões relacionadas a certificados, caminhos de arquivos e dependências do ambiente.

**Próximo passo (início do Encontro 4):**

* Continuar a coleta integrada de contratação, itens e resultados homologados.
* Melhorar o tratamento de falhas, tentativas e checkpoints da coleta.
* Continuar a organização dos documentos coletados para o processamento do RAG.
* Avançar na normalização dos dados e na criação dos relacionamentos entre órgãos, contratações, itens, fornecedores e resultados.
* Continuar a preparação da estrutura de documentos, chunks e metadados para recuperação.
* Finalizar o processamento da base normativa e validar os documentos e metadados coletados.

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

**Próximo passo (início do Encontro 5):**

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

# Resumo do dia - Encontro 5 - 2026-09-25

## Resumo do time no dia

**Entregamos hoje:**

* Avançamos na organização e documentação do corpus, mantendo o repositório alinhado entre código, documentação, arquivos de coleta e materiais de acompanhamento.
* Consolidamos o `CORPUS_INVENTORY.md` a partir dos dados reais coletados, registrando versões, arquivos, tamanhos, hashes e situação da coleta da base normativa.
* A base normativa permaneceu com 13 documentos coletados, sem falhas, incluindo 1 lei, 7 decretos estaduais e 5 editais.
* Evoluímos o controle de versões do corpus, permitindo gerar novas versões e registrar diferenças entre versões sem sobrescrever os dados anteriores.
* Ajustamos o cálculo de hash do conteúdo da Lei 14.133/2021 para desconsiderar elementos dinâmicos do HTML oficial, evitando alterações falsas na detecção de mudanças.
* Realizamos uma verificação das perguntas das personas em relação às fontes normativas, garantindo que as questões previstas possuíssem documentos de referência.
* Identificamos dados pessoais presentes nos documentos normativos e implementamos mascaramento de CPF e telefone nos dados processados, mantendo informações necessárias para o contexto da contratação.
* Após o reprocessamento, foram realizados testes para verificar a ausência dos dados mascarados e a identificação dos chunks que continham dados pessoais.
* Avançamos na coleta e preparação dos dados de contratos e contratações, incluindo a definição de uma estratégia para ampliar o corpus histórico do Estado do RJ.
* Na base agregada, avançamos na estratégia de expansão para diferentes períodos, mantendo a preservação dos dados RAW antes da normalização.
* Foram realizados novos testes de integração entre coleta, persistência, documentação e processamento.

**Ficou pendente:**

* Continuar a expansão histórica das bases estruturada e agregada.
* Completar a coleta de PCA para os períodos definidos.
* Continuar a coleta de contratos, itens, resultados homologados e demais recursos necessários.
* Integrar os dados coletados às estruturas normalizadas.
* Finalizar a organização dos logs estruturados e observabilidade da ingestão.
* Definir a estratégia final para os arquivos processados e sua disponibilização no repositório.
* Continuar a preparação da indexação e recuperação híbrida.
* Integrar as diferentes bases ao fluxo de consulta e geração do RAG.

**Bloqueios em aberto:**

* O PNCP continua apresentando limitações de volume, paginação, timeout e limite de requisições.
* A coleta histórica exige uma estratégia de divisão por períodos e checkpoints para evitar perda de dados ou sobrecarga das consultas.
* Alguns componentes de observabilidade ainda precisam ser integrados à estrutura definitiva do projeto.
* A definição do relacionamento entre PCA e contratações continua exigindo validação devido à ausência de uma chave direta em determinadas situações.

**Próximo passo (início do Encontro 6):**

* Continuar a expansão histórica dos dados estruturados e agregados.
* Avançar na coleta por períodos e checkpoints.
* Continuar a coleta e processamento dos documentos de contratos e contratações.
* Finalizar a documentação e inventário das bases.
* Evoluir a estrutura de observabilidade e auditoria das coletas.
* Avançar na preparação da recuperação híbrida e integração com o pipeline RAG.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na análise da estratégia de expansão do corpus, organização do inventário, tratamento de dados pessoais, investigação de alterações de conteúdo, documentação e revisão das estruturas de ingestão.
* As sugestões foram avaliadas e validadas pela equipe por meio dos dados coletados, testes automatizados e verificações realizadas no repositório.

# Resumo do dia - Encontro 6 - 2026-09-28

## Resumo do time no dia

**Entregamos hoje:**

* Avançamos significativamente na expansão e auditoria dos dados RAW das bases estruturada e agregada, mantendo os dados originais e sua rastreabilidade.
* Ampliamos a coleta de contratos do Estado do RJ para o período de 01/01/2023 a 26/09/2026, utilizando diferentes modalidades e controle por períodos.
* No recorte do primeiro trimestre de 2023, foram coletados 2.024 contratos e, na ampliação posterior do período, mais 174.457 registros, totalizando 176.481 contratos únicos no conjunto coletado.
* Para o primeiro trimestre de 2023, foram coletados 4.804 itens de contratos e identificados 3.669 resultados homologados.
* Foram registradas 1.378 consultas de empenhos com execução concluída, mas sem registros retornados pelo PNCP, mantendo a ausência registrada para auditoria.
* Avançamos na coleta do PCA de 2023 para os órgãos identificados, totalizando 195 planos, 49.063 itens e 61 órgãos com checkpoint concluído.
* Também realizamos uma coleta inicial de atas de registro de preços, com 65.671 ocorrências e 36.597 registros únicos, mantendo essa fonte fora do snapshot trimestral por ainda estar em processo de ampliação.
* Criamos um snapshot imutável do primeiro trimestre de 2023, preservando os dados RAW, hashes, inventário, estrutura do banco e informações necessárias para restauração e auditoria.
* Registramos o snapshot com SQLite, dump SQL, inventário CSV e hashes, além do registro privado da versão no GitHub.
* Realizamos verificações de integridade, incluindo chaves estrangeiras, restauração do banco, contagens e hashes.
* Foram executados 69 testes automatizados relacionados à coleta, checkpoints, retries, respostas HTTP, preservação dos payloads, detecção de alterações e integridade.
* Mantivemos o controle de fontes no manifesto e o acompanhamento dos resultados das coletas.
* Avançamos na preparação das bases para as etapas posteriores de normalização, indexação e recuperação.

**Ficou pendente:**

* Continuar a coleta de contratos, itens, resultados e empenhos dos períodos restantes.
* Expandir a coleta de PCA para 2024, 2025 e 2026.
* Continuar a coleta completa das atas de registro de preços.
* Implementar a normalização dos dados RAW para as estruturas analíticas necessárias.
* Definir e implementar os relacionamentos entre organizações, unidades, fornecedores, PCA, contratações, itens, resultados e demais entidades.
* Continuar o processamento dos documentos de contratos e contratações para extração de texto e criação de chunks.
* Avançar na indexação e recuperação híbrida.
* Integrar as bases coletadas ao fluxo completo de consulta e geração do RAG.

**Bloqueios em aberto:**

* O volume de dados e as limitações do PNCP exigem execução por períodos, modalidades, páginas e checkpoints.
* Algumas consultas apresentam timeout, limite de requisições ou ausência de registros, exigindo tratamento e auditoria específicos.
* A coleta completa de algumas fontes, como atas de registro de preços, ainda precisa ser ampliada antes de entrar nos snapshots definitivos.
* A normalização ainda depende da consolidação e validação das relações entre as diferentes fontes.

**Próximo passo (início do Encontro 7):**

* Retomar e ampliar as coletas dos períodos restantes.
* Continuar a coleta de contratos, itens, resultados e empenhos.
* Avançar na coleta de PCA dos demais anos.
* Continuar a expansão das fontes agregadas e completar as fontes ainda parciais.
* Iniciar a normalização dos dados preservados na camada RAW.
* Continuar o processamento dos documentos e preparação dos chunks.
* Avançar na indexação, recuperação híbrida e integração com a geração de respostas.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na análise dos endpoints, planejamento da expansão histórica, tratamento das limitações do PNCP, modelagem dos dados, definição dos checkpoints, testes de integridade e organização dos snapshots.
* As sugestões foram revisadas e validadas pela equipe por meio das execuções reais, testes automatizados, auditorias dos dados e verificações de integridade.

# Resumo do dia - Encontro 7 - 2026-09-30

## Resumo do time no dia

**Entregamos hoje:**

* Continuamos a evolução da ingestão e do processamento dos dados coletados, mantendo a preservação dos dados RAW e a rastreabilidade das fontes.
* Avançamos na integração entre coleta, persistência, processamento, recuperação e geração de respostas.
* Evoluímos o processamento de documentos oficiais do PNCP, incluindo documentos em PDF e arquivos compactados, utilizando extração de texto e Docling para documentos que exigem tratamento adicional.
* Foram processados documentos reais, resultando em textos e chunks preparados para a etapa de recuperação.
* Implementamos controle de versão do corpus e identificadores determinísticos para os chunks, permitindo ingestão idempotente e reaproveitamento de conteúdos já processados.
* Na execução validada, foram lidos 3 textos, criados 2 documentos e gerados 55 chunks, com 34 chunks reutilizados.
* Validamos a recuperação híbrida utilizando BM25 para busca lexical e FAISS para busca vetorial, com fusão dos resultados por RRF.
* Avançamos na geração de respostas fundamentadas nos documentos recuperados, mantendo evidências numeradas e metadados de rastreabilidade.
* Implementamos a persistência do fluxo de consulta e resposta, relacionando Query, Response, ResponseSource e DocumentChunk.
* Foram persistidos cinco chunks na ordem final definida pelo RRF, mantendo a rastreabilidade das evidências utilizadas na resposta.
* Foram executados testes de integração relacionados à recuperação híbrida, geração e serviços de consulta, com os testes correspondentes passando.
* Continuamos a organização e documentação do repositório, integrando as contribuições das diferentes frentes do grupo.
* Mantivemos a evolução das bases estruturada e agregada e a preparação das demais fontes para integração ao fluxo completo do RAG.

**Ficou pendente:**

* Continuar a expansão e validação do corpus histórico.
* Finalizar as coletas dos períodos e fontes ainda pendentes.
* Continuar a normalização dos dados RAW e estruturar as entidades necessárias para consulta.
* Ampliar o processamento dos documentos das bases estruturada, agregada e conversacional.
* Continuar a indexação dos documentos e chunks produzidos.
* Integrar definitivamente o roteamento entre as quatro bases ao fluxo de consulta.
* Evoluir a avaliação do RAG, incluindo testes de recuperação, geração, rastreabilidade e qualidade das respostas.
* Continuar a preparação do sistema para o cenário completo de demonstração.

**Bloqueios em aberto:**

* A expansão do corpus continua condicionada às limitações de volume, paginação, timeout e limites de requisição do PNCP.
* Algumas fontes ainda estão em processo de ampliação e validação antes de serem consideradas completas.
* A integração completa das quatro bases ao roteamento e à consulta ainda depende da consolidação das estruturas de processamento e indexação.

**Próximo passo:**

* Continuar a expansão e consolidação do corpus.
* Finalizar as coletas e validações das bases.
* Avançar na normalização e indexação dos dados e documentos.
* Integrar as quatro bases ao roteamento e à recuperação híbrida.
* Evoluir a geração de respostas fundamentadas e a rastreabilidade das evidências.
* Ampliar os testes e a avaliação do pipeline RAG.
* Preparar a integração final para as próximas etapas do desafio e da demonstração.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na análise técnica, revisão da arquitetura, investigação das APIs, organização do corpus, tratamento dos dados, processamento documental, recuperação híbrida, geração de respostas, testes e documentação.
* As sugestões foram analisadas e adaptadas pela equipe, sendo validadas por meio de testes, execuções controladas, análise dos dados coletados e verificação dos resultados no projeto.
