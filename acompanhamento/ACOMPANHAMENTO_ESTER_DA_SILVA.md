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

## Encontro 10 · 07/10/2026

### O que eu fiz hoje

Dia de alinhamento e planejamento, depois da base normativa ter sido mesclada.

Começamos atualizando a nossa branch com a principal. Entraram nove commits —
os pull requests #29 a #33 —, trazendo a busca híbrida: FTS5 para busca por
palavra-chave no SQLite, indexação FAISS incremental, e o retrieve.py e o
index.py reescritos para combinar as duas com RRF. A pasta docs/ também foi
renomeada para notas/. Não houve conflito, porque a nossa branch não tinha
nada a mais que a principal. Rodei os 50 testes da base normativa depois do
merge, para confirmar que nada quebrou com o código novo, e subi.

Depois nós duas lemos as observações que o professor passou na última
aula. Primeiro descreve a evolução da arquitetura em dez etapas: a ideia é
que o sistema pare de tratar toda pergunta como consulta vetorial. Uma
pergunta como "qual foi o valor total dos contratos em dezembro de 2025?"
não deve ser respondida recuperando cinco trechos de texto — ela precisa
virar uma soma na base estruturada. Para isso entra uma camada nova antes da
recuperação: um Query Analyzer, que transforma a pergunta num JSON com
intenção, rota e filtros, e um Router, que decide entre três rotas —
estruturada (SQL), RAG (documentos) ou híbrida (as duas).

Ficamos com a Etapa 7 — Integrar Guardrails. Fui ver o que já existe: o
src/guardrails.py tem a função de verificação e sete termos de recusa
comercial, e há dois testes em tests/unit/test_guardrails.py. Mas procurei
por "guardrail" em src/ e app/ e a função não é chamada em lugar nenhum. Ou
seja, o guardrail existe e está testado, mas não está no caminho de nenhuma
pergunta. O que a etapa pede é que ele passe a ser a primeira coisa a rodar,
antes do Analyzer, e que uma pergunta bloqueada não chegue nem à ferramenta
de SQL nem ao RAG — além de ficar registrada no trace com a rota marcada
como bloqueada e o motivo da recusa.

A base normativa como "parcialmente pronta", fui procurar o motivo: o FTS5 e o 
FAISS indexam a tabela document_chunks do banco, e os nossos 794 
trechos estão num arquivo JSONL que nunca foi carregado nessa tabela. 
No meu banco local só existem registros da base estruturada. 
Então a busca híbrida ainda não alcança as leis e os decretos. 
Preciso confirmar com quem cuida da indexação de quem é
esse carregamento.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** mapear o que já existe de guardrails no código.
- **O que eu conferi / mudei:** Fui atrás do motivo da base normativa está
  "parcialmente pronta" e descobri que os nossos trechos não estão na tabela
  que a busca indexa — era uma informação que ninguém tinha levantado.

### O que travou

- Nada travou. O merge foi avanço direto e os 50 testes passaram.
- Fica pendente de confirmar com o time quem carrega os 794 trechos da base
  normativa na tabela que o FTS5 e o FAISS indexam.

### Próximo passo

- Começar a Etapa 7: colocar o guardrail no início do fluxo, antes do
  Analyzer, e registrar o bloqueio no trace.
- Escrever testes garantindo que uma pergunta bloqueada não aciona nenhuma
  ferramenta.

### Resumo do time no dia

- **Entregamos (base normativa):** branch sincronizada com a principal nas
  duas direções, 50 testes passando com o código novo da busca híbrida.
  Definimos que assumimos a Etapa 7 (integrar guardrails).
- **Travou:** o Query Analyzer e o Router, que são as Etapas 1 a 3 e
  precedem a nossa, ainda não existem — o src/router.py continua com 0 bytes.
- **Próximo passo:** iniciar a Etapa 7 e confirmar quem indexa os trechos da
  base normativa.

---

## Encontro 11 · 09/10/2026

### O que eu fiz hoje

O dia em que a base normativa saiu do arquivo e entrou no sistema.

Comecei atualizando a branch com a principal e fui atrás de uma coisa que
tinha ficado da aula passada: por que a nossa base aparecia como
"parcialmente pronta" enquanto a estruturada aparecia como pronta. Descobri
o motivo e ele era concreto. A busca do sistema — o FTS5 e o FAISS — só
procura dentro da tabela document_chunks do banco. Os nossos 794 trechos
estavam apenas no arquivo JSONL e nunca tinham sido gravados nessa tabela.
Conferi no banco: só havia registros da base estruturada. Ou seja, tudo o
que a gente coletou e processou nas últimas semanas estava invisível para
quem fizesse uma pergunta.

