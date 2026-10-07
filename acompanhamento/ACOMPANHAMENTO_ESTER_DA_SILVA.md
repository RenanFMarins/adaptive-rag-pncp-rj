# Acompanhamento · Ester da Silva

**Time:** 03 · Contratações Públicas do Estado do RJ
**Papel:** Base normativa (com a Ana Karina) · minha frente: coleta dos documentos

---

## Encontro 1 · 16/09/2026

### O que eu fiz hoje

Comecei o dia entendendo o que o Grande Desafio pede. Li o enunciado no Notion
e percebi que ele é bem diferente do Mini Desafio: agora somos nós que coletamos
o corpus, são quatro bases e o sistema precisa decidir para onde ir antes de
buscar. A parte que mais me chamou atenção foi a explicação de que o roteador
não deve decidir pelo assunto, e sim pelo tipo de evidência que responde a
pergunta.

Clonei o repositório do time e, ao longo da tarde, fui atualizando meu local
conforme o Alisson subia a estrutura do projeto e o ARQUITETURA.md. 
Com a Ana, ficamos com a base normativa e combinamos a divisão: eu fico com a
coleta (lista de URLs, download e hash) e ela com o processamento (extração de
texto, chunking e metadados). Hoje eu fiquei responsável pelo bloco
`editais_normativo` no `corpus_manifest.yaml`: declarei a natureza, o tipo de
acesso (`http_pdf`), a Lei 14.133/2021 como primeira fonte, o campo de vigência,
a sensibilidade padrão e a sugestão de chunking por artigo/cláusula.

Para os editais, no portal de editais (pncp.gov.br/app/editais), com filtro de UF = RJ, e
que dá para escolher os editais por palavra-chave ligada às perguntas das
personas (merenda, material de escritório, notebook). 

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** sugerir o bloco normativo do manifesto.
- **O que eu conferi / mudei:** conferi no Notion se os campos do manifesto
  seguiam a estrutura obrigatória e escolhi os editais no portal. 

### O que travou

- Ainda não encontrei os decretos estaduais do RJ que regulamentam a Lei 14.133

### Próximo passo

- Completar a lista de URLs (decretos estaduais e editais do RJ de 2025).
- Começar o `src/fetch_corpus.py` para a base normativa: baixar os PDFs,
  calcular o hash e registrar falhas sem interromper a coleta.
- Alinhar com a Ana o formato dos arquivos baixados, para facilitar o chunking.

---

## Resumo do time no dia

- **Entregamos:** estrutura do repositório, ARQUITETURA.md com coordenador e
  responsáveis por base, [PERSONAS.md], manifesto com as bases declaradas,
  relatos individuais.
- **Travou:** instabilidade do PNCP.
- **Próximo passo:** coleta real do corpus e o CORPUS_INVENTORY.md.

---

## Encontro 2 · 18/09/2026

### O que eu fiz hoje

Hoje a Ana e eu trabalhamos juntas para deixar o bloco `editais_normativo` do
manifesto pronto para a coleta.

Começamos revisando os editais. Testando os links, depois fomos atrás da Lei 14.133. 
O PDF do Senado abria no navegador, mas, no teste de download automático, 
voltava uma página de "verificação de segurança" em vez do arquivo. 
Trocamos pelo texto do Planalto, que é a fonte oficial,
baixa direto e já está atualizado (inclui uma alteração de 2025 no art. 79).
Uma versão em PDF que encontramos era de abril de 2021 e não tinha essa
alteração, e isso me mostrou na prática o problema de vigência que o professor
comenta.

A parte mais trabalhosa foram os decretos estaduais. Encontramos a lista oficial
no site da Redelog, mas os links levam a um site que bloqueia download
automático. Baixei os 7 decretos pelo navegador (Ctrl+P > Salvar como PDF) e 
salvei em `data/manual/editais_normativo/`.
Escolhemos os que se ligam às perguntas das personas (PCA, pregão, fase
preparatória, fiscalização, contratação direta e registro de preços) e
incluímos o decreto 49.129, que altera o de PCA, para o sistema não responder
com a regra antiga. Conferi cada PDF para ver se o decreto estava completo, do
art. 1º até a assinatura.

