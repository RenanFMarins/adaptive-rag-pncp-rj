# Ingestão incremental PNCP — offline e piloto online controlado

## Situação atual

`src/fetch_corpus.py` continua sendo o orquestrador histórico e mantém o
checkpoint legado `sync_checkpoint`. Seu comportamento operacional não foi
substituído.

`src/fetch_incremental.py` é um ponto de entrada separado. Nesta etapa ele:

- exige a escolha explícita entre `--offline`, `--online-pilot` e
  `--online-operational`;
- no modo offline, exige uma fixture JSON local;
- no modo online, aceita `contratacao`, `contrato`, `pca`,
  `ata_registro_preco`, `contratacao_item`, `resultado_item` ou `empenho`,
  sempre com UF RJ e uma janela de exatamente um dia;
- `contratacao` exige uma modalidade entre 1 e 14;
- `contrato`, `pca` e `ata_registro_preco` exigem um par CNPJ/unidade presente
  no inventário congelado e não aceitam modalidade;
- `contratacao_item`, `resultado_item` e `empenho` exigem o identificador de uma
  execução-pai compatível, concluída e validada no RJ;
- aceita somente banco SQLite em `/tmp`;
- utiliza exclusivamente os checkpoints v2;
- reutiliza a persistência RAW, a identidade canônica e o versionamento já
  existentes;
- nunca usa um banco padrão implícito.

A coleta real possui entrada controlada para contratações, contratos, PCA e
atas.
Os pilotos de contratações e contratos já foram validados contra a API real
em bancos isolados em `/tmp`. No PCA, os casos HTTP 200 e 204, a descoberta e
a recuperação do plano integral estão homologados. O piloto de atas foi
homologado com respostas HTTP 200 e 204, validação de escopo e reprocessamento
idempotente. Itens de contratação, resultados homologados e empenhos estão
habilitados de forma controlada. A cadeia contratação → item → resultado foi
homologada com payloads reais. Para empenhos, tanto o HTTP 404 contextual
quanto o HTTP 200 com payload e reprocessamento idempotente foram homologados.

O transporte comum e os adaptadores de endpoint já possuem respostas tipadas
e preservam a diferença entre 200, 204 e 404 contextual. Contratações,
contratos, atas e o fluxo de descoberta + plano integral do PCA são exercitados
por transporte simulado e por um piloto real isolado em `/tmp`.

`src/ingestion/adapter_runner.py` integra esses adaptadores aos checkpoints v2,
à persistência RAW e ao watermark. Esse runner não cria cliente HTTP e recusa
bancos e logs fora de `/tmp`. A rota online cria o cliente somente depois de
validar todas as travas do piloto.

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

Piloto online real, limitado a um dia e uma modalidade:

```bash
python3 -m src.fetch_incremental \
  --resource contratacao \
  --uf RJ \
  --start-date 2023-04-01 \
  --end-date 2023-04-01 \
  --modality 6 \
  --online-pilot \
  --db-path /tmp/pncp_incremental_pilot.db
```

O banco precisa ser novo ou uma cópia que tenha recebido as migrações
`001`–`005`. Requisições e ingestão geram logs JSONL ao lado do banco.

Piloto de um membro da cobertura de contratos:

```bash
python3 -m src.fetch_incremental \
  --resource contrato \
  --uf RJ \
  --start-date 2023-04-01 \
  --end-date 2023-04-01 \
  --organization-cnpj 00038166000105 \
  --unit-code 925136 \
  --scope-inventory config/pncp_rj_scope_inventory.json \
  --online-pilot \
  --db-path /tmp/pncp_incremental_contrato_pilot.db
```

O endpoint de contratos não aceita UF. Por isso o CLI não envia `uf` na URL:
ele comprova o recorte do RJ pelo par CNPJ/unidade do inventário e ainda
valida CNPJ, unidade e UF de cada payload retornado. O plano de cobertura com
2.116 membros é registrado automaticamente; executar um único membro não
declara a janela completa.

