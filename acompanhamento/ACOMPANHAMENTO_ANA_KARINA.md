# Acompanhamento · Ana Karina

**Time:** 03 · Contratações Públicas do Estado do RJ
**Papel:** Base normativa (com a Ester) · minha frente: processamento dos documentos

---

## Encontro 1 · 16/09/2026

### O que eu fiz hoje

Fiquei com a base normativa junto com a Ester, que reúne a Lei 14.133/2021, os decretos estaduais e os editais das contratações do RJ.

Criei a branch `base-normativa` para a gente trabalhar separado da principal.

Combinamos que Ester e eu fariamos tudo juntas logo cuidamos da coleta e do processamento: extrair o texto dos PDFs, dividir por artigo ou cláusula e montar os metadados de cada trecho. Por isso, hoje fiquei com a seção 4.1 do ARQUITETURA.md. Completei a descrição da base com o identificador (`editais_normativo`), o formato, o uso esperado, a estratégia de chunking, os metadados e a questão da vigência.

Uma coisa que eu entendi melhor escrevendo essa parte é que a lei não pode ser cortada em pedaços de tamanho fixo: se um artigo for separado dos seus
parágrafos, a resposta pode sair incompleta ou errada. Por isso, a ideia é dividir respeitando a hierarquia (artigo, parágrafo, inciso) e guardar essa
referência no metadado, para a resposta citar exatamente o artigo.


### O que travou

- Juntar a minha alteração no ARQUITETURA.md com a versão que o Alisson subiu, sem dar conflito
- Erro "not a git repository" por estar com o terminal na pasta errada.


### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude
- **Para quê:** sugerir a estrutura da seção 4.1 e a lista de metadados, e
  entender o erro do Git.
- **O que eu conferi / mudei:** comparei os metadados com os obrigatórios do
  enunciado (`source_file`, `doc_type`, `chunk_id`, `sensitivity`, `base_id`) e
  escrevi a explicação da divisão por artigo com as minhas palavras.


### Próximo passo

- Pesquisar bibliotecas de extração de texto de PDF e testar com a Lei 14.133.
- Começar o chunking por artigo em `src/ingest.py`.
- Criar o teste que verifica se todo chunk tem os metadados obrigatórios
  (`source_file`, `doc_type`, `chunk_id`, `sensitivity`, `base_id`).

---

## Resumo do time no dia

- **Entregamos:** estrutura do repositório, ARQUITETURA.md com coordenador e
  responsáveis por base, [PERSONAS.md], manifesto com as bases declaradas,
  relatos individuais.
- **Travou:** instabilidade do PNCP.
- **Próximo passo:** coleta real do corpus e o CORPUS_INVENTORY.md.

## Encontro 2 · 18/09/2026

### O que eu fiz hoje

Hoje trabalhei junto com a Ester para fechar a lista de documentos da base normativa no manifesto.

Revisamos os editais e vimos que nem todos eram o que o comentário dizia, então corrigimos e ficamos só com editais de 2025. Também trocamos a Lei 14.133 do
Senado pela versão do Planalto, porque o site do Senado bloqueava o download automático e o Planalto traz o texto oficial e atualizado.

Depois buscamos os decretos estaduais do RJ que regulamentam a lei, na lista oficial da Redelog. Ficamos com 7 decretos, eu junto com a  Ester calculou o sha256 de cada um e registrou no manifesto; pesquisei os decretos , conferi os PDFs e revisei o manifesto

Como a minha parte é o processamento, olhei os documentos pensando em como vamos dividi-los em trechos. Percebi que a lei do Planalto vem em HTML e
precisa ser lida como `cp1252`, senão os acentos quebram, e que os decretos seguem a mesma estrutura de artigo, parágrafo e inciso da lei, o que ajuda no
chunking. Também vi que o decreto 49.129 altera o 48.760, então vamos precisar guardar essa relação no metadado para não responder com a regra antiga.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude 
- **Para quê:** entender por que alguns links não baixavam e o que é o sha256.
- **O que eu conferi / mudei: Abri os decretos para ver se estavam completos, conferi se os editais eram mesmo de 2025 e auxiliei a Ester em todo processo.

### O que travou

- Sites que bloqueiam download automático e instabilidade do PNCP.

### Próximo passo

- Começar a extração de texto (PDF e HTML) e o chunking por artigo no
  `src/ingest.py`.
- Criar o teste que verifica se todo chunk tem os metadados obrigatórios.

### Resumo do time no dia

- **Entregamos (base normativa):** manifesto com a Lei 14.133 do Planalto,
  5 editais de 2025 revisados e 7 decretos estaduais com sha256.
- **Travou:** bloqueio de download em sites públicos e instabilidade do PNCP.
- **Próximo passo:** coleta com o `fetch_corpus.py` e o CORPUS_INVENTORY.md.

## Encontro 3 · 21/09/2026

Seguimos a arquitetura do README do time: criamos a pasta
`app/modules/normative/` com `services.py` (a coleta), `model.py`,
`schemas.py` e `routes.py`. A coleta baixou a Lei 14.133 e os 5 editais,
copiou os 7 decretos e conferiu o hash de cada um. Terminou com 13 documentos
e nenhuma falha. Os registros ficaram em `data/inventory/`.

Na hora de rodar, passei por alguns erros e fui entendendo cada um. O primeiro
foi de sintaxe: uma linha só com `"""` tinha se perdido na colagem, e o Python
entendia o resto do arquivo como texto. Depois apareceu "No module named
'truststore'", porque a biblioteca não estava instalada no meu Python;
resolvi com `python -m pip install`, que instala no mesmo Python que roda o
projeto.

Criamos os testes da coleta. O arquivo ficou em `tests/integration/`, e por
isso o primeiro comando do pytest e o `git add` não acharam o arquivo; quando
usei o caminho certo, os 9 testes passaram. Fiz o commit e o push da branch
`base-normativa` e conferimos no GitHub que os 6 arquivos chegaram.

Olhando o que a coleta gerou pensando no processamento, vi que os documentos
chegam em dois formatos (a lei em HTML e o resto em PDF) e que os decretos
salvos pelo navegador têm cabeçalho e rodapé em cada página, que vou precisar
limpar antes de dividir por artigo. [ajustar com a sua visão]

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude (junto com a Ester).
- **Para quê:** entender os erros de sintaxe e de biblioteca, e saber em qual
  pasta colocar o código segundo a arquitetura.
- **O que eu conferi / mudei:** substituí o arquivo inteiro em vez de colar
  pedaços, instalei as bibliotecas no meu Python, corrigi o caminho do teste e
  conferi no GitHub se o push tinha chegado.

### O que travou

- Erro de sintaxe causado por uma linha perdida na colagem.
- Biblioteca `truststore` não instalada no meu Python.
- Caminho do teste diferente do comando (`tests/integration/`).

### Próximo passo

- Fazer o processamento da base normativa em `app/modules/ingest/services.py`:
  extrair o texto, dividir a lei e os decretos por artigo e os editais por
  cláusula, e gravar os trechos em `data/processed/`.
- Criar o teste que verifica se todo trecho tem os 5 metadados obrigatórios.

### Resumo do time no dia

- **Entregamos (base normativa):** coleta em `app/modules/normative/services.py`
  (13 documentos, 0 falhas), registros em `data/inventory/` e 9 testes
  passando.
- **Travou:** certificados dos sites do governo, erro de colagem e caminho do
  teste.
- **Próximo passo:** processamento da base normativa e CORPUS_INVENTORY.md.