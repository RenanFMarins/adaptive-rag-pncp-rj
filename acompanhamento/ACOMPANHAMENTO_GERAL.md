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

# Resumo do dia - Encontro 8 - 2026-10-02

## Resumo do time no dia

****Entregamos hoje:****

* Avançamos na integração das diferentes frentes do projeto, com evolução simultânea das bases, ingestão, processamento, recuperação, geração e organização da aplicação.
* Evoluímos a coleta e persistência dos dados estruturados e agregados, mantendo a organização dos dados RAW e dos mecanismos de controle utilizados nas coletas.
* Continuamos a coleta e processamento dos dados do PNCP, incluindo a organização das informações de contratos, contratações, itens e resultados para as etapas posteriores de integração.
* Avançamos na preparação da recuperação documental, incluindo testes de ingestão e organização dos documentos para utilização no mecanismo de busca híbrida.
* Integramos o fluxo de recuperação e geração de respostas à API da aplicação por meio do endpoint `POST /query/generate`, utilizando a estrutura de RAG já desenvolvida.
* Validamos consultas reais pela API e pelo Swagger, com respostas geradas a partir dos documentos recuperados e respectivas evidências.
* A resposta gerada passou a manter a rastreabilidade das fontes, incluindo posição dos resultados, identificadores dos chunks, relevância e metadados.
* Avançamos na persistência do fluxo de consulta e resposta, relacionando consultas, respostas e fontes utilizadas durante a geração.
* Evoluímos a observabilidade da ingestão com a implementação de logs estruturados em JSONL, incluindo `run_id`, etapas executadas, duração das operações e registro de falhas.
* Corrigimos um problema de idempotência relacionado à seleção indevida de arquivos `.meta.json` durante o processamento.
* Foram adicionados testes relacionados ao logging, idempotência e comportamento da ingestão, elevando a suíte de testes de 37 para 50 testes.
* Identificamos e corrigimos dados processados anteriormente sem o campo de vigência, realizando o reprocessamento completo dos 794 chunks da base normativa.
* Avançamos na organização da arquitetura de consulta, iniciando a definição de um componente responsável por interpretar a pergunta do usuário antes da execução da busca ou consulta.
* Foram realizados diagnósticos e auditorias da coleta histórica do PNCP, incluindo análise de cobertura, checkpoints, integridade e registros ainda pendentes.

****Ficou pendente:****

* Continuar a expansão e auditoria das bases estruturada e agregada.
* Completar as coletas históricas ainda pendentes e validar a cobertura dos dados.
* Continuar a integração dos dados RAW com as estruturas necessárias para consultas.
* Ampliar o processamento e indexação dos documentos das diferentes bases.
* Continuar a evolução do fluxo de recuperação e geração de respostas.
* Integrar o componente de interpretação das perguntas ao fluxo principal da aplicação.
* Estruturar o roteamento entre consultas estruturadas, RAG e consultas que necessitem combinar as duas abordagens.
* Continuar a evolução dos mecanismos de auditoria, observabilidade e rastreabilidade.

****Bloqueios em aberto:****

* O PNCP continua apresentando limitações e diferenças de cobertura entre os recursos consultados, exigindo auditoria dos checkpoints e dos registros pendentes.
* Parte da coleta histórica ainda apresenta resultados parciais e precisa ser concluída antes do fechamento definitivo dos snapshots.
* A integração completa entre as diferentes formas de consulta ainda depende da definição e implementação do roteamento da aplicação.

****Próximo passo (início do Encontro 9):****

* Continuar a coleta e auditoria dos dados históricos do PNCP.
* Completar os registros pendentes e validar a cobertura das bases estruturada e agregada.
* Continuar a integração da ingestão e indexação dos documentos.
* Evoluir o componente de interpretação das perguntas e iniciar sua integração com o roteamento.
* Estruturar as consultas estruturadas e a integração com o RAG existente.
* Continuar os testes de recuperação, geração, persistência e rastreabilidade.

****Uso de assistentes de IA:****

* Utilizamos assistentes de IA como apoio na análise dos dados coletados, auditoria de bancos e checkpoints, investigação das APIs, organização da arquitetura de consulta, implementação dos logs, testes, integração do RAG com a API e documentação.

* As sugestões foram analisadas e adaptadas pela equipe, sendo validadas por meio de testes automatizados, consultas reais, auditorias dos dados e execuções controladas.

# Resumo do dia - Encontro 9 - 2026-10-05