Para garantir que o corpus seja sempre o mesmo, calculamos o sha256 de cada
decreto com o `Get-FileHash` do PowerShell e registramos no manifesto, junto com
o link de origem. Entendi que o hash funciona como uma impressão digital: se o
arquivo mudar, o código muda, e é isso que vai permitir comparar versões do
corpus. Também ajustamos o `volume_alvo` para 13 (1 lei + 5 editais + 7 decretos)
e deixamos comentado que a lei vem em HTML e os editais em PDF.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** entender o que é sha256 e sugerir o formato do trecho de decretos
  no manifesto.
- **O que eu conferi / mudei:** abrimos cada decreto para confirmar que estava
  completo, rodamos o `Get-FileHash` e comparamos com os códigos, escolhemos quais decretos entravam e mantivemos a estrutura de `acesso` que o time já usava.

### O que travou

- Sites bloqueando download automático (Senado e o site dos decretos).
- O PNCP às vezes responde erro 422 e, segundos depois, funciona. O
  `fetch_corpus.py` vai precisar tentar de novo antes de marcar como falha.

### Próximo passo

- Escrever a coleta da base normativa no `src/fetch_corpus.py`: baixar, conferir
  se veio PDF/HTML de verdade, tentar de novo em caso de erro, calcular o sha256
  e registrar falhas sem interromper a coleta.

### Resumo do time no dia

- **Entregamos (base normativa):** manifesto com a Lei 14.133 do Planalto,
  5 editais de 2025 revisados e 7 decretos estaduais com sha256.
- **Travou:** bloqueio de download em sites públicos e instabilidade do PNCP.
- **Próximo passo:** coleta com o `fetch_corpus.py` e o CORPUS_INVENTORY.md.

---

## Encontro 3 · 21/09/2026

### O que eu fiz hoje

Hoje a Ana e eu trabalhamos juntas na coleta da base normativa.
Começamos atualizando o repositório local com a main, que tinha
recebido várias mudanças do time (login, banco de dados e requirements).

Antes de escrever código, precisamos entender onde ele deveria ficar. 
Como o time definiu que devemos seguir a arquitetura
do README, a coleta ficou em `app/modules/normative/services.py`, junto com
`model.py`, `schemas.py` e `routes.py`, que por enquanto estão vazios.

A coleta lê o bloco `editais_normativo` do manifesto, baixa a Lei 14.133 e os
5 editais, copia os 7 decretos que baixamos à mão, confere o sha256 de cada
decreto e grava tudo em `data/raw/v1/`. Os registros de cada arquivo (tamanho,
hash, origem, status) ficam em `data/inventory/v1_editais_normativo.json`,
que é a base para o CORPUS_INVENTORY.md. O resultado foi 13 documentos
coletados, 0 falhas e divergência 0 em relação ao `volume_alvo`. Rodando uma
segunda vez, nada foi baixado de novo, que é a idempotência que o professor
pede.

Também criamos os testes da coleta, que rodam sem internet: reconhecer PDF e
HTML, não aceitar a mensagem de erro do PNCP como documento, gerar sempre o
mesmo nome para o mesmo link, não baixar de novo o que já existe e marcar como
falha um decreto com hash diferente do manifesto. Os 9 testes passaram.

O commit e o push foram feitos do computador da Ana, porque trabalhamos nele,
então o commit aparece no nome dela.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** escrever o rascunho da coleta e dos testes, comparar as duas
  estruturas de pastas e entender os erros que apareceram.
- **O que eu conferi / mudei:** mudamos o local do código para seguir a
  arquitetura do time, ajustamos o caminho dos registros para
  `data/inventory/`, rodamos a coleta e os testes e conferimos o resultado
  (13 documentos, 9 testes). Revisei no GitHub se os arquivos chegaram na
  branch `base-normativa`.