Antes de mexer, conferi se dava para resolver sem atrapalhar ninguém.
Procurei quem importa os nossos módulos em todo o projeto e não há ninguém;
as nossas rotas nem estão ligadas na API. Então o trabalho era nosso e só
nosso.

Escrevi o carregador, o app/modules/normative/persistencia.py. Ele lê o
nosso JSONL e grava os trechos no banco, e é idempotente pelo chunk_id:
rodar de novo não duplica nada. Rodou e gravou 794 trechos em 13
documentos, que é exatamente o volume_alvo do manifesto. Rodei uma segunda
vez para conferir: zero gravados, 794 já existentes.

Aí veio a parte que valeu o dia. O FTS5 indexou os trechos sozinho, por um
gatilho que já existia, e fui testar uma busca de verdade. Perguntei "prazo
de vigência da ata de registro de preços" e o sistema trouxe o Art. 84 da
Lei 14.133, que é a resposta certa. Testei mais duas perguntas e vieram os
artigos corretos. Foi a primeira vez que vi o nosso corpus respondendo.

Uma coisa que me deixou satisfeita: não escrevemos uma linha de código de
busca. Os trechos entraram na tabela e passaram a circular pela mesma
recuperação que o resto do sistema usa. Era exatamente isso que queria dizer 
com "reutilizar RAG".

Depois fizemos mais três coisas. Primeiro, o aviso de trechos sem data de
vigência no fim do processamento — o problema que eu vivi na sexta, de
rodar a ingestão sem a coleta e gerar 313 trechos sem data em silêncio.
Agora o programa avisa quantos ficaram sem data e qual comando rodar.

Segundo, consertamos o título de um edital que ficava vazio. O número dele
está no texto, mas o título é longo — "PREGÃO ELETRÔNICO PARA REGISTRO DE
PREÇOS N° 019/2025" — e a nossa regra só aceitava 20 caracteres entre o
tipo e o número. A primeira ideia foi ampliar o limite, mas testei nos
cinco editais e isso estragava outros dois. Criamos então uma regra reserva
que só roda quando a principal não acha nada. Os cinco saem certos agora.

Terceiro, reprocessamos o corpus e eu comparei o antes e o depois trecho a
trecho: 794 trechos, nenhum texto alterado, nenhum chunk_id alterado — só
os 27 daquele edital ganharam o número. Isso importa porque significa que
nada do que alguém já tivesse indexado ficou velho.

No fim do dia atualizei a branch de novo e entrou o PR #42 do Luciano, com
o planejador, o executor e a rota híbrida. O Adaptive RAG do enunciado
passou a existir de verdade hoje.

Os nossos testes foram de 50 para 81.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** investigar por que a base estava "parcialmente pronta",
  escrever o carregador e os testes, e conferir o impacto das mudanças.
- **O que eu conferi / mudei:** três vezes não aceitei o que me foi dito.
  Perguntei se o ingest/services.py era código do grupo e a resposta inicial
  estava errada — conferi o histórico e os únicos nomes no arquivo são o meu
  e o da Ana. Perguntei se as nossas mudanças afetariam os outros e exigi a
  verificação em vez da suposição. E quando me disseram que faltava um
  servidor Ollama, pedi para olhar o código: já existe um servidor do ECOA
  configurado por padrão e ele está no ar. Também escolhi não criar coluna
  nova no banco, porque isso mexeria em arquivo compartilhado.

### O que travou

- Nada travou. Os dois merges passaram sem conflito.
- Para rodar os testes do carregador faltavam três pacotes na minha máquina
  que o projeto declara mas nunca tinham sido instalados, e faltava o .env,
  que o projeto exige e não vem pronto.

### Próximo passo

- A indexação FAISS da base normativa, que é a busca por significado. É o
  último item e é mais simples do que parecia: o servidor do ECOA já está
  configurado no código.
- Escrever as nove perguntas de referência no eval/questions.json, que
  continua com 0 bytes.

### Resumo do time no dia

- **Entregamos (base normativa):** os 794 trechos carregados no banco e
  encontráveis pela busca, o aviso de trechos sem data, o conserto do
  número do edital e o preenchimento de título no recarregamento. Testes de
  50 para 81.
- **Travou:** nada na nossa parte. 
- **Próximo passo:** indexação FAISS e as perguntas de referência.

---
## Encontro 12 · 14/10/2026