## Resumo do time no dia

****Entregamos hoje:****

* Avançamos na consolidação das bases coletadas e no fechamento de etapas importantes da ingestão e preparação do corpus.
* Finalizamos a cobertura dos resultados homologados dos itens do recorte trabalhado, chegando a 100% dos itens identificados com resultado, sem registros pendentes nesse conjunto.
* Avançamos na coleta e organização dos dados do PCA, incluindo a consulta de novos órgãos, identificação dos planos disponíveis e integração dos resultados ao conjunto de dados já coletado.
* Foram identificados novos planos e itens associados aos dados do PCA, ampliando a base agregada para as próximas etapas de processamento.
* Iniciamos uma nova frente de coleta de atas de registro de preços, estruturando checkpoint próprio, seleção das unidades e registro dos dados em formato adequado para posterior auditoria e integração.
* Avançamos na definição de um fluxo reproduzível para as novas coletas, com checkpoints, retomada segura, atualização dos registros e geração de logs.
* A base normativa processada foi integrada ao projeto com 794 chunks, mantendo os metadados, rastreabilidade e regras de processamento definidas anteriormente.
* Foram realizados testes de auditoria da base normativa, verificando duplicidades, tamanho dos chunks e consistência dos dados processados.
* A base normativa foi considerada congelada para a etapa de benchmark, permitindo iniciar a definição de perguntas de referência para avaliação do sistema.
* Avançamos no processamento e ingestão das demais fontes documentais e na preparação da recuperação para testes.
* Evoluímos a arquitetura de consulta com o desenvolvimento do Query Analyzer, responsável por interpretar a pergunta antes de definir a estratégia de consulta.
* Foram realizados testes com perguntas estruturadas, documentais/normativas e híbridas, validando a identificação de diferentes necessidades de consulta.
* O componente passou a diferenciar cenários de consulta estruturada, RAG e híbrida, preparando a integração futura com o Router e as ferramentas de consulta.
* Avançamos na organização da documentação, integração das contribuições do grupo e alinhamento das próximas etapas do projeto.
* Foram realizadas apresentações e discussões com a equipe e orientação do projeto para avaliar o progresso e os próximos passos.

****Ficou pendente:****

* Continuar a coleta e auditoria das atas de registro de preços.
* Finalizar as etapas restantes da coleta histórica e organizar os artefatos para release.
* Continuar a expansão e validação das bases estruturada e agregada.
* Integrar o Query Analyzer ao fluxo principal da aplicação.
* Implementar o Router responsável por encaminhar cada pergunta para a estratégia adequada.
* Estruturar a ferramenta de consulta aos dados estruturados e definir as regras de execução segura das consultas.
* Continuar a integração entre as bases, recuperação, geração e persistência.
* Iniciar e ampliar o benchmark com perguntas de referência para avaliar recuperação e qualidade das respostas.

****Bloqueios em aberto:****

* A coleta de algumas fontes ainda está em andamento e depende da execução por unidades, períodos e checkpoints.
* A estrutura de roteamento ainda não está implementada, sendo necessário integrar o Query Analyzer às etapas seguintes da consulta.
* O componente de Router ainda precisa ser estruturado para conectar as perguntas às ferramentas de RAG e consulta estruturada.
* A avaliação sistemática do RAG ainda depende da definição e execução do conjunto de perguntas de benchmark.

****Próximo passo (início do Encontro 10):****

* Continuar e auditar a coleta das atas de registro de preços e demais fontes ainda pendentes.
* Organizar os artefatos finais das bases coletadas e preparar os próximos releases.
* Integrar o Query Analyzer ao fluxo principal.
* Iniciar a implementação do Router e das ferramentas de consulta estruturada.
* Integrar o roteamento com o RAG já existente.
* Continuar o benchmark das perguntas de referência e avaliar recuperação, geração e rastreabilidade.
* Avançar na integração completa do pipeline para a demonstração final.

****Uso de assistentes de IA:****

* Utilizamos assistentes de IA como apoio na auditoria das bases, análise de cobertura, organização das coletas, definição de checkpoints, investigação das APIs, desenvolvimento e validação do Query Analyzer, estruturação da arquitetura de consulta, criação de testes e documentação.

* As sugestões foram analisadas e adaptadas pela equipe, sendo validadas por meio das execuções reais, testes automatizados, auditorias dos dados e resultados obtidos no projeto.