### O que travou

- Os sites do governo usam certificados da ICP-Brasil, que o Python não
  reconhece, e todos os downloads davam SSLError. Resolvemos com a biblioteca
  `truststore`, que usa os certificados do Windows. O Planalto também só
  respondeu quando o programa se identificou como navegador.
- Salvamos o teste em `tests/integration/` e o comando procurava em `tests/`,
  por isso deu "file not found".

### Próximo passo

- Incluir `truststore` e `pypdf` no `requirements.txt` (ainda não foi enviado).
- Combinar com o coordenador a montagem do CORPUS_INVENTORY.md com as 4 bases
  e onde ficam os decretos baixados à mão (`data/manual/` não está na
  arquitetura).
- Na próxima aula, apoiar a Ana no processamento da base normativa.

### Resumo do time no dia

- **Entregamos (base normativa):** coleta em `app/modules/normative/services.py`
  (13 documentos, 0 falhas), registros em `data/inventory/` e 9 testes
  passando.
- **Travou:** certificados dos sites do governo, erro de colagem e caminho do
  teste.
- **Próximo passo:** processamento da base normativa e CORPUS_INVENTORY.md.

---

## Encontro 4 · 23/09/2026

### O que eu fiz hoje

Hoje a Ana e eu trabalhamos juntas no processamento da base normativa, que é a
frente dela, depois de termos concluído a coleta na aula passada.

Comecei preparando o meu ambiente. Ao rodar a coleta na minha máquina, apareceu
"ModuleNotFoundError: No module named 'requests'", porque as bibliotecas tinham
sido instaladas só no computador da Ana. Instalei `requests`, `pyyaml`,
`truststore` e `pypdf` com `python -m pip install`, que garante a instalação no
mesmo Python que roda o projeto, e a coleta funcionou: 13 documentos, 0 falhas.

Criamos o módulo `app/modules/ingest/`, com `services.py`, `schemas.py` e
`routes.py`, seguindo a arquitetura do time. O processamento lê os documentos
que a coleta baixou, extrai o texto (PDF e HTML), limpa o cabeçalho e o rodapé
que o navegador colocou nos decretos e corta os documentos em pedaços: a lei e
os decretos por artigo, e os editais por cláusula. Cada pedaço leva junto os
metadados obrigatórios. O resultado foram 784 pedaços, gravados em
`data/processed/v1_editais_normativo.jsonl`.

Fiquei responsável por conferir o resultado. Abri o arquivo gerado e verifiquei
que a Lei 14.133 saiu com os 194 artigos, em ordem e sem faltar nenhum, que não
havia pedaço sem metadado obrigatório nem identificador repetido, e que os tipos
de documento estavam certos (7 decretos, 5 editais e 1 lei). Também li alguns
pedaços para ver se o artigo estava inteiro, com os parágrafos e incisos juntos.

Depois criamos os testes, em `tests/test_ingest_normativa.py`, com um documento
de exemplo em `tests/fixtures/`. Os 9 testes passaram.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** escrever o processamento e os testes, e entender os erros que
  apareceram no caminho.
- **O que eu conferi / mudei:** conferi eu mesma o arquivo gerado (os 194
  artigos, os metadados e os tipos de documento) e rodei os testes.

### O que travou

- As bibliotecas não estavam instaladas na minha máquina.
- O arquivo de exemplo está salvo em cp1252, de propósito, para imitar o site do
  Planalto, e o VS Code mostra os acentos errados. Aprendi que não posso salvá-lo
  pelo editor, senão os testes quebram.

### Próximo passo

- Montar, com o time, o CORPUS_INVENTORY.md, que é obrigatório na Etapa 1, a
  partir do `data/inventory/`.
- Abrir o pull request da `base-normativa` para a main.

### Resumo do time no dia

- **Entregamos (base normativa):** processamento em
  `app/modules/ingest/services.py` (784 pedaços, Lei 14.133 com 194 artigos) e
  9 testes passando.