O PCA usa as mesmas travas de inventário:

```bash
python3 -m src.fetch_incremental \
  --resource pca \
  --uf RJ \
  --start-date 2026-01-01 \
  --end-date 2026-01-01 \
  --organization-cnpj 00038166000105 \
  --unit-code 925136 \
  --scope-inventory config/pncp_rj_scope_inventory.json \
  --online-pilot \
  --db-path /tmp/pncp_incremental_pca_pilot.db
```

O feed fragmentado serve apenas para descobrir PCAs alterados. Antes de emitir
qualquer registro, o adaptador busca o endpoint direto de cada plano, valida
seu CNPJ, unidade e integridade e persiste uma representação RAW integral.
Como `dataFim` é exclusivo nesse feed, o adaptador acrescenta um dia somente ao
parâmetro HTTP final. A janela, o checkpoint e o watermark continuam
representando exatamente o dia solicitado.

As atas também usam o inventário congelado:

```bash
python3 -m src.fetch_incremental \
  --resource ata_registro_preco \
  --uf RJ \
  --start-date 2026-01-01 \
  --end-date 2026-01-01 \
  --organization-cnpj 00038166000105 \
  --unit-code 925136 \
  --scope-inventory config/pncp_rj_scope_inventory.json \
  --online-pilot \
  --db-path /tmp/pncp_incremental_ata_pilot.db
```

O JSON de ata não possui UF. O recorte territorial é comprovado pelo membro
CNPJ/unidade do inventário do RJ; o adaptador valida que esses dois campos do
payload correspondem exatamente ao membro solicitado.

Itens de contratação são descobertos exclusivamente a partir de uma execução
incremental pai, concluída no mesmo banco:

```bash
python3 -m src.fetch_incremental \
  --resource contratacao_item \
  --uf RJ \
  --start-date 2026-10-16 \
  --end-date 2026-10-16 \
  --parent-run-id ID_DA_EXECUCAO_PAI \
  --online-pilot \
  --db-path /tmp/pncp_incremental_itens_pilot.db
```

O `parent_run_id` não é aceito como uma lista arbitrária de controles PNCP. A
execução precisa existir, ter terminado com sucesso, ser do recurso
`contratacao` e conter somente registros cuja unidade esteja no RJ. Assim, a
fila de reconciliação recebe alvos auditáveis derivados da RAW, sem confiar em
identificadores informados manualmente.

Resultados homologados seguem a mesma regra, usando como pai uma execução de
itens concluída no mesmo banco:

```bash
python3 -m src.fetch_incremental \
  --resource resultado_item \
  --uf RJ \
  --start-date 2026-10-16 \
  --end-date 2026-10-16 \
  --parent-run-id ID_DA_EXECUCAO_DE_ITENS \
  --online-pilot \
  --db-path /tmp/pncp_incremental_resultados_pilot.db
```

Cada alvo contém o controle PNCP e o número do item. Antes da consulta, o
coletor resolve a contratação ancestral na RAW e confirma sua UF; itens sem pai
ou fora do RJ são rejeitados.

Empenhos são descobertos a partir de uma execução de contratos concluída:

```bash
python3 -m src.fetch_incremental \
  --resource empenho \
  --uf RJ \
  --start-date 2026-10-16 \
  --end-date 2026-10-16 \
  --parent-run-id ID_DA_EXECUCAO_DE_CONTRATOS \
  --online-pilot \
  --db-path /tmp/pncp_incremental_empenhos_pilot.db
```

O contrato pai precisa estar concluído e ter UF RJ. Nesse endpoint, HTTP 404
significa que o contrato consultado não possui empenhos disponíveis; o alvo é
registrado como `NOT_FOUND`, sem criar um ativo RAW artificial.

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

## Monitoramento e retomada automática

Os templates em `ops/systemd/` executam o piloto sempre com `--resume` e
`Restart=on-failure`, aguardando 30 minutos entre falhas. `--resume` também é
válido para uma janela ainda inexistente; por isso o mesmo comando serve para
iniciar e recuperar. Os templates são exemplos e não são instalados ou ativados
automaticamente.

