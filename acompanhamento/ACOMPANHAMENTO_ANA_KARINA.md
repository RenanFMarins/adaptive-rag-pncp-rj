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

## Encontro 4 · 23/09/2026

### O que eu fiz hoje

Hoje fiz, com a Ester, o processamento da base normativa, que é a minha frente.
A coleta já estava pronta da aula passada, então os documentos estavam
disponíveis para serem tratados.

Criei o módulo `app/modules/ingest/`, com `services.py`, `schemas.py` e
`routes.py`, como manda a arquitetura do time. O processamento faz quatro
coisas: extrai o texto dos arquivos (PDF e HTML), limpa o que não é do
documento, corta em pedaços e coloca os metadados.

O que mais me chamou atenção foram os detalhes de cada formato. A Lei 14.133 vem
em HTML e precisa ser lida como cp1252, senão os acentos quebram. Além disso, o
Planalto mantém o texto revogado riscado na página: se ele entrasse, o sistema
responderia com regra que não vale mais. Nos decretos, o cabeçalho e o rodapé da
impressão apareciam no meio dos artigos, e os rótulos "Art. Xº" ficam numa
coluna à esquerda, o que exigiu ler o PDF respeitando a posição do texto na
página.

Na divisão por artigo, aprendi que não basta procurar "Art." no começo da linha:
citações como "Art. 2º desta Lei" apareciam no meio de um artigo e quebravam o
pedaço, e a Lei 14.133 ainda insere artigos no Código Penal, que fogem da
sequência. O resultado final foram 784 pedaços, com a lei completa em 194
artigos. [ajustar com a sua visão]

Depois criei os testes em `tests/test_ingest_normativa.py`, com uma lei de
exemplo bem pequena em `tests/fixtures/lei_trecho.html`, feita de propósito com
um artigo com parágrafos e incisos, uma citação e um trecho riscado. Os 9 testes
passaram.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** escrever o processamento e os testes e entender os problemas de
  formato dos documentos.
- **O que eu conferi / mudei:** rodei o processamento, conferi os pedaços
  gerados, ajustei o caminho de saída para `data/processed/` e corrigi o lugar
  dos arquivos de teste.

### O que travou

- Os arquivos de teste foram parar em `tests/integration/tests/fixtures/` por
  causa das "pastas compactas" do VS Code, e o pytest não encontrava.
- O arquivo de exemplo aparece com os acentos errados no editor, porque está em
  cp1252 de propósito, e não pode ser salvo pelo VS Code.

### Próximo passo

- Entregar o `data/processed/v1_editais_normativo.jsonl` para quem faz a
  indexação e a busca.
- Ajudar no CORPUS_INVENTORY.md e abrir o pull request para a main.

### Resumo do time no dia

- **Entregamos (base normativa):** processamento em
  `app/modules/ingest/services.py` (784 pedaços, Lei 14.133 com 194 artigos) e
  9 testes passando.
- **Travou:** caminho das pastas de teste e codificação do arquivo de exemplo.
- **Próximo passo:** CORPUS_INVENTORY.md e integração com a etapa de busca.

## Encontro 6 · 28/09/2026

### O que eu fiz hoje

Trabalhamos as duas na minha máquina, revisando o que ainda faltava na base
normativa em relação ao enunciado. Depois da lista pronta, pegamos as duas
pendências de maior peso.

A primeira foi a *data dos editais*. Eu tinha feito o processamento no
encontro anterior, e quando conferimos os metadados descobrimos que os 303
trechos de edital estavam sem data_publicacao a lei e os decretos têm a data
na linha de título, os editais não têm nada parecido. Tentamos extrair do texto
e o resultado foi ruim: o que vinha eram as datas das leis citadas dentro do
edital. Acabamos indo buscar na API do PNCP, que devolve a data oficial de
publicação de cada arquivo.

Alterei o metadados_do_documento para ler uma ficha gravada pela coleta, em
vez de consultar a rede na hora de processar. Isso importa para a parte que é
minha: os testes do processamento continuam rodando offline, sem depender de o
PNCP estar no ar.

Reprocessei os 13 documentos e confirmei os 784 trechos, agora todos com data.
Escrevi também o teste que garante que um edital *sem* ficha continua sendo
processado, em vez de quebrar a ingestão.

A segunda parte foi o inventário em JSON, que passou a ter o envelope exigido
pelo enunciado, com o manifest_hash amarrando o corpus ao manifesto.

Os testes foram de 27 para 31.

### Onde usei IA e o que mudei no resultado