- **Travou:** bibliotecas faltando e codificação do
  arquivo de exemplo.
- **Próximo passo:** CORPUS_INVENTORY.md e integração com a etapa de busca.

---

## Encontro 5 · 25/09/2026

### O que eu fiz hoje

Hoje a Ana não pôde comparecer, então comecei atualizando a nossa branch com a main, que tinha 15 commits novos do time, e rodei tudo de novo para conferir que o merge não quebrou nada: a coleta
(13 documentos, 0 falhas), o processamento (784 trechos) e os testes (18
passando). Precisei instalar o pytest na minha máquina.

Criei o `CORPUS_INVENTORY.md`, que estava vazio e é entregável obrigatório da
Etapa 1. Usei os dados reais da coleta: totais da versão, tabela por base,
detalhe dos 13 arquivos com tamanho e sha256, as falhas (nenhuma) e o
histórico de versões. As outras três bases ficaram com as linhas em branco,
para cada responsável preencher.

Depois implementei o que faltava da coleta em relação ao enunciado: os comandos
`update` e `inventory`. O `update` cria a versão seguinte sem sobrescrever a
anterior e gera o `DIFF_v1_v2.md`, dizendo o que entrou, saiu, mudou de
conteúdo e permaneceu idêntico. Isso é o que vai permitir o teste de regressão
nas próximas sprints. Testei criando a v2: a v1 continuou intacta.

Na primeira execução, o diff acusou que a Lei 14.133 tinha mudado. Comparei os
dois downloads e descobri que o texto é idêntico: o que muda é um script de
segurança do site do Planalto, com um código diferente a cada acesso. Se
ficasse assim, toda atualização daria alarme falso. Passei a calcular também um
`sha256_conteudo`, que ignora os scripts no caso de HTML, e o diff passou a
acusar corretamente 13 arquivos idênticos.

Conferi se o corpus responde às perguntas normativas do PERSONAS.md,
procurando os temas nos 784 trechos. Todas têm fonte: ME/EPP aparece na Lei
14.133 (arts. 4, 15, 60 e 81), adesão a ata no Decreto 48.843, prazo de
vigência nos Decretos 48.816 e 48.817, e dispensa por valor no art. 75 da lei.

Por último, fiz uma varredura de dados pessoais e encontrei, nos editais, 4
CPFs, 2 telefones e 31 e-mails, o que contraria a política de sensibilidade
que nós mesmas escrevemos. Implementei o mascaramento na ingestão: CPF e
telefone viram `[CPF MASCARADO]` e `[TELEFONE MASCARADO]`, enquanto CNPJ, nome
de empresa e valores continuam, porque são públicos por lei. Os e-mails
encontrados são de setores, e não de pessoas, então foram mantidos e
sinalizados no metadado `dados_pessoais`, para o time decidir depois.
Após reprocessar, não sobrou nenhum CPF nem telefone visível, e 19 trechos ficaram
marcados.

Escrevi testes para tudo o que fiz hoje: versão seguinte na sequência, hash que
ignora o script do site mas detecta mudança real de texto, classificação do
diff, inventário legível e o mascaramento. O total passou de 18 para 27 testes,
todos rodando sem internet.

Também corrigi o `requirements-dev.txt`, que estava com `trustsore` escrito
errado, o que fazia o `pip install -r requirements-dev.txt` falhar, e
acrescentei o `pytest`, que não estava listado.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** o mascaramento e os
  testes, e me ajudar a investigar por que o diff acusava mudança na lei.
- **O que eu conferi / mudei:** decidi manter a v2 como demonstração do
  versionamento em vez de apagá-la; decidi manter os e-mails de setor
  sinalizados em vez de mascarar tudo, porque a política fala em e-mail pessoal;
  conferi o resultado do mascaramento reprocessando os 784 trechos; e rodei
  todos os testes antes de dar por encerrado.

### O que travou