# Resumo do dia - Encontro 10 - 2026-10-07

## Resumo do time no dia

***Entregamos hoje:****

* Avançamos na consolidação da nova arquitetura de consulta do projeto, definindo com mais clareza a separação entre interpretação da pergunta, roteamento, recuperação, geração e auditoria.
* Atualizamos as branches com a principal e incorporamos os novos componentes da busca híbrida, utilizando FTS5 para busca por palavras-chave, FAISS para busca semântica e RRF para combinação dos resultados.
* Foram executados os 50 testes da base normativa após a atualização do código, confirmando que as alterações da busca híbrida não quebraram o funcionamento existente.
* Avançamos na implementação e validação do FTS5, complementando a recuperação semântica já existente e realizando testes sobre os resultados retornados.
* Foram realizados ajustes no prompt e no contexto enviado à LLM, incluindo limitação do tamanho das respostas, padronização das citações no formato `[1]`, `[2]` e instruções para evitar a mistura de evidências de processos diferentes.
* O contexto enviado para a geração passou a apresentar identificadores mais claros das evidências, incluindo `numeroControlePNCP`, título do documento e URL de origem.
* Avançamos na definição do Query Analyzer, organizando a interpretação das perguntas em três possibilidades principais: `structured`, `rag` e `hybrid`.
* Foram organizadas as próximas etapas relacionadas ao Router, que deverá encaminhar cada pergunta para a estratégia de consulta adequada, aproveitando os componentes RAG já desenvolvidos.
* Avançamos na implementação da camada de auditabilidade, utilizando um `trace_id` único para cada consulta e registrando as informações da execução em arquivos próprios de auditoria.
* A auditoria passou a registrar informações relacionadas à pergunta, estratégia de retrieval, chunks recuperados, scores de BM25 e FAISS, RRF, contexto, prompt, resposta, tempo de processamento, persistência e possíveis erros.
* Avançamos na integração do Guardrail ao fluxo de geração, fazendo com que perguntas fora do escopo definido possam ser bloqueadas antes da recuperação das evidências e da chamada à LLM.
* Foi realizado um teste com uma pergunta de recusa comercial, sendo bloqueada corretamente pelo Guardrail. A resposta não realizou retrieval nem geração pela LLM, apresentando `sources: []` e `prompt: null`.
* As consultas bloqueadas também passaram a permanecer rastreáveis por meio da auditoria, registrando o bloqueio, o motivo da recusa e a mensagem retornada.
* Foram mantidas as regras de sanitização dos registros de auditoria para evitar o armazenamento de informações sensíveis, como tokens, chaves de API e dados de autorização.
* Identificamos uma pendência na base normativa: os 794 chunks processados ainda não estão carregados na tabela `document_chunks`, utilizada pela busca híbrida, impedindo que esses conteúdos sejam recuperados atualmente pelo FTS5 e FAISS.

****Ficou pendente:****

* Integrar o Query Analyzer ao fluxo principal da aplicação.
* Implementar e integrar o Router responsável por encaminhar cada pergunta para a estratégia adequada.
* Estruturar a ferramenta de consulta aos dados estruturados e definir as regras de execução segura das consultas.
* Integrar as rotas `structured`, `rag` e `hybrid` aos respectivos componentes de consulta.
* Finalizar a integração dos Guardrails ao fluxo completo e ampliar os testes de bloqueio.
* Carregar e disponibilizar os 794 chunks da base normativa na tabela utilizada pela busca híbrida.
* Definir e executar a indexação da base normativa no FTS5 e FAISS após sua disponibilização no banco.
* Continuar os testes de recuperação, geração, persistência e auditabilidade.
* Continuar a documentação e organização das próximas etapas do projeto.

****Bloqueios em aberto:****

* O Query Analyzer e o Router ainda não estão integrados ao fluxo principal da aplicação.
* A ferramenta de consulta aos dados estruturados ainda precisa ser implementada para permitir que perguntas quantitativas sejam respondidas diretamente pela base estruturada.
* Os 794 chunks da base normativa ainda não estão na tabela utilizada pela busca híbrida, fazendo com que os conteúdos processados não estejam disponíveis para recuperação.
* A integração completa do Guardrail depende da conexão com as etapas seguintes da arquitetura, principalmente Analyzer, Router e ferramentas de consulta.

****Próximo passo (início do Encontro 11):****