- *Ferramenta:* Claude.
- *Para quê:* entender por que os editais estavam sem data de publicação,
  escrever a função que lê a ficha do PNCP na ingestão e os testes novos, e
  diagnosticar os erros de indentação e de importação que apareceram no
  caminho.
- *O que eu conferi / mudei:* conferi a resposta da API do PNCP antes de
  aceitar a solução, porque a primeira ideia (extrair a data do texto do PDF)
  tinha dado resultado errado e eu queria ver a fonte; reprocessei os 13
  documentos e conferi os metadados dos 784 trechos, em vez de confiar na
  contagem; e fiz questão de que a ingestão lesse um arquivo local em vez de
  chamar a rede, para os meus testes continuarem rodando offline.

### O que travou

- Meu ambiente virtual estava sem pypdf, truststore, requests, PyYAML e
  pytest, e foi preciso instalar um a um conforme os erros apareciam.
- O requirements.txt do repositório está salvo em UTF-16 e não instala com
  pip install -r. Qualquer pessoa que clonar vai bater nisso.
- Colamos os dois testes novos no arquivo errado e eles falharam com
  NameError, porque dependiam de um helper que estava no outro arquivo.
- Ao colar blocos de código no VS Code, a primeira linha perdia o recuo e virava
  IndentationError. Aconteceu três vezes até a gente pegar o jeito de
  conferir sempre a primeira linha depois de colar.

### Próximo passo

- Overlap entre as partes de um artigo longo, para o código cumprir o que o
  manifesto promete.
- Documentar o processamento no README.
- Entregar o data/processed/v1_editais_normativo.jsonl para a indexação.

### Resumo do time no dia

- *Entregamos (base normativa):* campo_vigencia preenchido nos 784 trechos,
  com a data vinda da API oficial do PNCP; inventário data/inventory/v1.json
  no formato do enunciado, com manifest_hash; 31 testes passando.
- *Travou:* dependências ausentes no ambiente e a codificação do
  requirements.txt.
- *Próximo passo:* overlap, README, logs e pull request para a main.


## Encontro 7 · 30/09/2026

### O que eu fiz hoje

Hoje mexemos no processamento, que é a parte que eu venho cuidando desde o
começo.

A primeira mudança foi o **overlap**. O manifesto prometia "split por
artigo/cláusula, com overlap" e o meu código não fazia isso — quando um artigo
passava de 4.000 caracteres, eu dividia em partes e a parte seguinte começava
seca, sem a frase que a introduzia. Agora cada parte repete os 200 caracteres
finais da anterior, cortados em palavra inteira para não começar no meio de uma
palavra.

O que eu não quis fazer foi overlap entre artigos diferentes. Para texto
normativo isso seria ruim: o artigo é uma unidade fechada, e colar o fim do Art.
74 no começo do Art. 75 faria a busca devolver o artigo errado com um pedaço do
certo. Deixei isso escrito no manifesto e no comentário do código, porque é o
tipo de decisão que alguém desfaz sem querer.

Acrescentei também os metadados `parte` e `tem_overlap` em cada trecho, para
quem for indexar saber quais repetem texto e não contar o mesmo conteúdo duas
vezes.

Depois veio o **lixo de impressão**. Olhando os trechos, vi que os editais do
SEI trazem a data da impressão e o link com o número da página no meio das
cláusulas — 125 linhas em 57 trechos. Eu já tinha um filtro para isso, feito
para os decretos, mas ele exigia ano de dois dígitos e os editais vêm com
quatro. A regra estava lá e não pegava.

Reprocessei os 13 documentos depois de cada mudança e conferi os números: o
corpus foi para 796 com o overlap e voltou para 794 com a limpeza, porque sem o
lixo alguns trechos deixam de estourar o limite. Conferi também que a Lei 14.133
continua completa e descobri que ela tem um artigo a mais do que eu contava, o
Art. 44-A, incluído por uma lei de 2025.

Escrevi quatro testes do overlap e dois do lixo de impressão. O total foi de 31
para 37.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** escrever a função do overlap, corrigir o filtro de lixo de
  impressão e escrever os testes.
- **O que eu conferi / mudei:** reprocessei os 13 documentos a cada alteração e
  comparei as contagens por arquivo, em vez de aceitar o total; conferi que a
  mudança do lixo só afetou o edital de 60 páginas, o que confirmou que o filtro
  não estava comendo texto bom; e conferi a contagem de artigos da lei antes de
  dar por encerrado.

### O que travou

- Um dos testes do overlap falhava porque o texto de exemplo não tinha quebras
  de linha, e a minha função divide por linha de propósito, para não cortar no
  meio de uma frase. Isso mostrou uma limitação real: um documento que viesse
  todo numa linha só geraria um chunk enorme.
