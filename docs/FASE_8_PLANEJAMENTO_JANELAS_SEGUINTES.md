# PNCP/RJ — Fase 8: planejamento das janelas seguintes

Data: 2026-10-19

Branch: `feature/ingestao-incremental-pncp`

## 1. Ponto de partida

```text
watermark composto: 2026-10-16T23:59:59.999999
último dia integralmente fechado: 2026-10-18
início do incremental oficial: 2026-10-16
overlap_days: 2
max_window_days: 1
```

O dia 19/10 não entrou no plano porque ainda não estava integralmente
fechado no fuso operacional durante a auditoria.

## 2. Plano calculado

`plan_closed_windows()` produziu, em ordem:

| Data | Tipo | Modalidades | Motivo |
|---|---|---:|---|
| 2026-10-16 | `REPROCESS` | 14 | sobreposição do intervalo confirmado |
| 2026-10-17 | `RUN` | 14 | primeira janela ainda não coberta |
| 2026-10-18 | `RUN` | 14 | segunda janela ainda não coberta |

O piso de 16/10 impede o planejador de tentar reprocessar 15/10, data anterior
à ativação incremental oficial.

## 3. Suporte a reprocessamento controlado

O planejador de cobertura recebeu a opção:

```text
--reprocess-completed
```

Sem essa opção, uma cobertura concluída retorna `14 SKIP`. Com ela, a mesma
janela retorna `14 REPROCESS`. O executor converte a ação em
`IncrementalRunConfig(reprocess=True)` e preserva as demais proteções:

- confirmação redundante do banco;
- log absoluto;
- intervalo mínimo de 30 segundos;
- parada no primeiro erro;
- identidade canônica e hash para impedir versões duplicadas;
- observação idempotente da mesma janela, cursor e ordinal.

## 4. Simulação da sobreposição

Comando somente leitura:

```bash
python3 -m src.fetch_incremental_coverage \
  --date 2026-10-16 \
  --reprocess-completed \
  --db-path "/caminho/absoluto/data/debug/pncp_contracts_2023_t1_all.db"
```

Resultado:

```text
ready: true
REPROCESS: 14
BLOCK: 0
```

Nenhuma chamada à API ou escrita no SQLite ocorreu durante a simulação.

## 5. Ordem obrigatória

As datas devem ser executadas estritamente na ordem 16, 17 e 18. A validação
de continuidade rejeita uma tentativa de 18/10 antes da conclusão de 17/10,
antes de consumir a API.

Cada data representa 14 shards. Com intervalo de 30 segundos, o tempo mínimo
de espera entre shards é 6 minutos e 30 segundos por data. A estimativa para
as três coberturas é de aproximadamente 22 a 30 minutos, dependendo da
latência e da paginação do PNCP.

## 6. Validação

```text
testes direcionados: 16 passed
suíte completa: 263 passed
git diff --check: sem erros
plano de 16/10: 14 REPROCESS
```

## 7. Decisão

**PLANO DAS JANELAS 16–18/10 APROVADO EM MODO SOMENTE LEITURA.**

As três janelas ainda não foram executadas. Antes de iniciá-las é necessário:

1. criar um novo backup do banco apó a Fase 7;
2. reconfirmar que não existem coletores ativos;
3. executar 16/10 com `--reprocess-completed`;
4. auditar a idempotência;
5. executar 17/10 e, depois, 18/10;
6. validar o novo watermark composto e a integridade final.
