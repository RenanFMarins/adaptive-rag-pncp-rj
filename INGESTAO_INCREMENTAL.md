# Ingestão incremental PNCP — simulação offline

## Situação atual

`src/fetch_corpus.py` continua sendo o orquestrador histórico e mantém o
checkpoint legado `sync_checkpoint`. Seu comportamento operacional não foi
substituído.

`src/fetch_incremental.py` é um ponto de entrada separado. Nesta etapa ele:

- exige `--offline`;
- exige uma fixture JSON local;
- aceita somente banco SQLite em `/tmp`;
- utiliza exclusivamente os checkpoints v2;
- reutiliza a persistência RAW, a identidade canônica e o versionamento já
  existentes;
- não cria nem utiliza cliente HTTP.

A coleta incremental real ainda não está habilitada.

## Execução segura

Exemplo funcional com a fixture sintética do repositório:

```bash
python3 -m src.fetch_incremental \
  --resource contratacao \
  --uf RJ \
  --start-date 2023-04-01 \
  --end-date 2023-04-30 \
  --modality 6 \
  --offline \
  --fixture tests/fixtures/incremental/contratacao_offline.json \
  --db-path /tmp/pncp_incremental_offline.db
```

Também é possível chamar o arquivo diretamente a partir da raiz:

```bash
python3 src/fetch_incremental.py --help
```

Não existe banco padrão. Caminhos relativos ou fora de `/tmp` são recusados.

## Retomada e reprocessamento

Uma janela que falhou ou perdeu o lease exige retomada explícita:

```bash
python3 -m src.fetch_incremental \
  --resource contratacao \
  --uf RJ \
  --start-date 2023-04-01 \
  --end-date 2023-04-30 \
  --offline \
  --resume \
  --fixture tests/fixtures/incremental/contratacao_offline.json \
  --db-path /tmp/pncp_incremental_offline.db
```

Uma janela concluída somente pode ser executada novamente com
`--reprocess`. Retomada e reprocessamento são mutuamente exclusivos.

## Jobs, janelas e watermark

O `job_id` é derivado deterministicamente de:

- nome lógico do job;
- modo incremental;
- recurso;
- estratégia;
- endpoint lógico offline;
- UF;
- modalidade;
- filtros da configuração.

O intervalo não faz parte do job: ele identifica a `sync_window`. Assim, o
mesmo job pode possuir várias janelas fechadas e inclusivas. O watermark usa o
valor explícito da fixture ou, na ausência dele, o fim determinístico da janela;
nunca usa o horário local de conclusão como posição da fonte.

## Estratégias por recurso

| Recurso | Suporte offline | Estratégia | Situação para API real |
|---|---:|---|---|
| `pca` | Sim | `endpoint` | endpoint de atualização ainda deve ser confirmado |
| `contratacao` | Sim | `endpoint` | endpoint e semântica de atualização ainda devem ser confirmados |
| `contrato` | Sim | `endpoint` | endpoint de atualização ainda deve ser confirmado |
| `ata` / `ata_registro_preco` | Sim | `endpoint` | endpoint de atualização ainda deve ser confirmado |
| `contratacao_item` | Sim | `relationship` | depende de contratação-pai alterada |
| `resultado_item` | Sim | `relationship` | depende de item/contratação alterados |
| `empenho` | Sim | `relationship` | depende de contrato-pai alterado |

Nenhum endpoint real foi inventado ou habilitado.

## Formato das fixtures

Recursos com estratégia `endpoint` usam páginas:

```json
{
  "strategy": "endpoint",
  "watermark_value": "2023-04-30T23:59:59Z",
  "pages": [
    {
      "cursor": "1",
      "records": [
        {
          "external_id": "identidade-canônica-do-registro",
          "payload": {"campo": "valor"}
        }
      ]
    }
  ]
}
```

Recursos com estratégia `relationship` agrupam páginas por alvo estável:

```json
{
  "strategy": "relationship",
  "targets": [
    {
      "target": {"numero_controle": "compra-pai"},
      "pages": [
        {
          "cursor": "1",
          "records": [
            {
              "external_id": "compra-pai|1",
              "payload": {"numeroItem": 1}
            }
          ]
        }
      ]
    }
  ]
}
```

`external_id` é obrigatório para evitar que a fixture invente regras de
identidade diferentes das regras dos coletores reais.

## Renovação de lease

A renovação é cooperativa e ocorre no mesmo worker, entre os eventos da fonte.
Não existe thread adicional. Os parâmetros são:

```text
--lease-seconds
--lease-renewal-seconds
```

O intervalo de renovação deve ser menor que a duração do lease. A duração do
lease também deve ser maior que o tempo máximo de uma única operação bloqueante.
Se uma operação individual ultrapassar o lease, a confirmação é recusada e a
janela permanece recuperável depois da expiração.

## Banco existente

Uma cópia de banco histórico precisa receber, manualmente e nessa ordem:

```text
migrations/001_raw_canonical_identity_index.sql
migrations/002_sync_window_checkpoint.sql
```

As migrações não são aplicadas automaticamente em bancos existentes. Nunca use
o snapshot original como destino da simulação.

## Pendências antes da ativação online

1. Confirmar os endpoints e parâmetros de atualização no PNCP.
2. Definir a semântica do watermark por recurso.
3. Implementar os adaptadores HTTP reais por estratégia.
4. Validar reconciliação de pais alterados com itens, resultados e empenhos.
5. Definir política operacional de janelas sobrepostas.
6. Aplicar as migrações somente após backup e homologação.

