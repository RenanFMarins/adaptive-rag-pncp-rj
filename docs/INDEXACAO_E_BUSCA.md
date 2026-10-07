# Indexação e busca híbrida

Este guia descreve como o projeto transforma documentos já processados em
evidências recuperáveis pelo RAG. Ele vale para a base estruturada do PNCP e
para documentos adicionados pelas demais frentes da equipe.

## Arquitetura

```text
Contratos e contratações JSON
  -> raw_asset (SQLite)
  -> consultas factuais por SQL

Documento original -> Docling -> Markdown -> chunks JSONL
  -> Document + DocumentChunk (SQLite, fonte de verdade)
  -> FTS5 (busca lexical persistente)
  -> FAISS (vetor + chunk_id)
  -> RRF
  -> texto e metadados recuperados de DocumentChunk
```

`raw_asset` não é copiado integralmente para o FAISS. Ele permanece como fonte
para filtros, contagens, valores, datas e modalidades. O FAISS contém apenas
chunks documentais que precisam de busca semântica.

## Artefatos e responsabilidades

| Artefato | Conteúdo | Fonte de verdade? |
|---|---|---|
| JSONL de chunks | texto dividido e metadados de um lote | artefato canônico portátil |
| `Document` / `DocumentChunk` | texto, metadados e vínculos relacionais | sim |
| FTS5 | índice lexical do SQLite | não; é derivado de `DocumentChunk` |
| FAISS | embeddings e lista ordenada de `chunk_id` | não; é derivado de `DocumentChunk` |

O `chunk_id` liga os resultados do FAISS ao chunk persistido. O FTS5 usa o
`DocumentChunk.id` como `rowid` interno. Portanto os textos não precisam ser
duplicados nos índices.

## Fluxo para a base PNCP por lote

1. Baixar e processar o lote no Docling.
2. Gerar o JSONL de chunks do lote:

   ```powershell
   python -m src.base_estruturada.pipelines.pipeline_chunks `
     --periodo 2026/08 --lote lote_001 --versao v1
   ```

3. Persistir o JSONL no SQLite. Esta etapa é idempotente: chunks com o mesmo
   `chunk_id` são ignorados.

   ```powershell
   python -m src.base_estruturada.pipelines.pipeline_persistencia_documentos `
     --periodo 2026/08 --lote lote_001 --versao v1 `
     --corpus-version-id 1
   ```

4. Acrescentar somente os chunks daquele lote ao índice FAISS:

   ```powershell
   python -m src.pipeline_indexacao_faiss `
     --arquivo-chunks data/chunks/v1/2026/chunks_2026_08_lote_001.jsonl `
     --indice-dir data/index/faiss/v1 `
     --origem 2026_08_lote_001 `
     --tamanho-lote 50
   ```

5. Consultar. A consulta nunca gera embeddings dos documentos; ela somente usa
   FTS5, FAISS e os chunks já persistidos.

   ```powershell
   python -m src.retrieve "Qual é o prazo de vigência do contrato?" `
     --cache-dir data/index/faiss/v1
   ```

## Continuidade após interrupção

O FAISS salva `chunks.faiss`, `chunk_ids.json` e `estado_indexacao.json` a cada
microlote. Se a execução falhar, rode o mesmo comando novamente. Apenas os
`chunk_id` que ainda não estiverem no índice receberão embeddings.

Não apague manualmente somente um dos três arquivos do índice. Para começar um
índice novo, use outro diretório, por exemplo `data/index/faiss/v2`.

## Como outras bases da equipe entram

Uma equipe não precisa gerar lote mensal. Após persistir `DocumentChunk`, ela
usa a mesma pipeline com filtros. Exemplos:

```powershell
# Todos os chunks de uma base
python -m src.pipeline_indexacao_faiss `
  --base-id base_normativa `
  --indice-dir data/index/faiss/v1

# Uma versão específica de corpus
python -m src.pipeline_indexacao_faiss `
  --corpus-version-id 2 `
  --indice-dir data/index/faiss/v1
```

O FTS5 é atualizado automaticamente por triggers quando um `DocumentChunk` é
inserido, alterado ou removido. Se for necessário reparar ou conferir o índice
lexical, execute:

```powershell
python -m src.pipeline_reconstruir_fts
```

## Operação e limites

- O primeiro FTS5 é preenchido automaticamente ao inicializar o banco após a
  atualização. A reconstrução manual só é necessária para manutenção.
- O progresso exibido pela indexação FAISS representa os embeddings novos do
  comando atual; chunks já indexados não são recalculados.
- O diretório `data/index/` é local e derivado, por isso não vai para Git.
- Trocar o modelo de embedding exige um novo diretório de índice, pois a
  dimensão ou o espaço vetorial podem mudar.
- Perguntas factuais devem ser respondidas por SQL sobre `raw_asset`; FTS5 e
  FAISS servem para recuperação textual e semântica de documentos.