- A primeira conferência do overlap parecia dizer que ele não estava
  funcionando, e o problema era o comando de verificação, não o código.

### Próximo passo

- Cobrir o caso do documento sem quebras de linha.
- Entregar o `data/processed/v1_editais_normativo.jsonl` para quem vai indexar.
- Logs estruturados, quando o time definir.

### Resumo do time no dia

- **Entregamos (base normativa):** overlap entre partes de artigo longo, com os
  metadados `parte` e `tem_overlap`; remoção do cabeçalho e rodapé de impressão
  dos editais; seção da base normativa no README; 37 testes passando. Corpus em
  794 trechos.
- **Travou:** os logs dependem de definição do time, ainda estamos decidindo 
- **Próximo passo:** logs, pull request e o arquivo de teste duplicado na branch
  principal.

  ## Encontro 8 · 02/10/2026

### O que eu fiz hoje

Hoje fechei o último item do enunciado que ainda faltava na nossa base
normativa: os logs estruturados, do item 2.4.

O `app/core/logging.py` estava no repositório com 0 bytes desde o começo do
projeto. Como ele é o lugar que o README aponta e a nossa coleta e ingestão já
estavam prontas para serem instrumentadas, escrevi. São cerca de 40 linhas: uma
função que grava o evento em `logs/pipeline-AAAA-MM-DD.jsonl` e um gerenciador
de contexto que mede a duração da etapa.

Instrumentei as duas pontas. Cada execução recebe um `run_id`, que é o que
amarra os eventos de uma mesma rodada — sem ele, como diz o enunciado, os logs
são ruído. A coleta emite um evento de resumo mais um por documento; a
ingestão, um por documento. Numa execução completa saem 27 eventos. Usei os
stages `coleta` e `ingestao`.

Duas decisões que tomei e que vale explicar: o campo `tokens` fica zerado
nessas duas etapas, porque nenhuma delas chama o LLM, mas existe para que toda
etapa tenha o mesmo formato; e o log não engole falha — uma URL morta vira um
evento com status `falhou` sem abortar a coleta, e uma exceção vira status
`erro` e continua subindo.

Depois disso encontrei um bug nosso, e esse foi o aprendizado do dia.

Eu tinha deixado anotada uma melhoria pequena: o `coletado_em` do inventário
carimbava a hora da execução, então toda recoleta dizia que os documentos
tinham sido coletados hoje, mesmo sem baixar nada. Fui corrigir isso, o que me
obrigou a rodar o `fetch` duas vezes seguidas — e aí apareceu.

Desde segunda-feira, quando a coleta passou a gravar uma ficha `.meta.json` ao
lado de cada edital para pegar a data de vigência, a função que garante a
idempotência procurava o documento com `glob(nome + ".*")` e pegava o primeiro
resultado. Na segunda execução, ela encontrava a ficha antes do PDF. O
inventário passava a registrar um arquivo de 223 bytes no lugar de um edital de
560 KB, com o tipo e o hash errados.

O que me marcou é que nada denunciava: o `volume_alvo` continuava batendo 13 e
as falhas continuavam zero. Só apareceria lá na frente, quando alguém tentasse
indexar e encontrasse um JSON minúsculo esperando um edital. E não foi
encontrado por acaso — apareceu porque fui mexer num detalhe que parecia menor.

Corrigi, travei com dois testes, e commitei separado da melhoria, para o bug
ficar visível no histórico com a explicação de como nasceu.

Ainda fiz a duração de cada download no log (o evento por documento saía sem
latência, e agora o 422 intermitente do PNCP vai aparecer como uma latência
alta em vez de sumir na média).

Os testes foram de 37 para 50.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** escrever o módulo de log, instrumentar a coleta e a ingestão,
  diagnosticar o bug da ficha e montar o roteiro de apresentação.
- **O que eu conferi / mudei:** não aceitei a primeira conferência do log, que
  mostrava os eventos com latência nula, e fui atrás de por quê — era porque
  nada tinha sido baixado; apaguei um edital de propósito para provar num
  download real, e o evento registrou 3.584 ms; decidi não inventar duração
  para documento que já estava no disco, porque estimar número num log é pior
  do que registrar que não se aplica.

### O que travou

- Descobri que o `data/processed/` que estava commitado tinha sido gerado numa
  máquina onde as fichas do PNCP ainda não existiam, então os 313 trechos de
  edital estavam sem data de vigência. A capacidade estava certa e testada; o
  arquivo é que estava velho. Reprocessei e voltou para 794 de 794.

### Próximo passo

- Continuar o trabalho em grupo.

