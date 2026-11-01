# Piloto FAISS com embeddings OpenAI

O provedor de embeddings é independente do provedor de geração. A chave deve
existir somente no `.env` local e nunca deve ser enviada ao Git.

Configuração para OpenAI:

```dotenv
OPENAI_API_KEY=preencha-localmente
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1024
EMBEDDING_TIMEOUT_SECONDS=60
```

O identificador persistido no FAISS inclui provedor, modelo e dimensão. Um
índice Ecoa e um índice OpenAI nunca devem compartilhar o mesmo diretório.

## Construção controlada

Primeiro use um diretório de staging e um limite pequeno:

```bash
.venv/bin/python -m \
  src.base_estruturada.pipelines.pipeline_indexacao_faiss \
  --indice-dir data/index/faiss/staging/openai-v1 \
  --limite-chunks-novos 55 \
  --tamanho-lote 10 \
  --tamanho-checkpoint 55 \
  --origem piloto_operacional
```

Depois audite sem gerar novos embeddings:

```bash
.venv/bin/python -m \
  src.base_estruturada.pipelines.pipeline_indexacao_faiss \
  --auditar \
  --indice-dir data/index/faiss/staging/openai-v1
```

Somente selecione o staging em `RAG_FAISS_INDEX_DIR` depois de validar
contagens, dimensão, modelo e checksums. A indexação usa a chave configurada e
pode gerar custo externo; portanto, o limite deve ser mantido no primeiro
ensaio.

## Homologação operacional de 01/11/2026

O piloto de 55 vetores foi copiado para um staging independente
`data/index/faiss/staging/openai-v2`. Cinco chunks normativos foram indexados
primeiro como ensaio real. Após validar modelo, dimensão, hashes e retomada, os
789 chunks normativos restantes foram processados em checkpoints de 50.

Resultado final:

| Indicador | Resultado |
| --- | ---: |
| Vetores estruturados | 55/55 |
| Vetores normativos | 794/794 |
| Total | 849/849 |
| Dimensão | 1.024 |
| IDs órfãos ou duplicados | 0 |
| Conteúdos alterados | 0 |
| Checkpoints ativos após compactação | 1 |

Modelo persistido:

```text
openai:text-embedding-3-small:d1024
```

A compactação preservou os 18 shards anteriores e um snapshot de estado para
rollback. A segunda execução encontrou zero chunks pendentes. O SHA-256 do
estado local homologado é:

```text
48b3dc7b501bd1eb2504a386baddd6a969f4bcbfb223e66c5a5799f3d649b2c1
```

O teste semântico "Quais são as competências dos fiscais de contrato?" retornou
nas primeiras posições o Decreto RJ 48.817/2023 e o art. 117 da Lei
14.133/2021. Com `RAG_FAISS_INDEX_DIR` apontando para o `openai-v2`, a API
respondeu HTTP 200 em `/health` e `/ready`, com o componente `vector_index`
marcado como pronto.

O diretório `data/index/` é ignorado pelo Git. O resultado acima descreve o
artefato operacional local; não afirma que o índice acompanha um clone limpo.
