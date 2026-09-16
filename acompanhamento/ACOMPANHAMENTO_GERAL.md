Resumo do dia - Encontro 1 - 2026-09-16 - (escrito em conjunto)

## Resumo do time no dia

**Entregamos hoje:**

* Criamos e configuramos o repositório da equipe, com os integrantes e o mentor.
* Estruturamos a arquitetura inicial do projeto e definimos a divisão de responsabilidades entre os integrantes.
* Criamos e revisamos os documentos iniciais de requisitos e Engenharia de Software.
* Configuramos a estrutura inicial do backend com FastAPI, SQLAlchemy, SQLite, Pydantic Settings e Uvicorn.
* Criamos o `README.md`, `AGENTS.md`, `.gitignore` e `requirements.txt`, deixando o ambiente inicial documentado e reproduzível.
* Criamos o `PERSONAS.md`, com três personas, nove perguntas de referência, rotas esperadas e tipos de consulta.
* Criamos a primeira versão do `corpus_manifest.yaml`, declarando as quatro bases: **normativa, estruturada, conversacional e agregada**, com suas fontes, formas de acesso e critérios iniciais de seleção.
* Iniciamos a definição e organização da **base normativa**, incluindo a seleção inicial das fontes e a estratégia de processamento dos documentos.
* Definimos a necessidade de coleta e processamento separado conforme a natureza de cada base.

**Ficou pendente:**

* Completar a seleção das fontes da base normativa, incluindo decretos estaduais e editais do RJ de 2025.
* Iniciar a coleta real dos documentos e dados das quatro bases.
* Criar o `CORPUS_INVENTORY.md` para registrar os documentos e dados efetivamente coletados.
* Implementar o `fetch_corpus.py` para automatizar a coleta, incluindo download, hash e registro de falhas.
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
* Completar a lista de fontes da base normativa e iniciar o `fetch_corpus.py`.
* Criar e manter o `CORPUS_INVENTORY.md` com os documentos coletados.
* Iniciar a extração, processamento e chunking dos documentos normativos.
* Implementar os primeiros Models e módulos do backend conforme a arquitetura definida.
* Iniciar a preparação da ingestão para as demais bases e estruturar a futura indexação e recuperação híbrida.

**Uso de assistentes de IA:**

* Utilizamos assistentes de IA como apoio na organização da documentação, estruturação do projeto, revisão da arquitetura, definição das personas e perguntas, organização do manifesto e esclarecimento de dúvidas técnicas.
* As sugestões foram revisadas e ajustadas pela equipe de acordo com o enunciado, as fontes do cenário e a arquitetura definida para o projeto.