- Os logs estruturados (item 2.4 do enunciado) continuam pendentes, porque
  `app/core/logging.py` e `src/obs.py` estão vazios e é preciso combinar com o
  time quem escreve e quais são os nomes de `stage` da preparação do corpus.

### Próximo passo

- Definir com o time o módulo de logs e instrumentar a coleta e a ingestão.
- Documentar no README como rodar a coleta e o processamento.
- Abrir o pull request da `base-normativa` para a main.
- Perguntar ao time onde ficam os decretos baixados à mão (`data/manual/`, que
  não está na estrutura do README) e se o `data/processed/` vai para o Git.

### Resumo do time no dia

- **Entregamos (base normativa):** CORPUS_INVENTORY.md, comandos `update` e
  `inventory` com diff entre versões, mascaramento de dados pessoais na
  ingestão e 27 testes passando.
- **Travou:** logs estruturados dependem de decisão do time.
- **Próximo passo:** logs, README e pull request para a main.

---

## Encontro 6 · 28/09/2026

### O que eu fiz hoje

Comecei o dia comparando, item por item, o que já está no repositório com o que
o enunciado do professor exige da base normativa. Foi um exercício útil: a
coleta, o versionamento, o diff, o inventário legível, o processamento e a
política de sensibilidade já estavam prontos, mas apareceram quatro pendências
que eu não tinha enxergado antes. Organizei em ordem de peso e ataquei as duas
primeiras.

A primeira foi a **data de vigência dos editais**. O manifesto declara
`campo_vigencia: data_publicacao`, mas quando fui conferir, só 481 dos 784
trechos tinham esse campo — os 303 chunks de edital estavam todos sem data. A
lei e os decretos trazem a data na linha de título; os editais, não.

A primeira ideia foi extrair a data do texto do PDF, e ela se mostrou ruim
rápido: o que o regex trazia era "13 de dezembro de 2023" e coisas parecidas,
que são as datas de **outras normas citadas dentro do edital**. Um edital cita
dezenas delas. Foi aí que fui atrás da API do PNCP e descobri que, tirando o
número do arquivo do fim da URL, ela devolve a ficha da compra com o campo
`dataPublicacaoPncp` — a data oficial, sem adivinhação.

A solução ficou assim: a coleta passa a gravar um `<arquivo>.meta.json` ao lado
de cada edital baixado, e a ingestão lê esse arquivo. Isso mantém a rede só na
coleta, que é onde ela deve estar, e os testes do processamento continuam
rodando offline. Acrescentei também um metadado `fonte_data`, que registra de
onde veio a data — inclusive o valor `indisponivel`, para o caso de o PNCP não
responder. Achei importante deixar isso explícito em vez de fingir que toda data
tem a mesma confiabilidade. O resultado final foi 784 de 784 com data.

A segunda pendência foi o **formato do inventário em JSON**. O nosso
`v1_editais_normativo.json` era uma lista solta de arquivos, e o enunciado pede
um `v1.json` com envelope: `scenario_id`, `version`, `coletado_em`,
`manifest_hash`, `totais`, `por_base`, `arquivos` e `falhas`. Faltava tudo isso,
principalmente o `manifest_hash`, que é o sha256 do manifesto e é o que prova de
qual versão do manifesto aquele corpus veio.

Montei o comando de forma que ele **junta o que cada base já coletou** em vez de
exigir que as quatro estejam prontas. Hoje o `v1.json` sai só com a nossa base;
quando as outras rodarem, entram sozinhas. Assim ninguém fica bloqueado
esperando ninguém — o que, para um arquivo compartilhado pelo time inteiro, me
pareceu a decisão mais importante do dia.

Os testes foram de 27 para 31.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** investigar por que os editais estavam sem data, escrever as
  funções de consulta ao PNCP e do envelope do inventário, e os testes.
