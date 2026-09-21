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

## Encontro 4 · DD/MM/AAAA

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