### Resumo do time no dia

- **Entregamos (base normativa):** logs estruturados (item 2.4), correção do bug da ficha do PNCP e 50 testes passando. A base normativa cumpre todos os itens do enunciado.
- **Travou:** Descobri que o `data/processed/` que estava commitado tinha sido gerado numa
  máquina onde as fichas do PNCP ainda não existiam, então os 313 trechos de
  edital estavam sem data de vigência. A capacidade estava certa e testada; o
  arquivo é que estava velho. Reprocessei e voltou para 794 de 794.
- **Próximo passo:** Continuar o trabalho em grupo.

  ## Encontro 9 · 05/10/2026

### O que eu fiz hoje

Trabalhamos juntas o dia todo. Foi o dia em que o nosso pull request foi
aprovado e mesclado na branch principal, depois de uma semana aberto.

Para a minha parte isso significa que o processamento que venho cuidando desde o
começo saiu da nossa branch e entrou no projeto. São 794 trechos, cada um com o
documento de origem, o artigo ou a cláusula a que pertence, a data de vigência e
a marca de sensibilidade. Quem for construir a busca já tem acesso a eles.

Atualizei a minha cópia do projeto com o que entrou da principal: a camada
conversacional com os guardrails de escopo e a pipeline de documentos da base
estruturada. Rodei os 50 testes para confirmar que o processamento continua
passando com o código novo.

Fizemos uma auditoria nos 794 trechos, que foi o que mais me interessou, porque
mexe diretamente com a minha decisão de como dividir o texto. Procuramos textos
duplicados, trechos acima do limite de 4.000 caracteres e trechos curtos demais.
Não apareceu nenhum problema: zero duplicados, nenhum acima do limite, e a
mediana ficou em 1.744 caracteres.

Os seis trechos com menos de 100 caracteres me chamaram atenção no começo, mas
são legítimos: artigos vetados, como o "Art. 172. (VETADO)", e cláusulas de
edital que dizem literalmente "não se aplica". São trechos curtos porque o
documento é curto ali, não porque a divisão errou. [ajustar com a sua visão]

Também decidimos juntas o que ainda faria sentido mexer no processamento, e a
resposta foi quase nada. A limitação que eu tinha identificado na semana passada
um documento que venha com o texto todo numa linha só geraria um chunk acima
do limite não vai acontecer, porque o corpus está congelado desde o fim do
Sprint 1. Preferimos registrar a decisão de não corrigir a corrigir um problema
hipotético.

No fim do dia começamos a rascunhar as perguntas de referência da base normativa
para o benchmark, conferindo no corpus qual artigo responde cada uma.

### Onde usei IA e o que mudei no resultado

- *Ferramenta:* Claude.
- *Para quê:* conferir o estado do repositório depois dos merges, auditar o
  corpus, preparar o material de apresentação e localizar no corpus as respostas
  das perguntas de referência.
- *O que eu conferi / mudei:* questionei as três melhorias que me foram
  sugeridas para a base normativa e descartei duas, porque resolviam problemas
  que não vão acontecer — o corpus está congelado e ninguém está travado
  esperando documentação. Preferi registrar a decisão de não fazer.

### O que travou

- Nada travou no processamento hoje.
- O src/router.py está com 0 bytes e o eval/ está vazio. O roteador é o que
  decide em qual base buscar, e sem ele o sistema não faz o que o enunciado
  chama de Adaptive RAG.

### Próximo passo

- Terminar o rascunho das perguntas de referência da base normativa.
- Entender como o módulo de indexação vai consumir os nossos trechos,
  principalmente o metadado tem_overlap, que marca texto repetido entre partes
  de um mesmo artigo e não deve ser contado duas vezes.

### Resumo do time no dia

- *Entregamos (base normativa):* o PR foi mesclado e a base está integrada à
  branch principal, com todos os itens do enunciado cumpridos. Auditoria do
  corpus sem defeitos encontrados.
- *Travou:* o roteador e o benchmark continuam vazios.
- *Próximo passo:* perguntas de referência e alinhar quem assume o roteador.

## Encontro 10 · 07/10/2026

### O que eu fiz hoje

Hoje não foi dia de construir, foi dia de entender para onde o projeto vai.

Atualizamos a nossa branch com a principal e rodou os 50 testes da base
normativa depois do merge. Entraram nove commits com a busca híbrida do
time: FTS5 para busca por palavra-chave, FAISS para busca por significado, e
as duas combinadas por RRF. Nada da nossa parte quebrou.