O acompanhamento pode ser feito pelo journal e pelos logs JSONL em `/tmp`:

```bash
journalctl --user -u pncp-incremental-pilot.service -f
tail -f /tmp/pncp_incremental_pilot.http.jsonl
tail -f /tmp/pncp_incremental_pilot.incremental.jsonl
```

## Planejamento de janelas e sobreposição

`plan_closed_windows()` gera janelas inclusivas e determinísticas sem usar o
maior timestamp recebido como cursor. A política padrão revisita dois dias já
confirmados e limita cada janela a um dia. Tanto `overlap_days` quanto
`max_window_days` são configuráveis e validados. Janelas que atravessam o
watermark confirmado são marcadas explicitamente para reprocessamento.

## Jobs, janelas e watermark

O `job_id` é derivado deterministicamente de:

- nome lógico do job;
- modo incremental;
- recurso;
- estratégia;
- endpoint e filtros do adaptador;
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
| `pca` | Sim | `endpoint` | HTTP 200/204, plano integral e idempotência homologados |
| `contratacao` | Sim | `endpoint` | piloto online explícito habilitado somente em `/tmp` |
| `contrato` | Sim | `endpoint` | piloto real homologado por CNPJ/unidade, restrito a um dia |
| `ata` / `ata_registro_preco` | Sim | `endpoint` | piloto real homologado por CNPJ/unidade, restrito a um dia |
| `contratacao_item` | Sim | `relationship` | piloto real homologado a partir de execução-pai validada no RJ |
| `resultado_item` | Sim | `relationship` | piloto real homologado a partir de execução de itens validada no RJ |
| `empenho` | Sim | `relationship` | HTTP 200 com payload e HTTP 404 contextual homologados |

Nenhum endpoint dependente aceita alvos arbitrários no CLI.

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

O formato acima permanece compatível e considera cada entrada simultaneamente
uma descoberta do pai e uma resposta simulada. Para testar filhos tardios sem
fingir uma nova alteração do pai, use o contrato explícito:

```json
{
  "strategy": "relationship",
  "discoveries": [],
  "responses": [
    {
      "target": {"numero_controle": "compra-pai", "numero_item": 1},
      "outcome": "FOUND",
      "pages": [
        {
          "records": [
            {
              "external_id": "compra-pai|1|1",
              "payload": {"sequencialResultado": 1}
            }
          ]
        }
      ]
    }
  ]
}
```

`discoveries` representa pais novos ou alterados. `responses` representa o que
o adaptador encontrou ao consultar os alvos que a fila durável declarou devidos.
Os resultados aceitos são:

- `FOUND`: um ou mais registros;
- `EMPTY`: consulta válida sem registros, incluindo `200 []` ou `204`;
- `NOT_FOUND`: ausência contextual, como o `404` observado para empenhos.

Erros de transporte ou HTTP não elegíveis não são resultados vazios: eles
falham a janela e não avançam o reagendamento do alvo.

## Reconciliação de recursos dependentes

Itens, resultados e empenhos são mantidos em
`sync_reconciliation_target`. Uma resposta vazia conclui somente a tentativa
atual; o alvo recebe uma próxima data e pode ser consultado novamente sem que o
pai tenha mudado. A janela anterior continua imutável.

Baseline operacional congelada em `config/pncp_incremental_policy.json`:

| Recurso | Cadência | Horizonte |
|---|---:|---:|
| Item | 1 dia | 365 dias |
| Resultado | 1 dia | 365 dias |
| Empenho | 7 dias | 730 dias |

Esses valores estão aprovados para piloto, não constituem SLA do PNCP. Devem
ser reavaliados após 30 dias de observação. Podem ser sobrescritos por
`--reconciliation-cadence-days` e
`--reconciliation-horizon-days`. A conclusão em `sync_target_progress` e o
reagendamento da fila ocorrem na mesma transação.

