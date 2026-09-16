# Acompanhamento · Ana Karina

**Time:** 03 · Contratações Públicas do Estado do RJ
**Papel:** Base normativa (com a Ester) · minha frente: processamento dos documentos

---

## Encontro 1 · 16/09/2026

### O que eu fiz hoje

Fiquei com a base normativa junto com a Ester, que reúne a Lei 14.133/2021, os decretos
estaduais e os editais das contratações do RJ.

Criei a branch `base-normativa` para a gente trabalhar separado da principal.

Combinamos que Ester e eu fariamos tudo juntas logo cuidamos da coleta e do processamento: extrair o
texto dos PDFs, dividir por artigo ou cláusula e montar os metadados de cada
trecho. Por isso, hoje fiquei com a seção 4.1 do ARQUITETURA.md. Completei a
descrição da base com o identificador (`editais_normativo`), o formato, o uso
esperado, a estratégia de chunking, os metadados e a questão da vigência.

Uma coisa que eu entendi melhor escrevendo essa parte é que a lei não pode ser
cortada em pedaços de tamanho fixo: se um artigo for separado dos seus
parágrafos, a resposta pode sair incompleta ou errada. Por isso, a ideia é
dividir respeitando a hierarquia (artigo, parágrafo, inciso) e guardar essa
referência no metadado, para a resposta citar exatamente o artigo.
[ajustar com a sua visão]

### Onde usei IA e o que mudei no resultado

- **Ferramenta:** [qual usou]
- **Para quê:** [ex.: sugerir a estrutura da seção 4.1 e a lista de metadados]
- **O que eu conferi / mudei:** [ex.: comparei com os metadados obrigatórios do
  enunciado; corrigi o nome da Ester, que estava diferente em duas partes do
  documento; reescrevi ... ]

### O que travou

- [ex.: dúvida sobre como juntar a minha alteração no ARQUITETURA.md com a
  versão que o Alisson subiu, sem dar conflito]
- [ex.: ainda não sei qual biblioteca usar para extrair texto de PDF]

### Próximo passo

- Pesquisar bibliotecas de extração de texto de PDF e testar com a Lei 14.133.
- Começar o chunking por artigo em `src/ingest.py`.
- Criar o teste que verifica se todo chunk tem os metadados obrigatórios
  (`source_file`, `doc_type`, `chunk_id`, `sensitivity`, `base_id`).

---

## Resumo do time no dia

- **Entregamos:** [igual ao da Ester ou com a sua visão]
- **Travou:** [...]
- **Próximo passo:** [...]