### O que eu fiz hoje

Trabalhei junto com a Ana na comparação entre dois carregadores de dados do projeto: o persistencia.py da base normativa e a função persistir_chunks_jsonl_normativos do Luciano (após o merge do PR #46 dele). Identificamos juntas dois pontos de conflito importantes entre as duas abordagens, que a Ana depois comunicou ao Luciano. Também acompanhei a tentativa de configuração do ambiente de desenvolvimento (venv) para rodar a indexação FAISS, ajudando a interpretar os erros de dependência que apareceram.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claudinha (assistente de IA para mentoria da residência), usada em conjunto com a Ana
- **Para quê:** Para comparar o código dos dois carregadores e entender as divergências de comportamento entre eles, além de interpretar as mensagens de erro de instalação de dependências do ambiente virtual.
- **O que eu conferi / mudei:** Validei junto com a Ana que a chave de identificação do documento é diferente entre os dois carregadores (source_file vs. base_id|source_file, via _document_source_file), o que gera risco de duplicidade/documentos órfãos. Também confirmamos que o carregador do Luciano sempre sobrescreve title e source_url, enquanto o da Ana preserva o title já preenchido. Observei que esse comportamento do Luciano já evoluiu desde um relatório meu anterior, onde eu tinha apontado que o title ficava None — isso já foi corrigido do lado dele. Acompanhei também a verificação na documentação do PyPI de que networkx==3.7 exige Python 3.12+, incompatível com o Python 3.10.4 do ambiente.

### O que travou

- Mesmo conflito identificado com a Ana: divergência de chave de identificação e de critério de sobrescrita de campos entre os dois carregadores (base normativa vs. carregador do Luciano).
- Mesma incompatibilidade de ambiente: Python 3.10.4 incompatível com networkx e numpy==2.5.3 exigidos no requirements.txt, impedindo avançar para a indexação FAISS.

### Próximo passo

- Apoiar o alinhamento com o Luciano sobre qual padrão de chave e de sobrescrita de campos o grupo vai adotar entre os dois carregadores.
- Apoiar a migração do ambiente para Python 3.12+, para viabilizar a execução da indexação FAISS.

### Resumo do time no dia

- **Entregamos (base normativa):** Diagnóstico completo do conflito entre os dois carregadores de dados (chave de identificação de documento e política de sobrescrita de campos), formalizado e enviado ao Luciano para alinhamento.
- **Travou:** Decisão final sobre qual carregador/padrão de chave usar (depende do Luciano); configuração de ambiente impedindo a execução da indexação FAISS.
- **Próximo passo:** Fechar com o Luciano o padrão de chave e de sobrescrita de campos; migrar o ambiente para Python 3.12+ e recriar o .venv.

---

## Encontro 13 · 16/10/2026

### O que eu fiz hoje

- Eu e Ana criamos o ambiente virtual `.venv312` com Python 3.12.10.
- Instalei as dependências do `requirements.txt`.
- Verifiquei a versão do SQLAlchemy (2.1.1) (feito em conjunto com a Ana).
- Adicionei `.venv312/` ao `.gitignore` (feito em conjunto com a Ana).
- Fiz o commit `1f82b7b` na branch `base-normativa` e enviei ao GitHub, com conferência do escopo por `git show --stat HEAD` (feito em conjunto com a Ana).

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude Haiku
- **Para quê:** orientação de comandos do PowerShell e do Git, organização do plano de trabalho e rascunho do relatório.
- **O que conferi / mudei:**
  - Corrigimos o comando de busca, porque `Select-String` não aceita `-Recurse`. A recursão fica no `Get-ChildItem`.
  - Conferimos o escopo do commit antes de considerá-lo concluído.
  - Retiramos do rascunho afirmações não confirmadas, como o papel do ECOA e os motivos dos atrasos.

### O que travou

- A indexação ainda não foi iniciada.
- O comando para localizar a configuração do projeto ainda não foi executado com sucesso.
- O servidor ECOA caiu em alguns momentos .
- Falta confirmar o papel da Groq no projeto e se o `.venv312` vai virar padrão do grupo.
- Comparação dos carregadores de chunks (`persistencia.py` do grupo e `persistir_chunks_jsonl_normativos`, do Luciano, PR #46) ainda não executada. A decisão que o nosso carregador fica como padrão.

### Próximo passo

- Rodar o comando corrigido de busca e confirmar a configuração do projeto, sem expor chaves.
- Comparar os dois carregadores em ambiente de teste, antes de rodar qualquer um na base principal.
- Executar a consulta de documentos órfãos após cada carga.
- Confirmar o acesso ao servidor e, se estiver liberado, testar a conexão antes de indexar.

### Resumo do time no dia

- **Entregamos (base normativa):** commit `1f82b7b` na branch `base-normativa`, com `.venv312/` no `.gitignore` (Ana e Ester).
- **Travou:** indexação parada; acesso ao servidor a confirmar; decisão sobre o carregador depende de conversa com o Luciano.
- **Próximo passo:** confirmar a configuração e o acesso ao servidor e, depois, iniciar a indexação.

---

## Encontro 14 · 19/10/2026

### O que eu fiz hoje

Trabalhei com a Ana para fechar de vez o carregamento da base normativa e fazer a indexação vetorial.

O Luciano respondeu e escolheu a versão `normativo-v1` para a base normativa. Com isso unificamos os dois carregadores em um só. Antes de mexer, conferi se dava para fazer sem atrapalhar ninguém: o `pipeline_persistencia_normativa.py` dele só é chamado por ele mesmo, e nenhum outro arquivo importa a função auxiliar que ele continha. Mudamos só esse arquivo, que passou a chamar o `persistir()` do nosso carregador. Ele mantém os mesmos argumentos, mas o padrão deixou de ser o corpus de id 1 e passou a ser a versão `normativo-v1` resolvida pelo nome, porque o número do id é diferente em cada banco. Fizemos dois commits separados e abrimos o PR #53, que foi mesclado.

Para ter certeza de que o problema era real, rodei os dois carregadores em bancos temporários com os 794 trechos. Os trechos saem idênticos, mas a chave do documento era diferente: rodar um depois do outro dava 26 documentos, 13 deles sem nenhum trecho. Depois do ajuste, 13 documentos e nenhum órfão. Também descobri que a minha leitura da semana passada estava desatualizada: o carregador do Luciano já preenchia o título.

Rodei a migração no meu banco real. O resultado foi 13 chaves migradas para o prefixo, 13 URLs preenchidas, 794 trechos intactos, e conferi em seguida que nenhum documento ficou sem trecho.

Depois fizemos a indexação FAISS. Instalei o `faiss-cpu` e o `numpy`, testei com 10 trechos e rodei os 794. A estimativa que eu tinha dado, de 10 a 20 minutos, estava errada: levou cerca de 4 minutos, a 3 vetores por segundo. A auditoria deu 794 vetores para 794 trechos, cobertura de 100% nos 13 documentos, nenhum duplicado e nenhuma inconsistência.

Testei a busca com perguntas escritas com palavras diferentes das da lei. A busca por significado achou o Art. 86 (adesão à ata), o Art. 75 (dispensa por valor) e o Art. 84 (vigência da ata) onde a busca por palavra-chave errou. Mas nenhuma das buscas achou o Art. 4º da Lei 14.133, que é a resposta para "pequena empresa tem vantagem?", porque o texto dele fala em "Lei Complementar 123" e não em pequena empresa. E em duas perguntas a busca combinada piorou o resultado em relação à de significado.

Escrevemos o `eval/questions.json`, que estava vazio, com as dez perguntas de referência da base normativa, cada uma com a fonte conferida no banco. Medi um baseline nas sete que têm fonte: a busca combinada acertou 6 de 7 nos 3 primeiros e 7 de 7 nos 10 primeiros.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** comparar os dois carregadores, escrever a unificação e os testes, rodar a indexação e medir a busca.
- **O que eu conferi / mudei:** não aceitei que manter os dois carregadores era seguro sem testar, e a medição mostrou que dependia de passar o argumento certo em cada banco. Perguntei se podíamos mexer no pipeline do Luciano e só mexi depois de confirmar que ninguém mais o usava. A primeira busca com 10 trechos não provou nada sobre qualidade e só validou a indexação completa. Também percebi que a minha estimativa de tempo estava errada e passei a medir antes de estimar.

### O que travou

- O índice FAISS foi criado do zero, só com a base normativa. A aplicação lê `data/index/faiss/v1`, e o procedimento do time é preparar o staging a partir do `v1` e indexar em cima, então o nosso não pode substituí-lo. 
- O Art. 4º da Lei 14.133 não aparece em nenhuma busca para a pergunta de pequena empresa.

### Próximo passo

- Receber a resposta do grupo sobre o índice e, se for o caso, refazer o staging a partir do `v1` deles.
- Subir o `eval/questions.json` e transformar o script de medição no `eval/benchmark.py`.

### Resumo do time no dia

- **Entregamos (base normativa):** um carregador único na versão `normativo-v1` (PR #53), os 794 trechos migrados e indexados no FAISS com 100% de cobertura, e as perguntas de referência no `eval/questions.json`.
- **Travou:** a promoção do índice depende do grupo.
- **Próximo passo:** alinhar o índice com o grupo e medir a recuperação com o benchmark.

---

## Encontro 15 · 21/10/2026

### O que eu fiz hoje

Dia de fechar a base normativa e de preparar a apresentação de 23/10.

Li com a Ana as orientações da apresentação: 14h, de 15 a 20 minutos, todos apresentam, e a demonstração precisa mostrar também onde o sistema falha. A partir disso fizemos uma revisão completa da base normativa, olhando os testes, o banco, o índice, a privacidade e o que a principal já tem.

A revisão achou cinco inconsistências nos nossos arquivos, e corrigi todas. O hash do manifesto dependia do fim de linha: no meu Windows o arquivo vem com CRLF e no repositório está com LF, então o mesmo conteúdo tinha hashes diferentes. O manifesto prometia o metadado "objeto", que nenhum dos 794 trechos tem, e não declarava seis que existem. O hash gravado no inventário estava velho, porque o manifesto mudou depois dele. O CORPUS_INVENTORY dizia 25/09 e o JSON dizia 28/09, e a v2 aparecia mais antiga que a v1, efeito do fetch sobrescrevendo a data a cada execução. E o README só ensinava o fetch. Escrevemos testes novos, entre eles um que teria falhado com o manifesto antigo, e os testes da base normativa foram de 98 para 102. Fiz quatro commits separados e conferi o PR #54, aberto pela Ana: dez arquivos, sem banco, sem FAISS e sem BM25. Mesclei com merge commit, para manter os commits de cada uma.

O v1 do grupo tem 65.362 vetores do PNCP e já existe um staging/v2 com 66.482. Ele concorda com o nosso plano de copiar, acrescentar os 794 e auditar, com a publicação condicionada à validação. Por isso o nosso índice, que foi criado do zero, não pode substituir o do grupo.

Testei o sistema para a demonstração. Rodei o analisador nas dez perguntas de referência: acertou N1, N2, N5, N6, N7 e N10. Errou a base da N3 e da N9 (escolheu "agregada"), a rota da N4 (estruturada) e falhou na N8. A hipótese de que a N10 era a que o sistema ia errar não se confirmou. Na N8 conferi o que o modelo recebeu: a data certa do PNCP, 12/02/2026, chegava três vezes, e ele respondeu 09/02/2026. O erro é do modelo, não do nosso dado. E o limite de 30 segundos do ECOA derruba a geração.

Montei o kit para o gerente do grupo. Antes de subir o meu banco, conferi o conteúdo e vi que ele tinha duas contas de usuário e 12.070 registros brutos do PNCP. Em vez dele, gerei um banco limpo só com a normativa, 3 MB, e o índice de 794 vetores. Extraí o pacote numa pasta nova para provar que funciona sozinho.

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** Claude.
- **Para quê:** revisar a base, corrigir as inconsistências, testar o sistema e montar o pacote para o Drive.
- **O que eu conferi / mudei:** pedi para corrigir os erros antes do merge e conferi o diff do PR em vez de aceitar. Antes de enviar o banco, conferi o conteúdo e decidimos não subir o app.db. Não aceitei que a data errada da N8 fosse culpa do nosso dado: verifiquei o que o modelo recebia. Uma instrução que recebi estava errada, a de colocar o hash dentro do próprio zip, porque isso muda o hash; o hash ficou em arquivo separado.

### O que travou

- O índice consolidado depende de confirmar qual é a base mais atual, v1 ou v2, e se o banco compartilhado já tem os 794 trechos.
- O limite de 30 segundos do ECOA derruba a geração das respostas; falta decidir o valor ou configurar um provedor reserva.
- O analisador roteou errado as perguntas N3, N4, N8 e N9. 

### Próximo passo

- Preparar os slides do nosso bloco e ensaiar a demonstração em 22/10.

### Resumo do time no dia

- **Entregamos (base normativa):** cinco correções de consistência e quatro testes novos (PR #54 mesclado), revisão completa do estado da base, e um kit com banco limpo e índice para o gerente.
- **Travou:** o índice consolidado, e o limite de 30 s do ECOA ameaça a demonstração.
- **Próximo passo:** índice consolidado, slides e ensaio da demonstração.

---

## Encontro 16 · DD/MM/AAAA

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