* Integrar o Query Analyzer ao fluxo principal da aplicação.
* Avançar na implementação do Router e conectar as rotas `structured`, `rag` e `hybrid`.
* Estruturar a ferramenta de consulta aos dados estruturados com execução segura e somente leitura.
* Continuar a integração do Guardrail antes das etapas de consulta e recuperação.
* Carregar os 794 chunks da base normativa em `document_chunks` e realizar a indexação necessária para a busca híbrida.
* Continuar os testes de recuperação, geração e auditoria, incluindo consultas bloqueadas.
* Integrar as diferentes frentes do pipeline e preparar a arquitetura para a demonstração final.

****Uso de assistentes de IA:****

* Utilizamos assistentes de IA como apoio na análise e evolução da arquitetura, desenvolvimento e validação do Query Analyzer, implementação e testes da recuperação híbrida, análise dos Guardrails, estruturação da auditabilidade, revisão de prompts e organização das próximas etapas do projeto.

* As sugestões foram analisadas e adaptadas pela equipe de acordo com o código existente, os requisitos do projeto e as decisões tomadas durante o desenvolvimento, sendo validadas por meio de testes, execuções reais e auditorias dos resultados.


# Resumo do dia — Encontro 11 — 2026-10-09

**## Resumo do time no dia**

**\*\*\*Entregamos hoje:\*\*\***

* Avançamos na definição e integração da arquitetura de consultas, organizando o fluxo entre interpretação da pergunta, roteamento, consulta estruturada, recuperação documental e geração da resposta.
* Foram realizados testes manuais do Query Analyzer com sete perguntas. Seis classificações foram consideradas coerentes, enquanto uma pergunta ambígua — “Qual é o valor do contrato?” — foi classificada incorretamente como uma operação de soma, evidenciando a necessidade de aprimorar a interpretação da intenção do usuário.
* Foram testadas consultas estruturadas envolvendo quantidade de contratos, objeto, data, município, número de contrato e órgão responsável.
* Nas verificações realizadas no banco, foram identificados 6.021 contratos distintos publicados em agosto de 2026 e 3.855 registros referentes ao município do Rio de Janeiro no mesmo período.
* Foi testada uma consulta híbrida que combinava contratos publicados em agosto de 2026 no município do Rio de Janeiro com a busca por cláusulas de penalidade por atraso. A estratégia foi classificada como híbrida, com necessidade de SQL e RAG, mas foram identificadas falhas na extração dos termos documentais e inconsistências nos filtros temporais.
* Avançamos na análise da integração entre Query Analyzer, Router, execução SQL e recuperação RAG, identificando ajustes necessários para que cada pergunta seja encaminhada à estratégia adequada.
* Ana Karina e Ester atuaram conjuntamente na persistência da base normativa. Os 794 chunks, distribuídos em 13 documentos, foram carregados na tabela `document_chunks`, tornando-os disponíveis para recuperação pela aplicação.
* O carregador da base normativa foi estruturado para evitar duplicações. Em uma segunda execução, os 794 chunks já existentes foram reconhecidos, sem novas inserções.
* Foram corrigidos problemas relacionados a títulos extensos de editais e à identificação de datas de vigência ausentes, com a inclusão de avisos para facilitar a identificação de registros incompletos.
* Após o reprocessamento, os textos e identificadores dos 794 chunks foram preservados. Em 27 chunks de um edital, foi corrigida a numeração que estava ausente.
* Foram realizados testes de recuperação documental, incluindo uma consulta sobre o prazo de vigência da ata de registro de preços, que recuperou corretamente o Art. 84 da Lei nº 14.133/2021.
* A suíte de testes da frente normativa passou de 50 para 81 testes, conforme os relatos de Ana Karina e Ester.
* Avançamos na integração das estratégias `structured`, `rag` e `hybrid`, com continuidade do desenvolvimento e dos testes dos endpoints de consulta.
* Luiz Felipe contribuiu para a organização da arquitetura, da documentação e do planejamento técnico, apoiando o alinhamento das etapas do pipeline e a discussão sobre consultas estruturadas, recuperação documental e integração dos componentes.
* A equipe identificou que a recuperação da base normativa dependia da persistência dos chunks na tabela utilizada pela aplicação, problema tratado durante o encontro com o carregamento dos registros.

**\*\*\*Ficou pendente:\*\*\***