Lemos juntas os dois documentos que o professor passou. O que entendi é que
o sistema hoje responde tudo do mesmo jeito: pega a pergunta, busca trechos
de texto parecidos e manda para a LLM escrever a resposta. Isso funciona bem
para uma pergunta sobre o que um decreto determina, mas erra feio numa
pergunta de número. Se alguém pergunta o valor total dos contratos de
dezembro, buscar cinco trechos de texto e somar o que aparece neles dá uma
resposta incompleta o certo é fazer uma soma no banco. Por isso entra uma
etapa nova antes da busca, que lê a pergunta e decide o caminho: banco de
dados, documentos, ou os dois.

Ficamos com a Etapa 7 — integrar os guardrails. O guardrail é a regra que
impede o sistema de responder o que ele não deve, como indicar qual empresa
contratar. Ele já está escrito e testado, mas descobrimos que ele não é
chamado em nenhum lugar: existe no código e não roda. A nossa parte é
colocá-lo como a primeira coisa a acontecer, antes de qualquer busca, para
que uma pergunta proibida não chegue nem ao banco nem aos documentos, e para
que a recusa fique registrada com o motivo.

Entendi também por que a tabela do professor diz que a base normativa está
"parcialmente pronta". A busca só encontra o que está numa tabela específica
do banco, e os nossos 794 trechos estão num arquivo que nunca foi carregado
nela. Então tudo o que a gente coletou e processou ainda não é encontrável
por quem faz uma pergunta. É pouco trabalho, mas é o que falta.

### Onde usei IA e o que mudei no resultado

- Ferramenta: Claude.
- Para quê: entender o que integrar guardrails exige, e descobrir o que ainda falta na base normativa.
- O que eu conferi / mudei: pedi para me explicarem com exemplo concreto

### O que travou

- Nada travou hoje.
- As Etapas 1 a 3 (Query Analyzer e Router) vêm antes da nossa e ainda não
  existem. O src/router.py continua com 0 bytes.

### Próximo passo

- Começar a Etapa 7 com a Ester: o guardrail rodando antes de tudo.
- Confirmar com o time quem carrega os nossos trechos na tabela que a busca
  indexa.

### Resumo do time no dia

- Entregamos (base normativa): branch sincronizada com a principal e 50
  testes passando com o código novo da busca híbrida. Assumimos a Etapa 7.
- Travou: o Query Analyzer e o Router, que precedem a nossa etapa, ainda
  não existem.
- Próximo passo: iniciar a Etapa 7 e confirmar quem indexa os trechos da
  base normativa.

    ## Encontro 11 · 09/10/2026

### O que eu fiz hoje

O dia em que a base normativa saiu do arquivo e entrou no sistema.

Trabalhamos juntas o dia todo. Começamos atrás de uma coisa que tinha
ficado da aula passada: por que a nossa base aparecia como "parcialmente
pronta" enquanto a estruturada aparecia como pronta. O motivo era concreto.
A busca do sistema só procura dentro de uma tabela do banco, a
document_chunks. Os nossos 794 trechos estavam apenas no arquivo JSONL e
nunca tinham sido gravados nessa tabela. Ou seja: tudo o que a gente
coletou e processou nas últimas semanas estava invisível para quem fizesse
uma pergunta. Isso me surpreendeu, porque a gente achava que entregar o
JSONL era o fim do nosso trabalho.

Antes de mexer, conferimos se dava para resolver sem atrapalhar ninguém.
Ninguém no projeto importa os nossos módulos, e as nossas rotas nem estão
ligadas na API. Então era trabalho nosso e só nosso.

Escrevemos o carregador, o app/modules/normative/persistencia.py, que lê o
nosso JSONL e grava os trechos no banco. Ele é seguro de rodar várias
vezes: na segunda passada ele vê que já está tudo lá e não duplica. Rodou e
gravou 794 trechos em 13 documentos, exatamente o volume_alvo do manifesto.

Aí veio a parte que valeu o dia. Perguntamos ao sistema "prazo de vigência
da ata de registro de preços" e ele trouxe o Art. 84 da Lei 14.133, que é a
resposta certa. Foi a primeira vez que vi o nosso corpus respondendo uma
pergunta de verdade. Depois de semanas coletando PDF e ajustando regra de
divisão de texto, ver isso funcionando foi diferente.

E não escrevemos uma linha de código de busca. Os trechos entraram na
tabela e passaram a circular pela mesma recuperação que o resto do sistema
usa — era isso que queria dizer com "reutilizar RAG".

