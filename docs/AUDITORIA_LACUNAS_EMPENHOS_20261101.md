# Auditoria das quatro lacunas conhecidas de empenhos

## Escopo

Esta auditoria revalidou os quatro alvos de empenho que permaneceram sem
resposta bem-sucedida na coleta histórica. Nenhum banco foi modificado.

Todos os alvos pertencem ao CNPJ `28523215000106`, ano 2026:

| Sequencial do contrato | Tentativas históricas | Resultado histórico | Estado em 01/11/2026 |
| ---: | ---: | --- | --- |
| 1032 | 3 | HTTP 500 | HTTP 502 |
| 1060 | 3 | HTTP 500 | HTTP 503 |
| 1070 | 2 | HTTP 500 | HTTP 503 |
| 1120 | 2 | HTTP 500 | HTTP 503 |

A verificação atual consultou somente o status dos endpoints oficiais e
descartou o corpo da resposta. Ela não executou o coletor, não alterou
checkpoints e não gravou payloads na RAW.

## Interpretação

Os quatro alvos continuam indisponíveis no serviço de origem. HTTP 500, 502 e
503 não demonstram que um contrato não possui empenhos; demonstram apenas que
o PNCP não entregou uma resposta utilizável para esses identificadores.

Por isso:

1. nenhuma linha vazia ou sintética foi criada;
2. os 1.900 empenhos existentes foram preservados;
3. `empenho` permanece com cobertura `PARTIAL`;
4. `known_gap_count=4` permanece correto;
5. a tarefa é encerrada como **lacuna externa confirmada e justificada**, não
   como recuperação de registros.

Uma nova tentativa pode ser realizada futuramente. Somente uma resposta
oficial bem-sucedida deve reduzir `known_gap_count` e alimentar a normalizada.

## Evidência histórica

As tentativas estão registradas em `ingestion_run`, no snapshot RAW local. A
primeira ocorreu em 18/10/2026 07:13 UTC e a última terminou em 18/10/2026
15:07 UTC. O encerramento administrativo e a classificação original também
estão documentados em
[`FASE_0_AUDITORIA_RAW.md`](FASE_0_AUDITORIA_RAW.md).