* Corrigir a classificação de perguntas ambíguas no Query Analyzer, diferenciando consultas sobre o valor de um contrato específico de solicitações de soma ou agregação.
* Aprimorar a extração de termos documentais nas consultas híbridas, incluindo expressões como penalidade e atraso.
* Padronizar os filtros temporais, evitando inconsistências entre campos como `ano`, `mes`, `periodo_inicio` e `periodo_fim`.
* Concluir a integração do Query Analyzer e do Router com as ferramentas de consulta estruturada e recuperação RAG.
* Finalizar a indexação FAISS da base normativa e validar sua integração com o FTS5 e a busca híbrida.
* Preparar e executar as nove perguntas de referência previstas em `eval/questions.json`.
* Ampliar os testes de regressão para as rotas estruturadas, documentais e híbridas.
* Continuar a documentação da arquitetura e organizar os critérios de seleção da fonte de informação para cada tipo de pergunta.

**\*\*\*Bloqueios em aberto:\*\*\***

* O Query Analyzer ainda apresenta falhas na interpretação de algumas perguntas ambíguas.
* A extração incompleta de termos e a falta de padronização dos filtros podem comprometer os resultados das consultas híbridas.
* Embora os 794 chunks tenham sido persistidos, a indexação FAISS ainda precisa ser concluída e validada para assegurar a recuperação semântica.
* A integração entre Analyzer, Router, SQL Executor e RAG ainda requer testes de ponta a ponta.

**\*\*\*Próximo passo (início do Encontro 12):\*\*\***

* Ajustar a classificação de perguntas ambíguas e a extração de termos e filtros temporais.
* Continuar a integração do Query Analyzer, do Router e das ferramentas de consulta estruturada.
* Finalizar a indexação FAISS e validar a recuperação combinada com FTS5 e RRF.
* Executar as perguntas de referência da base normativa e documentar a qualidade das fontes recuperadas.
* Comparar os carregadores normativos e verificar a consistência dos metadados e a prevenção de duplicações.
* Ampliar os testes de regressão e documentar os problemas identificados durante as consultas.
* Manter a documentação técnica atualizada e alinhar as próximas etapas entre as frentes de desenvolvimento.

**\*\*\*Uso de assistentes de IA:\*\*\***

* Foram utilizados assistentes de IA para apoiar a análise da arquitetura, o desenvolvimento do Query Analyzer e do roteamento, a revisão dos filtros e a organização do fluxo de consultas.
* Na base normativa, os assistentes apoiaram a análise da persistência dos chunks, a identificação de inconsistências nos metadados e a revisão dos procedimentos de carregamento e recuperação.
* A equipe utilizou IA como apoio à revisão de código, à elaboração de testes e à organização da documentação e das próximas etapas.
* As sugestões foram analisadas pela equipe e confrontadas com o código, as consultas ao banco e os resultados dos testes, sem considerar concluídas as funcionalidades que ainda dependiam de validação.


# Resumo do dia — Encontro 12 — 2026-10-14

**## Resumo do time no dia**

**\*\*\*Entregamos hoje:\*\*\***