Fizemos mais três coisas. O aviso de trechos sem data de vigência no fim do
processamento, que resolve o problema de quem roda a ingestão sem a coleta
antes e gera 313 trechos sem data sem perceber. O conserto do título de um
edital que ficava vazio: o número está no texto, mas o título é longo
demais e a nossa regra só aceitava 20 caracteres entre o tipo e o número —
ampliar o limite estragava outros dois editais, então criamos uma regra
reserva que só roda quando a principal falha. E o reprocessamento do
corpus, comparando antes e depois: 794 trechos, nenhum texto alterado,
nenhum chunk_id alterado, só os 27 daquele edital ganharam o número.

No fim do dia entrou o PR #42 do Luciano, com o planejador, o executor e a
rota híbrida. O Adaptive RAG do enunciado passou a existir de verdade hoje.

Os nossos testes foram de 50 para 81.

### Onde usei IA e o que mudei no resultado

- Ferramenta: Claude.
- Para quê: entender por que a nossa base estava invisível para a busca,
  escrever o carregador e os testes, e conferir o impacto das mudanças.
- O que eu conferi / mudei: fizemos questão de confirmar cada afirmação
  em vez de aceitar. Quando foi dito que o ingest/services.py poderia ser
  código do grupo, conferimos o histórico: os únicos nomes no arquivo são o
  meu e o da Ester, e a maior parte das linhas é minha. Quando foi dito que
  faltava um servidor Ollama, fomos olhar o código e já existe um servidor
  do ECOA configurado por padrão, que está no ar. Também decidimos não
  criar coluna nova no banco, porque isso mexeria em arquivo compartilhado
  com o time.

### O que travou

- Nada travou no nosso trabalho.
- Faltavam na máquina três pacotes que o projeto declara e o arquivo .env,
  que o projeto exige e não vem pronto no repositório.

### Próximo passo

- A indexação FAISS da base normativa, que é a busca por significado — a
  que encontra o artigo certo mesmo quando a pergunta não usa as mesmas
  palavras do texto.
- As nove perguntas de referência no eval/questions.json, que continua
  vazio.

### Resumo do time no dia

- Entregamos (base normativa): os 794 trechos carregados no banco e
  encontráveis pela busca, o aviso de trechos sem data, o conserto do
  número do edital e o preenchimento de título no recarregamento. Testes de
  50 para 81.
- Travou: nada na nossa parte. 
- Próximo passo: indexação FAISS e as perguntas de referência.

## Encontro 12 · 14/10/2026 — Relatório de Ana

### O que eu fiz hoje