- **O que eu conferi / mudei:** conferi na mão a resposta da API do PNCP antes
  de escrever qualquer código; decidi gravar a ficha em arquivo separado em vez
  de consultar a rede na ingestão, para os testes continuarem offline; decidi
  que o inventário junta as bases disponíveis em vez de esperar as quatro; e
  decidi adiar o item do overlap, que era o menos valioso e obrigaria a
  reprocessar tudo em cima da hora.

### O que travou

- O ambiente virtual da máquina onde trabalhamos não tinha `pypdf`,
  `truststore`, `requests`, `PyYAML` nem `pytest`, e foi preciso instalar um a
  um conforme os erros apareciam.
- Descobrimos que o `requirements.txt` do repositório está salvo em **UTF-16**,
  o que faz o `pip install -r requirements.txt` falhar. Qualquer pessoa que
  clonar o repositório vai bater nisso.
- Perdemos bastante tempo com recuo de linha: ao colar blocos no VS Code, a
  primeira linha perdia os espaços e virava `IndentationError`. Aprendi a
  conferir sempre a primeira linha depois de colar.

### Próximo passo

- Igualar manifesto e código no chunking: o manifesto promete overlap e o código
  não faz.
- Escrever no README como rodar a coleta e o processamento, e registrar a
  política de sensibilidade.
- Logs estruturados: avisar no grupo que vou escrever o `app/core/logging.py`,
  que está vazio, e propor `coleta` e `ingestao` como nomes de `stage`, já que a
  lista canônica só cobre a fase de consulta.
- Abrir o pull request da `base-normativa` para a main.
- Corrigir a codificação do `requirements.txt`.

---

## Encontro 7 · 30/09/2026

### O que eu fiz hoje

Fechamos as duas pendências que faltavam na base normativa e achamos uma terceira
no caminho.

A primeira foi o **overlap**. O manifesto declarava "split por artigo/cláusula,
com overlap" e o código não fazia overlap nenhum — manifesto e implementação
diziam coisas diferentes, e isso é o tipo de incoerência que ninguém percebe até
alguém confiar no manifesto.

Implementamos do jeito que faz sentido para texto normativo: o overlap existe
**só entre as partes de um artigo que ficou grande demais** e precisou ser
dividido. Cada parte passa a repetir os 200 caracteres finais da anterior,
cortados em palavra inteira. Entre artigos diferentes não há overlap nenhum, e
isso é deliberado: artigo é unidade fechada, e misturar dois faria a busca
devolver um artigo com o texto do outro. Reescrevemos o `chunking_sugerido` do
manifesto para descrever exatamente isso, inclusive o que o código **não** faz e
por quê.

Uma consequência que nós não tínhamos previsto: o total subiu de 784 para 796
trechos. A causa é mecânica — a cauda ocupa parte do limite de 4.000 caracteres,
então os trechos longos passam a ser cortados um pouco mais cedo. Registramos a
explicação no inventário, porque daqui a duas semanas alguém veria o número
mudar sem entender.

Chegamos a achar que o overlap não estava funcionando, porque o comando que nós
usamos mostrava só o começo da parte 2 — e dali é impossível distinguir repetição
de continuação natural. Só comparando o fim da parte 1 com o começo da parte 2
ficou claro. Escrevemos uma conferência que faz essa comparação para todos os
trechos: 281 partes de continuação, todas repetindo de fato o final da anterior.

A segunda foi o **README**. Ele não explicava em lugar nenhum como rodar a base
normativa — conferimos e não havia uma única menção aos comandos. Escrevemos a seção
dentro de "Bases do projeto", que é a parte que é nossa, com o que está no
corpus, as dependências, os quatro comandos e o que cada um produz, o critério
de divisão do texto, a lista de metadados e a política de sensibilidade. Escolhemos
esse lugar de propósito: é a única parte do README que ninguém mais edita, então
o risco de conflito é quase zero.

A terceira foi olhando os trechos do overlap, vimos que os editais
do SEI trazem, a cada troca de página, a data e hora da impressão e o link com o
número da página **dentro do texto das cláusulas**. Eram 125 linhas em 57
trechos, indo para o índice como se fossem conteúdo do edital.

