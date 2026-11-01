# Corpus normativo operacional

## Resultado

Em 01/11/2026, o corpus `normativo-v1` foi integrado ao `app.db` operacional
por meio da pipeline idempotente de persistência normativa. O banco não faz
parte do Git.

| Componente | Antes | Depois |
| --- | ---: | ---: |
| Documentos processados | 2 | 15 |
| Chunks processados | 55 | 849 |
| Linhas no FTS5 | 55 | 849 |
| Documentos normativos | 0 | 13 |
| Chunks normativos | 0 | 794 |

Os 13 documentos normativos possuem URL de origem. A versão
`normativo-v1` permanece separada da versão estruturada `pncp-2026-08`, e os
chunks usam `base_id=editais_normativo`.

## Procedimento seguro

Antes da alteração, a execução foi homologada em um SQLite temporário. O
piloto e a aplicação operacional apresentaram os mesmos resultados:

- 794 linhas válidas e nenhuma inválida;
- 13 documentos e 794 chunks criados na primeira execução;
- zero documentos e zero chunks criados na segunda execução;
- 794 chunks reconhecidos como existentes na segunda execução.

Foi criado um backup consistente com a API de backup do SQLite em
`data/backups/app_pre_normative_corpus_20261101.db.gz`. O diretório é ignorado
pelo Git. SHA-256 local do backup:

```text
6de0649b319364bf08ba8b343c7a1383fe326868d011199d77b2291d7f5748c5
```

## Validação

Após a integração:

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- 15 documentos, 849 chunks e 849 linhas no FTS5;
- 13 documentos normativos com URL de origem;
- busca FTS5/BM25 por competências de fiscais retornou cinco resultados
  normativos rastreáveis, incluindo o Decreto RJ 48.817/2023 nas primeiras
  posições.

Para repetir a importação de forma idempotente:

```bash
DATABASE_URL=sqlite:///./app.db \
python3 -m src.base_estruturada.pipelines.pipeline_persistencia_normativa \
  --versao v1 \
  --arquivo-chunks data/processed/v1_editais_normativo.jsonl \
  --inventario data/inventory/v1_editais_normativo.json
```

## Limitação atual

Esta etapa habilita a recuperação lexical FTS5/BM25 dos 794 chunks. Ela não
gera embeddings. O índice FAISS selecionado pela aplicação continua sendo o
piloto OpenAI com 55 vetores da base estruturada. A próxima etapa deve gerar
um índice compatível para o corpus ampliado e, depois, comparar BM25, FAISS e
RRF usando o mesmo benchmark.