* Demos continuidade à integração e à validação das rotas de consulta, com ajustes no Query Analyzer, nos filtros e nos componentes responsáveis pela execução das perguntas.
* Foram investigados problemas de desempenho nas chamadas ao serviço de LLM. Em uma execução, a análise da pergunta levou aproximadamente 213 segundos e a geração final, 242 segundos, totalizando cerca de 456 segundos.
* Foram adicionados registros de observabilidade para acompanhar os tempos de execução do Query Analyzer, da recuperação híbrida, da geração de embeddings e da resposta final.
* Foi implementada uma primeira tentativa de fallback do ECOA para OpenAI no Query Analyzer. Entretanto, os resultados disponíveis ainda não comprovam que o fallback automático tenha sido acionado durante os testes.
* Foram realizados outros testes de consulta, incluindo execuções com duração aproximada de 61 e 80 segundos. Em uma delas, o Query Analyzer levou 15,63 segundos e a geração final, 63,39 segundos; como o ECOA concluiu a execução, não foi possível atribuir a melhoria ao fallback.
* Ana Karina e Ester compararam os carregadores da base normativa após a integração das alterações, identificando diferenças na identificação dos documentos, na preservação de títulos e URLs e nos critérios utilizados para evitar duplicações.
* A análise identificou que um carregador utiliza `source_file` como referência, enquanto o outro considera uma chave composta baseada em `base_id` e `source_file`, por meio de `_document_source_file`. Essas diferenças precisam ser conciliadas para evitar inconsistências e documentos órfãos.
* Também foi identificada uma diferença no tratamento dos metadados: um carregador preserva títulos existentes, enquanto o outro pode sobrescrever campos como `title` e `source_url`. Foi relatada uma correção anterior para evitar títulos nulos, mas a comparação completa entre os carregadores permaneceu pendente.
* A equipe investigou problemas de instalação das dependências para a indexação FAISS. O ambiente com Python 3.10.4 apresentou incompatibilidade com `networkx==3.7`, que exige uma versão mais recente do Python, além da indisponibilidade da versão especificada de `numpy` para aquele ambiente.
* Renan restaurou e versionou as migrações incrementais `001_raw_canonical_identity_index.sql` e `002_sync_window_checkpoint.sql`, além da documentação `PNCP_INCREMENTAL_ENDPOINTS.md`, que estavam ausentes da branch e comprometiam a reprodutibilidade do ambiente.
* Foram validadas as migrações da ingestão incremental, incluindo a preservação dos dados RAW e dos checkpoints, a criação do índice de identidade canônica e do checkpoint v2 e a execução idempotente.
* As verificações da base SQLite apresentaram integridade `ok`, sem violações de chaves estrangeiras. Na validação relatada por Renan, foram aprovados 117 testes, além das verificações de compilação e de diferenças do Git.
* Luiz Felipe avançou nos ajustes de `src/query/structured_tool.py`, nos schemas de consulta, na camada ORM e nos testes, buscando alinhar a consulta estruturada à arquitetura definida para o projeto.
* Luciano continuou os testes das rotas e dos filtros, realizou ajustes no fluxo de validação e relatou a coleta e ingestão de novos documentos na base.
* A equipe avançou na organização do backlog técnico, na identificação de problemas de reprodutibilidade e na documentação das condições necessárias para estabilizar as consultas e a ingestão de dados.

**\*\*\*Ficou pendente:\*\*\***

* Continuar a investigação da latência das chamadas ao ECOA e avaliar alternativas para reduzir o tempo de resposta.
* Validar o funcionamento real do fallback automático para OpenAI no Query Analyzer e, posteriormente, no fluxo completo de recuperação e geração.
* Registrar o provedor e o modelo utilizados em cada etapa para facilitar a análise de desempenho e de falhas.
* Definir um padrão único para os carregadores da base normativa, alinhando a identificação dos documentos, a preservação de metadados e o tratamento de registros existentes.
* Executar testes para identificar possíveis documentos órfãos, duplicações e inconsistências entre `source_file`, `base_id` e os demais metadados.
* Criar um ambiente compatível com as dependências de indexação FAISS e concluir os testes de instalação e execução.
* Concluir a indexação FAISS e validar a recuperação documental com as perguntas de referência.
* Continuar os testes das consultas estruturadas, dos schemas, da camada ORM e da integração com o fluxo principal.
* Prosseguir com a coleta e ingestão de documentos e com a validação dos filtros e das rotas de consulta.
* Continuar as correções da ingestão incremental do PNCP, incluindo atomicidade, controle de lease, avanço seguro de watermark e recuperação de paginação.
* Atualizar a documentação técnica das migrações, dos checkpoints e das condições de sincronização.

**\*\*\*Bloqueios em aberto:\*\*\***

* A latência das chamadas ao ECOA pode tornar as consultas excessivamente demoradas e dificultar a execução dos testes de integração.
* O fallback para OpenAI ainda não teve seu acionamento automático comprovado, embora a chamada direta à OpenAI tenha sido validada posteriormente.
* A existência de dois carregadores com critérios diferentes de identificação e atualização dos documentos impede a definição segura de um padrão de persistência sem testes adicionais.
* As incompatibilidades entre versões do Python e dependências impediram o avanço da configuração inicial do ambiente para indexação FAISS.
* A indexação FAISS e a validação da recuperação semântica permanecem pendentes.
* A estabilização da ingestão incremental depende da implementação e validação dos controles de concorrência, checkpoints e recuperação de falhas.

**\*\*\*Próximo passo (início do Encontro 13):\*\*\***

