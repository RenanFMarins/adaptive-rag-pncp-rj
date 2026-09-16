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

### O que travou

- ainda não encontrei os decretos estaduais do RJ que regulamentam a Lei 14.133

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