`external_id` é obrigatório para evitar que a fixture invente regras de
identidade diferentes das regras dos coletores reais.

`discover_dependency_targets()` extrai somente pais `NEW/UPDATED` de uma
execução concluída. Replays `UNCHANGED` não criam nova descoberta; continuam
cobertos pela reconciliação periódica.

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
migrations/003_raw_observation.sql
migrations/004_sync_reconciliation_target.sql
migrations/005_sync_coverage_manifest.sql
```

Em 17/10/2026, as cinco migrações foram aplicadas a uma cópia integral do
banco operacional com 1.322.020 registros RAW. `PRAGMA integrity_check`
retornou `ok`, `PRAGMA foreign_key_check` não retornou violações e as contagens
RAW permaneceram iguais. O banco oficial não foi migrado.

## Versões RAW e observações

`raw_asset` armazena versões imutáveis. `raw_observation` registra cada janela
que observou uma versão, inclusive quando o resultado é `UNCHANGED`. Assim,
duas janelas podem apontar para o mesmo `raw_asset` sem duplicar o payload, e a
reexecução da mesma janela continua idempotente.

## Cobertura composta

Um watermark de job comprova somente aquele shard. Quando a cobertura depende
de várias modalidades, órgãos ou unidades, configure um manifesto congelado:

```text
--coverage-name contratacoes-rj-modalidades
--coverage-member modalidade:6
--coverage-members modalidade:1 modalidade:2 modalidade:3 modalidade:6
```

Todas as execuções da mesma janela devem repetir exatamente o mesmo nome e
conjunto de membros, mudando apenas `--coverage-member`. O conjunto não pode
ser ampliado silenciosamente depois da primeira janela. A execução informa
`coverage_status=PENDING` enquanto faltar algum membro e `COMPLETED` somente
quando o manifesto inteiro estiver coberto.

Para recursos particionados por órgão/unidade, `build_scope_inventory()`
constrói um inventário ordenado e deduplicado a partir de payloads de
contratação. CNPJ, unidade e UF são obrigatórios; registros fora do recorte ou
incompletos interrompem a construção. O hash `inventory_id` identifica o
conjunto congelado e `coverage_members` alimenta o manifesto composto.

O inventário congelado está em `config/pncp_rj_scope_inventory.json`:

- `inventory_id`:
  `inventory-fec7430eec6a854f91858dc1996a504bc9a50818f4de20dfa79b7b8d1ff2897f`;
- 2.116 pares órgão/unidade e 617 CNPJs;
- modalidades esperadas 1–14; a modalidade 2 não apareceu na RAW examinada,
  mas permanece como membro esperado;
- contratos e atas observados estão contidos no inventário;
- foram observados 839 pares órgão/unidade nos PCAs: 292 dentro do inventário
  e 547 fora dele. Dos 1.578 planos, 567 ficaram integralmente dentro do
  inventário e 1.011 possuem ao menos um par externo, pois a coleta antiga
  consultou por CNPJ. O adaptador incremental agora exige e valida também
  `codigoUnidade`.

A completude declarada é relativa à RAW histórica de contratações, não a um
cadastro externo oficial de todos os órgãos do estado.

As migrações não são aplicadas automaticamente em bancos existentes. Nunca use
o snapshot original como destino da simulação.

## Evidências do piloto real

Em uma cópia migrada em `/tmp` foram validados:

- HTTP 200 com 62 contratações em duas páginas;
- HTTP 204 como janela válida vazia;
- HTTP 404 de empenho como `NOT_FOUND` contextual;
- retry 503 → 200 em transporte HTTP local controlado;
- contratação → 38 itens, dos quais 28 novos em relação ao snapshot;
- item novo → resultado homologado novo;
- integridade e chaves estrangeiras válidas após todas as execuções.

Em 05/11/2026, o piloto de contratos também foi homologado em um banco novo e
descartável em `/tmp`, usando um único membro do inventário e a janela de
16/10/2026:

- HTTP 200 com um contrato, classificado como `NEW`;
- reprocessamento da mesma janela classificou a entidade como `UNCHANGED`,
  sem criar outra versão RAW;
- a janela adjacente sem registros retornou HTTP 204 e foi concluída sem erro;
- o payload confirmou o mesmo CNPJ, unidade e UF RJ do membro solicitado;
- a cobertura permaneceu `PENDING`, com 1 de 2.116 membros concluído;
- `PRAGMA integrity_check` retornou `ok` e `foreign_key_check` não apontou
  violações.

Também em 05/11/2026, o piloto de empenhos partiu de um membro válido do
inventário e da janela de contratos de 16/10/2026:

- o feed de contratos retornou HTTP 200 com um contrato `NEW`, no escopo exato
  de CNPJ, unidade e UF RJ;
- a execução-pai originou um alvo de empenho sem entrada manual de controle
  PNCP;
- o endpoint do alvo retornou HTTP 404 nas duas execuções, ambas concluídas
  com sucesso e com resultado de reconciliação `NOT_FOUND`;
- nenhum ativo RAW de empenho vazio foi criado;
- a cobertura do contrato permaneceu `PENDING`, com somente 1 de 2.116 membros
  concluído;
- `PRAGMA integrity_check` retornou `ok` e `foreign_key_check` não apontou
  violações.

Essa evidência homologa o encadeamento, o transporte e o significado contextual
do 404.

Em 06/11/2026, um segundo piloto isolado homologou o retorno HTTP 200 de
empenhos. O contrato `00059311000126-2-000912/2026`, já conhecido na RAW
histórica, foi usado somente para selecionar um membro válido do inventário:

- o feed do dia 06/10/2026 retornou quatro contratos `NEW`, todos com CNPJ,
  unidade e UF RJ compatíveis com o escopo solicitado;
- a descoberta dependente gerou quatro alvos sem entrada manual dos controles
  PNCP;
- os quatro endpoints de empenho responderam HTTP 200 e produziram quatro
  ativos RAW, todos com `sequencialEmpenho`;
- o reprocessamento consultou novamente os quatro alvos e classificou os quatro
  registros como `UNCHANGED`, sem criar novas versões ou observações
  duplicadas;
- os quatro alvos terminaram com reconciliação `FOUND` e nenhum empenho ficou
  órfão de seu contrato-pai;
- `PRAGMA integrity_check` retornou `ok`, `foreign_key_check` não apontou
  violações e nenhum contrato ficou fora do RJ.

Com os dois pilotos, os contratos HTTP do recurso estão homologados para
presença e ausência contextual. Ainda é necessário observar alterações reais
ao longo do tempo para validar a propagação de atualizações.

Na mesma data, o piloto de PCA foi executado em outro banco descartável em
`/tmp`. Três janelas de um dia, para dois membros válidos do inventário,
retornaram HTTP 204 e foram concluídas corretamente:

- nenhum ativo RAW vazio ou artificial foi criado;
- as três execuções e janelas terminaram com sucesso;
- as coberturas permaneceram `PENDING`, sem declarar completude indevida;
- a comparação diagnóstica com e sem o filtro opcional de unidade retornou o
  mesmo HTTP 204, descartando esse filtro como causa da janela vazia;
- `PRAGMA integrity_check` retornou `ok` e não houve violações de chave
  estrangeira.

Essa evidência homologa o transporte e o caso vazio.

Em 06/11/2026, o caso HTTP 200 foi homologado com um membro válido do
inventário e a janela lógica de 02/04/2025. A auditoria da API demonstrou que
`dataFim` é exclusivo no feed de atualização de PCA; por isso o adaptador passou
a enviar 03/04/2025 como limite HTTP, sem ampliar a janela interna:

- o feed fragmentado respondeu HTTP 200 e descobriu um PCA;
- o endpoint de detalhe respondeu HTTP 200 com o plano integral e 96 itens;
- CNPJ, unidade, ano e sequencial dos itens foram validados contra o plano e o
  membro congelado do inventário;
- a primeira execução criou uma entidade `NEW` e o reprocessamento classificou
  a mesma entidade como `UNCHANGED`;
- permaneceu somente uma versão RAW e uma observação, sem duplicação;
- as quatro respostas HTTP das duas execuções foram 200;
- `PRAGMA integrity_check` retornou `ok` e `foreign_key_check` não apontou
  violações.

Ainda em 05/11/2026, o piloto de atas foi homologado em um banco novo e
descartável em `/tmp`, usando o membro CNPJ `00394452000103`, unidade `160270`,
do inventário congelado do RJ:

- a janela de 30/10/2026 retornou HTTP 200 com três atas, todas classificadas
  como `NEW` na primeira execução;
- o reprocessamento da mesma janela classificou as três entidades como
  `UNCHANGED`, sem criar outra versão RAW;
- a janela de 01/11/2026 retornou HTTP 204 e foi concluída sem criar ativos
  RAW vazios ou artificiais;
- todos os payloads persistidos confirmaram o CNPJ e a unidade solicitados;
- o watermark não retrocedeu quando a janela de 30/10 foi processada depois da
  janela de 01/11;
- cada cobertura permaneceu `PENDING`, com somente 1 de 2.116 membros
  concluído;
- `PRAGMA integrity_check` retornou `ok` e `foreign_key_check` não apontou
  violações.

A comparação diagnóstica também mostrou que uma consulta mais ampla, sem o
filtro de unidade, pode retornar HTTP 500 no próprio PNCP. O piloto operacional
mantém por isso o par CNPJ/unidade do inventário, que reduz a carga e comprova
o recorte territorial sem inferir UF ausente no payload da ata.

O piloto de itens de contratação foi homologado na mesma data, em outro banco
novo e descartável em `/tmp`:

- uma janela de contratações de 16/10/2026, modalidade 12 e UF RJ retornou
  quatro entidades `NEW`;
- o `run_id` dessa execução-pai originou quatro alvos de reconciliação, sem
  entrada manual de controles PNCP;
- os quatro endpoints paginados retornaram 96 itens, todos classificados como
  `NEW` na primeira execução;
- o reprocessamento classificou os mesmos 96 itens como `UNCHANGED`, mantendo
  somente 96 versões RAW e 96 observações;
- todos os alvos terminaram como `COMPLETED` e `FOUND`, sem itens órfãos;
- nenhum pai estava fora do RJ;
- `PRAGMA integrity_check` retornou `ok` e `foreign_key_check` não apontou
  violações.

Na sequência, o piloto de resultados homologados reutilizou a cadeia de pais
no mesmo banco descartável:

- a primeira tentativa da janela-pai terminou em timeout e foi registrada como
  `FAILED`; a retomada explícita com `--resume` concluiu a janela com quatro
  contratações;
- os quatro pais produziram 96 itens e, por sua vez, 96 alvos de resultado;
- um alvo retornou 16 resultados homologados e 95 retornaram HTTP 204, todos
  tratados como conclusões válidas;
- o reprocessamento classificou os 16 registros como `UNCHANGED`, sem criar
  novas versões ou observações;
- permaneceram exatamente 4 contratações, 96 itens e 16 resultados na RAW,
  sem resultado órfão e sem contratação ancestral fora do RJ;
- `PRAGMA integrity_check` retornou `ok` e `foreign_key_check` não apontou
  violações.

## Pendências para ativação operacional

1. Obter uma fonte externa oficial para medir a completude absoluta do
   inventário de órgãos/unidades do RJ.
2. Acompanhar longitudinalmente um empenho alterado para verificar se o
   contrato-pai também muda; os retornos HTTP 200 e 404 já foram comprovados.
3. Criar a orquestração/scheduler que consome janelas planejadas e descobertas
   de dependência com retomada automática.
4. Obter autorização específica antes de aplicar `001`–`005` no banco oficial.