Trabalhei junto com a Ester na comparação entre dois carregadores de dados do projeto: o meu `persistencia.py` (base normativa) e a função `persistir_chunks_jsonl_normativos` do Luciano (após o merge do PR #46 dele). Identificamos juntas dois pontos de conflito importantes entre as duas abordagens e, em seguida, enviei ao Luciano uma mensagem detalhando esses pontos para alinharmos qual carregador vai prevalecer. Também comecei a configurar o ambiente de desenvolvimento (venv) para rodar a indexação FAISS (`pipeline_indexacao_faiss`), mas travei em erros de dependência antes de conseguir executar essa etapa.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claudinha (assistente de IA para mentoria da residência)
- **Para quê:** Para me ajudar a comparar os dois carregadores de dados (lendo o código do meu `persistencia.py` e da função do Luciano) e identificar divergências de comportamento entre eles, além de me guiar na configuração do ambiente virtual Python e na investigação de erros de instalação de dependências.
- **O que eu conferi / mudei:** Conferimos, eu e a Ester, que a chave de identificação do documento é diferente entre os dois carregadores (`source_file` no meu vs. `base_id|source_file` no do Luciano, via `_document_source_file`), o que gera risco de duplicidade/documentos órfãos se os dois rodarem sobre os mesmos dados. Também identificamos que o carregador do Luciano sempre sobrescreve `title` e `source_url` em `_atualizar_origem_documento`, enquanto o meu preserva o `title` já preenchido (tenho até um teste, `test_titulo_ja_gravado_nao_e_sobrescrito`). Notamos ainda que o código do Luciano já evoluiu desde o relatório da Ester anterior, resolvendo o problema de `title` ficar `None`. Além disso, na configuração do ambiente, verifiquei na documentação oficial do PyPI que `networkx==3.7` exige Python 3.12+, incompatível com meu Python 3.10.4, e ajustei a versão para `networkx==3.4.2`.

### O que travou

- Conflito entre os dois carregadores de dados (base normativa vs. carregador do Luciano, PR #46): chave de identificação do documento diferente e comportamento diferente ao sobrescrever campos já preenchidos manualmente.
- Incompatibilidade de versões no `requirements.txt` do projeto (gerado aparentemente em Python 3.12+) com o Python 3.10.4 instalado na minha máquina, afetando `networkx` e, em seguida, `numpy==2.5.3` (sem distribuição compatível disponível para 3.10.4).

### Próximo passo

- Alinhar com o Luciano, via mensagem já enviada, qual padrão de chave de identificação e qual critério de sobrescrita de campos (`title`, `source_url`) o grupo vai adotar entre os dois carregadores.
- Resolver a incompatibilidade de ambiente instalando Python 3.12+ e recriando o `.venv` do zero, para então conseguir rodar a indexação FAISS (`pipeline_indexacao_faiss`).

### Resumo do time no dia

- **Entregamos (base normativa):** Diagnóstico comparativo entre os dois carregadores de dados (persistencia.py vs. carregador do Luciano) com os dois pontos de conflito identificados e comunicados ao responsável; diagnóstico da incompatibilidade de versão do Python no ambiente do projeto.
- **Travou:** Decisão final sobre qual carregador/padrão de chave usar (depende de alinhamento com o Luciano); configuração de ambiente (Python 3.10.4 incompatível com dependências do `requirements.txt`), impedindo a execução da indexação FAISS.
- **Próximo passo:** Fechar com o Luciano o padrão de chave e de sobrescrita de campos entre os carregadores; migrar o ambiente para Python 3.12+ e recriar o `.venv` para rodar a indexação FAISS.

## Encontro 13 · 16/10/2026

### O que eu fiz hoje

- Criei o ambiente virtual `.venv312` com Python 3.12.10.
- Instalei as dependências do `requirements.txt`.
- Verifiquei a versão do SQLAlchemy (2.1.1).
- Adicionei `.venv312/` ao `.gitignore`.
- Fiz o commit `1f82b7b` na branch `base-normativa` e enviei ao GitHub. Conferi o escopo com `git show --stat HEAD`, que mostrou apenas o `.gitignore` alterado.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude Haiku 5.5 (chat do MyHUB.IA).
- **Para quê:** orientação de comandos do PowerShell e do Git, organização do plano de trabalho e rascunho do relatório.
- **O que conferi / mudei:**
  - Corrigi o comando de busca, porque `Select-String` não aceita `-Recurse`. A recursão fica no `Get-ChildItem`.
  - Conferi o escopo do commit antes de considerá-lo concluído.
  - Retirei do rascunho afirmações não confirmadas, como o papel do ECOA e os motivos dos atrasos.

### O que travou

- A indexação ainda não foi iniciada.
- O comando para localizar a configuração do projeto ainda não foi executado com sucesso.
- Não está claro se o acesso ao servidor do ECOA está liberado. Na conversa, isso apareceu de duas formas diferentes, então vale confirmar antes de registrar.
- Falta confirmar o papel da Groq no projeto e se o `.venv312` vai virar padrão do grupo.
- Comparação dos carregadores de chunks (`persistencia.py` do grupo e `persistir_chunks_jsonl_normativos`, do Luciano, PR #46) ainda não executada. A decisão sobre qual fica depende de conversa com o Luciano.

### Próximo passo

- Rodar o comando corrigido de busca e confirmar a configuração do projeto, sem expor chaves.
- Comparar os dois carregadores em ambiente de teste, antes de rodar qualquer um na base principal.
- Executar a consulta de documentos órfãos após cada carga.;
- Confirmar o acesso ao servidor e, se estiver liberado, testar a conexão antes de indexar.

## Encontro 14 · 19/10/2026

### O que eu fiz hoje

Eu e Ester trabalhamos juntas para fechar o carregamento da base normativa e fazer a indexação vetorial.

O Luciano respondeu e escolheu a versão normativo-v1. Com isso passamos a ter um carregador só: o pipeline dele, que só ele chamava, agora usa o persistir() do nosso carregador, com os mesmos argumentos. A mudança principal é que o padrão deixou de ser "o corpus de id 1", porque esse número muda de banco para banco, e passou a ser a versão pelo nome. Rodamos os dois carregadores em bancos temporários para ter evidência: antes, um depois do outro davam 26 documentos, 13 sem nenhum trecho; depois do ajuste, 13 e nenhum órfão. O PR #53 foi mesclado.

Aprendi uma coisa sobre como o sistema guarda os documentos: o trecho tem um identificador único, então o segundo carregador pulava os trechos e só criava documentos vazios ao lado. Era um erro silencioso, que não dava mensagem nenhuma.

Depois indexamos a base normativa no FAISS. Pensamos que ia levar mais de dez minutos e levou cerca de quatro. A auditoria mostrou 794 vetores, cobertura de 100% e nenhuma inconsistência. Testamos a busca com perguntas escritas com palavras diferentes da lei, e a busca por significado achou artigos que a de palavra-chave não achou, como o Art. 84 sobre a vigência da ata. Mas nenhuma achou o Art. 4º da Lei 14.133, a resposta para "pequena empresa tem vantagem?", porque ele fala em "Lei Complementar 123".

Escrevemos também o eval/questions.json, que estava vazio, com as dez perguntas de referência, cada uma com a fonte conferida no banco, e medimos um baseline da recuperação.

### Onde usei IA e o que mudei no resultado

- Ferramenta: Claude.
- Para quê: comparar os carregadores, entender o que significava cada campo da indexação e ler o resultado da busca.
- O que eu conferi / mudei: pedi para explicar cada passo da indexação em vez de só rodar o comando. Conferimos o que era do grupo e o que era nosso antes de alterar o pipeline do Luciano. E a primeira busca de teste não provou nada, porque só havia 10 trechos indexados.

### O que travou

- Nada travou no nosso trabalho.
- O índice foi feito do zero, e a aplicação lê um v1 que pode ter os vetores do PNCP. Precisamos que o Luciano e o Alisson digam como promover sem substituir o v1.

### Próximo passo

- Rodar a migração do carregador no meu banco: python -m app.modules.normative.persistencia --versao v1.
- Alinhar a promoção do índice com o Luciano e o Alisson.

### Resumo do time no dia

- Entregamos (base normativa): carregador único na versão normativo-v1 (PR #53), 794 trechos indexados no FAISS com 100% de cobertura e as perguntas de referência no eval/questions.json.
- Travou: a promoção do índice depende do Luciano e do Alisson.
- Próximo passo: alinhar o índice e medir a recuperação com o benchmark.

## Encontro 15 · 21/10/2026

### O que eu fiz hoje

Trabalhamos juntas para fechar a base normativa e preparar a apresentação.

Atualizei a minha máquina com o que os colegas fizeram: guardei uma cópia do meu banco, soltei o app.db do Git, trouxe a principal com um merge e devolvi o banco. Entendi por que o banco atrapalha: o Luiz Felipe comitou uma versão dele, e a minha tinha alterações locais, então o Git se recusa a juntar. Depois tentei rodar a preparação do índice e deu erro de database_url, porque eu não tinha o arquivo .env, que cada pessoa cria e não vai para o Git. Aprendi que aqueles comandos eram para a máquina da Ester, que já tem tudo pronto, e que o meu Python 3.10 não serve para o numpy do projeto. Nada foi alterado por causa do erro.

Conferimos o PR #54, que eu tinha aberto. A Ester achou cinco inconsistências nos nossos arquivos e corrigiu: o hash do manifesto mudava conforme o fim de linha do Windows, o manifesto declarava um metadado que nenhum trecho tem, o inventário estava com hash velho, as datas do CORPUS_INVENTORY estavam erradas e o README não ensinava a rodar a base. O PR levou dez arquivos, sem banco, sem FAISS e sem BM25, e foi mesclado com os commits de cada uma separados.

O Alisson respondeu que o índice do grupo tem 65.362 vetores do PNCP e concordou com o plano de acrescentar os nossos 794 sem alterar o dele. Os testes do sistema mostraram que o analisador roteou errado quatro das nossas perguntas, e que a resposta da pergunta da data do edital veio errada mesmo com a data certa no metadado. A hipótese que tínhamos de qual pergunta ia errar não se confirmou.

### Onde usei IA e o que mudei no resultado

- Ferramenta: Claude.
- Para quê: entender os erros de Git e de ambiente, revisar a base normativa e testar o sistema.
- O que eu conferi / mudei: pedi para explicar por que o app.db bloqueia o merge e por que o comando falhou sem o .env, em vez de só repetir os passos. Conferimos o que o PR levava antes de mesclar, para o banco não ir junto.

### O que travou

- Nada travou no nosso trabalho.
- O meu ambiente tem Python 3.10 e não tem .env; para rodar o projeto preciso do .venv312.
- O índice consolidado depende de o Alisson confirmar a base mais atual.

### Próximo passo

- Criar o .env e usar o ambiente com Python 3.12.
- Ajudar a preparar os slides e o ensaio da demonstração de 22/10.

### Resumo do time no dia

- Entregamos (base normativa): cinco correções de consistência e quatro testes novos (PR #54 mesclado), e um kit com banco limpo e índice para o gerente.
- Travou: o índice consolidado depende do Alisson, e o limite de 30 s do ECOA ameaça a demonstração.
- Próximo passo: índice consolidado, slides e ensaio da demonstração.