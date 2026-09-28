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

## Encontro 6 · DD/MM/AAAA

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
