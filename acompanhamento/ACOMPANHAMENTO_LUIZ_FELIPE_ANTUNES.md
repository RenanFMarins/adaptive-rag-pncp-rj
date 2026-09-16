# Acompanhamento — Grande Desafio IA Generativa e RAG

**Integrante:** Luiz Felipe Antunes
**Data:** 16/09/2026

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