O mais interessante é por que isso passou: o filtro já tinha uma regra para
data e hora, mas ela exigia ano de dois dígitos (`13/09/24`, formato dos
decretos), e os editais vêm com quatro (`21/02/2025`). A regra existia e não
pegava. Aceitar 2 ou 4 dígitos resolveu.

Tomamos um cuidado aqui: sobraram quatro ocorrências do domínio do SEI que nós
decidimos **não** remover. São o aviso de verificação da assinatura digital, que é
conteúdo do documento e aparece no meio da linha. O filtro só corta linha que
começa com o padrão, então ele preserva isso naturalmente — mas conferimos cada
uma antes de dar por encerrado.

Conferindo que nada de conteúdo tinha sido levado junto, descobrimos uma coisa boa:
a Lei 14.133 no nosso corpus tem os artigos 1 a 194 em ordem **mais o Art.
44-A**, incluído pela Lei 15.210/2025. Ou seja, o corpus capturou uma alteração
deste ano — justamente porque escolhemos o texto compilado do Planalto em vez do
PDF estático que estava circulando.

Os testes foram de 31 para 37.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** implementar o overlap, escrever a seção do README, investigar o
  lixo de impressão e escrever os testes.
- **O que eu conferi / mudei:** decidimos que não haveria overlap entre artigos
  diferentes, contra a leitura literal do manifesto, porque artigo é unidade
  fechada; conferimos o overlap comparando as duas partes em vez de aceitar o
  resultado do comando de verificação, que estava errado; decidimos preservar as
  quatro ocorrências do domínio do SEI depois de ler cada uma, em vez de apagar
  tudo que casava com o domínio; e conferimos a contagem de artigos da lei antes de
  commitar, o que revelou o Art. 44-A.

### O que travou

- O primeiro teste do overlap falhava, e o erro era nosso: o texto de exemplo não
  tinha quebras de linha, e o `_partir_se_longo` divide por linha justamente
  para não cortar no meio de uma frase. Isso nos mostrou uma limitação real do
  código — um documento que viesse com o texto todo numa linha só geraria um
  chunk gigante. Não acontece com os nossos 13, mas é um caso a cobrir depois.
- A conferência do overlap deu 4 falsos negativos por causa do nosso próprio
  comando, que fatiava 150 caracteres e ultrapassava a região repetida.

### Próximo passo

- Logs estruturados (item 2.4): é a última exigência do enunciado em aberto na
  nossa parte. O `app/core/logging.py` continua com 0 bytes.
- Abrir o pull request, depois de combinar o que fazer com o
  `tests/integration/test_normative_coleta.py` que está na branch principal — é
  uma cópia antiga do nosso arquivo, com 9 testes contra os 17 atuais.
- Cobrir o caso do documento sem quebras de linha.
- O `requirements.txt` em UTF-16 continua quebrado na branch principal.

### Resumo do time no dia

- **Entregamos (base normativa):** overlap coerente com o manifesto, seção da
  base normativa no README, remoção do lixo de impressão dos editais do SEI e
  37 testes passando. Corpus em 794 trechos.
- **Travou:** os logs continuam dependendo de uma definição do time.
- **Próximo passo:** logs, pull request e resolver o arquivo de teste duplicado.

---

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

- **Entregamos (base normativa):** logs estruturados (item 2.4), correção do bug da ficha 
do PNCP e 50 testes passando. A base normativa cumpre todos os itens do enunciado.
- **Travou:** Descobri que o `data/processed/` que estava commitado tinha sido gerado numa
  máquina onde as fichas do PNCP ainda não existiam, então os 313 trechos de
  edital estavam sem data de vigência. A capacidade estava certa e testada; o
  arquivo é que estava velho. Reprocessei e voltou para 794 de 794.
- **Próximo passo:** Continuar o trabalho em grupo.

---

## Encontro 9 · 05/10/2026

### O que eu fiz hoje

