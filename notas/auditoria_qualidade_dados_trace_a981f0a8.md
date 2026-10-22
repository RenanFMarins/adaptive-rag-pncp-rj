# Auditoria de qualidade de dados ? trace a981f0a8

## Escopo e m?todo

Auditoria somente leitura do trace `a981f0a8-eacb-4bfc-bb6c-372ea3b481c5`, `app.db` aberto com `mode=ro` e metadados locais de `data/index/faiss/staging/v2` e do staging consolidado. N?o houve altera??o de banco, ?ndice ou c?digo; n?o foram usados LLM, rede ou embeddings externos.

## Resumo executivo

- O trace possui 156 chunk IDs ?nicos nas etapas de ranking; todos os 156 existem no banco.
- Todos os 156 t?m `base_id=editais_normativo`, coerente com o filtro registrado (`base_ids_permitidos=[editais_normativo]`).
- H?, contudo, mistura documental confirmada: 70 chunks de editais/PNCP, 73 de decretos e 13 de leis. Isso explica ru?do normativo, mas n?o prova corrup??o: os registros foram explicitamente classificados no banco como `editais_normativo`.
- Nenhum chunk recuperado estava vazio ou abaixo de 40 caracteres; n?o foram encontradas duplicidades de conte?do entre os 156 IDs.
- Os 32 chunks do Decreto 48.817/2023 pertencem ao `document_id=1900` e ao arquivo correto.
- O ?ndice consolidado declara 67.276 vetores, dimens?o 1024 e modelo `xagi/qwen3-embedding:0.6b-q4_k_m`; n?o foi poss?vel atribuir o trace a um manifesto espec?fico apenas pelo JSON do trace.

## Documentos e metadados

| Grupo | Quantidade de chunks no trace | Evid?ncia |
|---|---:|---|
| Decreto 48.817/2023 (`document_id=1900`) | 32 | `editais_normativo|decreto-48817-2023-gestao-fiscalizacao.pdf` |
| PNCP/editais (`document_id` 1905, 1908, 1909, 1906, 1907, 1903) | 70 | fontes `pncp_*_arq*.pdf` |
| Outros decretos/leis | 54 | decretos 48xxx, Decreto 48.760 e Lei 14.133 |

Todos os IDs examinados retornaram `document_id`, `chunk_id`, `base_id`, `doc_type` e `source_file`. A consulta normativa permitiu que fontes PNCP e editais fossem tratadas como parte da base normativa porque seus metadados usam `base_id=editais_normativo`; isso ? uma anomalia de classifica??o de corpus confirmada, embora n?o seja perda de integridade referencial.

## Filtros por canal

O trace registra `top_k=5`, `bm25_k=100`, `dense_k=100`, `local_limit=20` e 794 chunks eleg?veis na base normativa. BM25 e FAISS retornaram candidatos fora do Decreto 48.817, incluindo `editais_normativo:pncp_42498600000171_2025_921_arq1:18:p1`; a busca local tamb?m foi limitada ao documento identificado. A evid?ncia dispon?vel confirma aplica??o do filtro de base, mas n?o demonstra um filtro de `document_id` nos canais globais BM25/FAISS.

## Duplicidade e extra??o

- IDs ausentes no banco: 0/156.
- IDs duplicados no conjunto do trace: 0.
- Conte?dos SHA-256 duplicados entre IDs: 0 grupos.
- Conte?do vazio: 0.
- Conte?do com menos de 40 caracteres: 0.

N?o h? anomalia confirmada de truncamento apenas pelo comprimento. Trechos curtos ainda podem ser semanticamente incompletos e devem ser revisados no golden dataset.

## Decreto 48.817/2023

Os chunks do decreto recuperados pertencem ao documento 1900 e ao arquivo `decreto-48817-2023-gestao-fiscalizacao.pdf`. Os artigos 24, 25 e 26 est?o presentes no banco como `24:p1`, `25:p1`, `25:p2` e `26:p1`; n?o houve diverg?ncia de origem.

## FAISS e identificadores

Os manifests locais declaram modelo e dimens?o compat?veis entre `staging/v2` e o staging consolidado. O `staging/v2` registra 66.482 vetores no estado de checkpoints; o consolidado registra 67.276. O `base/chunk_ids.json` cont?m 65.362 IDs e representa apenas a base, enquanto os checkpoints representam deltas. Essa diferen?a de escopo impede comparar somente o arquivo base com o total do ?ndice. Nenhum arquivo foi modificado.

A confirma??o definitiva de correspond?ncia vetor-a-vetor exige carregar o ?ndice e reconciliar a uni?o base+checkpoints com os mapas de IDs; essa etapa n?o foi executada nesta auditoria para manter o diagn?stico estritamente documental.

## Anomalias confirmadas

1. **Mistura de corpus sob `base_id=editais_normativo` (156 candidatos, 70 de PNCP/editais).** Impacto: candidatos de editais e PNCP competem com normas no BM25, FAISS e RRF.
2. **Filtro global n?o restringe o documento normativo identificado.** Confirmado pelo pr?prio conjunto BM25/FAISS do trace; impacto: maior ru?do antes do RRF e do corte Top 5.

## Suspeitas que exigem verifica??o

- O trace n?o identifica explicitamente qual diret?rio FAISS foi carregado; comparar manifests n?o prova qual ?ndice gerou cada score.
- A diverg?ncia entre 65.362 IDs da base e 66.482/67.276 totais pode ser apenas composi??o por checkpoints, mas deve ser reconciliada por um mapa completo.
- Alguns trechos longos podem conter m?ltiplas se??es e prejudicar granularidade, sem constituir erro de extra??o.

## Problemas de ranking que n?o s?o anomalias

A presen?a de `22:p1`, `22:p2`, `22:p3` no Top 5, ou a aus?ncia de `24:p1`/`26:p1`, ? comportamento de ranking. Os dados desses chunks existem, t?m origem correta e n?o apresentam duplicidade ou truncamento confirmado.

## Recomenda??es por prioridade

1. **Alta:** separar `base_id`/filtro de corpus normativo de fontes PNCP e editais, preservando os registros e reindexando somente ap?s aprova??o.
2. **Alta:** aplicar filtro de `document_id` ou de documento normativo nos canais globais quando a consulta identifica uma norma.
3. **M?dia:** gerar uma reconcilia??o offline da uni?o base+checkpoints contra `app.db`, incluindo hashes de conte?do e contagem total.
4. **M?dia:** revisar chunks longos e os r?tulos de corpus no golden dataset antes de qualquer ajuste de ranking.
5. **Baixa:** tratar diferen?as de ranking e relev?ncia sem?ntica separadamente de anomalias de dados.

Nenhuma corre??o foi aplicada automaticamente.