* Continuar a análise de latência e validar o fallback automático entre ECOA e OpenAI, incluindo o registro do provedor e do modelo utilizado.
* Criar e validar um ambiente com versão de Python compatível com as dependências do projeto.
* Comparar os carregadores normativos em ambiente de teste, definir o comportamento esperado dos metadados e verificar a existência de documentos órfãos ou duplicados.
* Finalizar a indexação FAISS e executar testes de recuperação documental e busca híbrida.
* Continuar a integração das consultas estruturadas com o Query Analyzer, o Router e o fluxo de geração.
* Prosseguir com os testes de filtros, schemas, camada ORM e execução segura das consultas.
* Validar as migrações incrementais e avançar nas correções de atomicidade, lease, watermark e recuperação de paginação.
* Atualizar a documentação técnica e registrar os resultados dos testes para orientar as próximas decisões do grupo.

**\*\*\*Uso de assistentes de IA:\*\*\***

* Foram utilizados assistentes de IA para apoiar a análise dos registros de desempenho, a investigação da latência das chamadas à LLM e a revisão da estratégia de fallback entre provedores.
* Os assistentes apoiaram a comparação dos carregadores normativos, a análise de metadados, a investigação de dependências e a preparação do ambiente de desenvolvimento.
* Na frente de ingestão incremental, a IA auxiliou na análise das migrações, dos checkpoints, dos riscos de concorrência e da documentação técnica.
* Também foi utilizada como apoio à revisão de código, à interpretação de resultados de testes e à organização das correções prioritárias.
* As sugestões foram verificadas pela equipe por meio de testes automatizados, análise dos logs e verificações de integridade, mantendo como pendentes os comportamentos que ainda não foram comprovados.


# Resumo do dia — Encontro 13 — 2026-10-16

**## Resumo do time no dia**

**\*\*\*Entregamos hoje:\*\*\***

* Avançamos na integração e validação do fluxo de consultas, incluindo o Query Analyzer, as estratégias de recuperação, a execução estruturada e a geração das respostas.
* A API foi executada por meio do Uvicorn e testada no endpoint `/query/ask`, com resposta HTTP 200.
* Os registros de execução confirmaram o uso do ECOA tanto na análise da pergunta quanto na geração final da resposta.
* A recuperação híbrida utilizou FTS5, FAISS e RRF e retornou cinco fontes documentais em um dos testes. A indexação da base normativa ainda não foi concluída, portanto esse resultado não representa a validação definitiva de toda a base.
* Uma chamada direta ao modelo `gpt-4.1-mini` por meio da OpenAI foi realizada com sucesso. Entretanto, o acionamento automático do fallback no fluxo RAG ainda não foi comprovado.
* Foi identificada a localização de `app/streamlit_console.py` e o comando necessário para executar o console, facilitando a preparação da integração com a interface.
* Alisson continuou a análise de desempenho e a validação dos componentes de consulta. Em uma execução relatada, o fluxo foi concluído em aproximadamente 38 segundos com uso do ECOA.
* Ana Karina e Ester prepararam um ambiente virtual com Python 3.12.10, instalaram as dependências e verificaram a versão do SQLAlchemy. Também ajustaram o `.gitignore` para excluir o diretório `.venv312/`.
* A preparação do ambiente representou um avanço para investigar a indexação FAISS, embora a execução da indexação ainda não tenha sido concluída.
* A comparação entre os carregadores normativos permaneceu em análise. Foram identificadas diferenças na identificação dos documentos e na atualização dos metadados, mas ainda não houve uma decisão final sobre qual implementação será adotada como padrão.
* Luiz Felipe integrou alterações relacionadas às consultas e à validação de segurança na branch `feat/luiz-desenvolvimento`, realizando o commit `598ae0c feat: integra melhorias de consulta e validacao de seguranca` e enviando as alterações ao repositório remoto.
* Após a integração, foram executados testes que resultaram em **382 testes aprovados e 76 subtestes aprovados**, sem falhas e com dois avisos de depreciação.
* Os ajustes de Luiz abrangeram `src/query/structured_tool.py`, `src/generate.py`, schemas, camada ORM, dependências e testes unitários e de integração.
* Renan continuou a validação da ingestão incremental do PNCP, verificando as migrações, os checkpoints e a integridade da base SQLite. Os resultados reportados incluíram integridade `ok`, ausência de violações de chaves estrangeiras e aprovação dos testes previstos para essa etapa.
* Foram mantidas as validações de reprodutibilidade e idempotência das migrações, com preservação dos dados RAW e dos checkpoints.
* A equipe identificou um alerta de versionamento relacionado ao arquivo `app.db`, que possui 81,24 MB e ultrapassa a recomendação de 50 MB do GitHub. Apesar do alerta, o envio das alterações de Luiz foi concluído.
* Foram organizadas as pendências de integração, indexação, desempenho, segurança e gerenciamento do banco de dados, orientando a continuidade do desenvolvimento.