Trabalhei com a Ana o dia todo, e foi um dia diferente dos anteriores: em vez de
construir, foi de integrar e revisar.

O pull request #20 foi aprovado e mesclado hoje. Com isso, tudo o que a
gente construiu saiu da nossa branch e entrou na branch principal: o módulo de
log, que estava com 0 bytes no repositório desde o começo do projeto, e os 794
trechos processados, que agora estão disponíveis para quem for construir a
busca. 

Depois disso cuidei da parte de integração. Entraram outros dois pull requests
ao longo do dia — a camada conversacional com os guardrails de escopo, e a
pipeline de documentos da base estruturada —, então trouxe a principal de volta
para a nossa branch duas vezes. Rodei os 50 testes depois de cada merge, para
confirmar que nada da base normativa tinha quebrado com o código novo do time.
Também conferi que o bloco normativo do manifesto continuava intacto, porque
numa das vezes anteriores ele tinha vindo com os acentos corrompidos.

Fizemos juntas uma auditoria no corpus, procurando defeito nos 794 trechos:
textos duplicados, trechos acima do limite de tamanho, trechos curtos demais.
Não encontramos nenhum problema. Os seis trechos abaixo de 100 caracteres são
legítimos — artigos vetados, como o "Art. 172. (VETADO)", e cláusulas de edital
que dizem "não se aplica". Foi bom ter conferido: até então a gente afirmava que
o corpus estava bom sem nunca ter olhado para ele desse ângulo.

Preparei o material da apresentação: um roteiro com os comandos, a saída
esperada e o que falar em cada momento, dividido entre eu e a Ana.

Sobrou um ponto real: a pasta data/raw/ é ignorada pelo Git, então as fichas com
as datas do PNCP não vão para o repositório. Quem clonar o projeto e rodar a
ingestão sem rodar a coleta antes vai gerar os 313 trechos de edital sem data de
vigência, e em silêncio. Foi exatamente o que aconteceu comigo na sexta. A
correção é um aviso no fim do processamento, dizendo quantos trechos ficaram sem
data.

No fim do dia começamos a rascunhar as perguntas de referência da base normativa
para o benchmark, conferindo cada uma no corpus para saber qual artigo responde.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** conferir o estado do repositório depois dos merges, auditar o
  corpus, preparar o material de apresentação e localizar no corpus as respostas
  das perguntas de referência.
- **O que eu conferi / mudei:** questionei as três melhorias que me foram
  sugeridas para a base normativa e descartei duas, porque resolviam problemas
  que não vão acontecer — o corpus está congelado e ninguém está travado
  esperando documentação. Preferi registrar a decisão de não fazer.

### O que travou

- Nada travou hoje. Os dois merges passaram sem conflito e os testes continuaram
  passando depois de cada um.
- Olhando o projeto, notamos que o src/router.py está com 0 bytes e o eval/ está
  vazio, a 18 dias do Demo Day. O roteador é o que o enunciado chama de coração
  do Adaptive RAG. 

### Próximo passo

- Terminar o rascunho das perguntas de referência da base normativa.
- Acrescentar o aviso de trechos sem data de vigência no fim do processamento.

### Resumo do time no dia

- **Entregamos (base normativa):** o PR #20 foi mesclado e a base normativa está
  integrada à branch principal, com todos os itens do enunciado cumpridos.
  Auditoria do corpus sem defeitos encontrados.
- **Travou:** o roteador (src/router.py) e o benchmark (eval/) continuam vazios.
- **Próximo passo:** perguntas de referência da base normativa e alinhar com o
  time quem assume o roteador.

---

## Encontro 10 · DD/MM/AAAA

### O que eu fiz hoje



### Onde usei IA e o que mudei no resultado

- **Ferramenta:** 
- **Para quê:** 
- **O que eu conferi / mudei:** 

### O que travou

- 

### Próximo passo

- 

### Resumo do time no dia

- **Entregamos (base normativa):**
- **Travou:**
- **Próximo passo:** 

---