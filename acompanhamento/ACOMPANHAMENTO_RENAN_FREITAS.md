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
teste