**\*\*\*Ficou pendente:\*\*\***

* Concluir a indexação FAISS da base normativa e validar a recuperação com as perguntas de referência.
* Finalizar a comparação dos carregadores normativos e definir um padrão único, incluindo regras para identificação de documentos, preservação de títulos e URLs e prevenção de duplicações.
* Validar o fallback automático para OpenAI no fluxo de análise, recuperação e geração, registrando o provedor e o modelo usados em cada etapa.
* Continuar a avaliação da latência e da qualidade das respostas geradas pelo ECOA.
* Integrar e validar a interface Streamlit com a API e o fluxo principal de consultas.
* Ampliar os testes das rotas `structured`, `rag` e `hybrid`, verificando filtros, fontes recuperadas, execução segura e fundamentação das respostas.
* Corrigir eventuais inconsistências nos schemas, na camada ORM e nos componentes de consulta identificadas após a integração.
* Revisar o tratamento do arquivo `app.db` no repositório e definir uma estratégia adequada para o banco de dados, evitando problemas de versionamento e distribuição.
* Continuar as validações da ingestão incremental, incluindo atomicidade das gravações, controle de lease, avanço do watermark, recuperação de paginação e tratamento de registros do PCA.
* Consolidar a documentação das migrações, dos checkpoints e das limitações identificadas durante as validações.

**\*\*\*Bloqueios em aberto:\*\*\***

* A indexação FAISS da base normativa continua pendente, limitando a validação completa da recuperação semântica e híbrida.
* A decisão sobre o carregador normativo padrão ainda depende de comparação e testes adicionais.
* O fallback automático para OpenAI não foi comprovado no fluxo completo, embora a chamada direta ao modelo tenha funcionado.
* A instabilidade e a latência dos serviços de LLM podem interferir na execução dos testes e na experiência de consulta.
* A integração da interface Streamlit com a API e o fluxo principal ainda precisa ser validada.
* O tamanho do arquivo `app.db` ultrapassa a recomendação do GitHub, exigindo uma definição sobre como manter e distribuir o banco.
* A ingestão incremental ainda depende da conclusão das validações de consistência, concorrência e recuperação de falhas.

**\*\*\*Próximo passo (início do próximo encontro):\*\*\***

* Finalizar a indexação FAISS e executar testes de recuperação com FTS5, FAISS e RRF.
* Definir o carregador normativo padrão após comparar o comportamento das implementações e verificar os metadados e a integridade dos documentos.
* Validar o fallback automático entre ECOA e OpenAI no fluxo completo de consulta.
* Continuar a análise de latência e a avaliação da qualidade, da fundamentação e da rastreabilidade das respostas.
* Integrar a interface Streamlit à API e validar o percurso completo da pergunta até a resposta.
* Executar testes de regressão das rotas estruturadas, documentais e híbridas após as novas integrações.
* Revisar o tratamento do arquivo `app.db` e definir uma estratégia de versionamento e distribuição do banco.
* Prosseguir com a validação da ingestão incremental, priorizando integridade dos dados, checkpoints, controle de concorrência e recuperação de falhas.
* Consolidar os resultados dos testes e atualizar a documentação técnica com as entregas, as limitações e as pendências ainda abertas.

**\*\*\*Uso de assistentes de IA:\*\*\***

* Foram utilizados assistentes de IA para apoiar a revisão e a integração do código, a análise dos componentes de consulta, a validação dos schemas e da camada ORM e a interpretação dos resultados dos testes.
* Os assistentes apoiaram a investigação dos registros de execução, da latência das chamadas à LLM e da configuração dos provedores ECOA e OpenAI.
* Também foram utilizados para analisar a persistência dos documentos normativos, comparar os carregadores e investigar a preparação do ambiente para a indexação FAISS.
* Na frente de ingestão incremental, a IA apoiou a análise das migrações, dos checkpoints, da integridade da base e das correções necessárias para garantir a reprodutibilidade.
* As sugestões foram revisadas pela equipe e verificadas por meio de testes automatizados, chamadas à API, consultas ao banco e verificações de integridade. Os resultados foram registrados conforme as evidências disponíveis, mantendo como pendentes as funcionalidades que ainda não tiveram sua integração ou execução completa comprovada.

