# Migrações controladas da camada RAW

Os arquivos deste diretório não são executados automaticamente em bancos
existentes. Essa decisão evita que a abertura de um banco histórico altere uma
base real sem revisão e backup.

## Backup seguro antes de uma migração

1. Confirme que não existe coletor gravando no banco.
2. Use a API de backup do SQLite para criar um arquivo novo em outro caminho.
3. Execute `PRAGMA quick_check` e `PRAGMA foreign_key_check` na cópia.
4. Gere SHA-256 do original e da cópia e registre tamanho e data.
5. Aplique a migração primeiro em outra cópia descartável.
6. Compare tabelas, contagens por recurso e chaves estrangeiras.

## 001_raw_canonical_identity_index.sql

Adiciona somente um índice não único sobre os campos já existentes:

```text
(base_id, resource_type, external_id)
```

O índice não altera payloads, checkpoints ou identificadores. Ele torna
eficiente a procura da mesma entidade quando ela é observada por coletores com
nomes de `source` diferentes.

## Identidades preservadas

- Entidade canônica: `(base_id, resource_type, external_id)`.
- Fonte/job: `source`.
- Execução: `ingestion_run_id`.
- Versão RAW: `raw_asset.id`.
- Conteúdo: `payload_hash` calculado sobre o JSON canônico.
- Momento da observação no PNCP: `source_updated_at`.

O `external_id` continua sendo produzido pelos coletores a partir das chaves
de negócio verificadas:

| Recurso | `external_id` |
|---|---|
| PCA | `idPcaPncp` |
| Contratação | `numeroControlePNCP` |
| Item | `numeroControlePNCP` + `numeroItem` |
| Resultado | `numeroControlePNCPCompra` + `numeroItem` + `sequencialResultado` |
| Contrato | `numeroControlePNCP` |
| Empenho | `numeroControlePNCPContrato` + `sequencialEmpenho` |
| Ata | `numeroControlePNCPAta` |

Por isso, `external_id` isolado não é tratado como globalmente único. Em
bancos históricos, onde `source_updated_at` ainda está vazio, o repositório
consulta o campo equivalente dentro do payload original. Se a API não fornecer
nenhuma data de atualização, uma repetição exata é tratada como replay
idempotente; sem um marcador temporal externo, ela não pode ser distinguida de
uma reversão exata posterior.

Exemplo de backup consistente (substitua os dois caminhos):

```bash
python3 -c 'import sqlite3; origem=sqlite3.connect("file:ORIGEM.db?mode=ro", uri=True); destino=sqlite3.connect("COPIA.db"); origem.backup(destino); destino.close(); origem.close()'
```

Não copie diretamente um arquivo `.db` enquanto houver um escritor ativo,
pois o estado pode também depender dos arquivos `-wal` e `-shm`.

## 002_sync_window_checkpoint.sql

Adiciona o controle de sincronização v2 sem converter nem renomear
`sync_checkpoint`:

- `sync_job`: identidade determinística da configuração, incluindo modo,
  recurso, endpoint, UF, modalidade e filtros;
- `sync_window`: intervalo diário fechado e inclusivo, estado, cursor e lease;
- `sync_target_progress`: progresso por identidade estável do alvo e seu
  fingerprint de configuração;
- `sync_watermark`: posição confirmada da fonte, com desempate para registros
  que possuem o mesmo timestamp.

O modelo legado continua sendo lido e escrito exclusivamente pelo fluxo
histórico atual. O modelo v2 não interpreta `last_page`, e sua ativação exige
uma migração explícita do banco e a seleção explícita do novo orquestrador.
Isso permite validar cada fonte separadamente antes da transição.

### Reversão

Enquanto nenhuma coleta v2 tiver sido ativada, a reversão consiste em remover,
em uma cópia e nesta ordem, `sync_watermark`, `sync_target_progress`,
`sync_window` e `sync_job`. Depois da ativação, esses registros são evidência de
auditoria; portanto, devem ser exportados e preservados antes de qualquer
remoção. A reversão nunca exige alterar `raw_asset`, `ingestion_run` ou
`sync_checkpoint`.

## 003_raw_observation.sql

Adiciona `raw_observation` sem alterar nenhuma linha de `raw_asset`. A tabela
separa a observação feita por uma execução da versão RAW observada:

- `observation_key` identifica de forma determinística a mesma observação
  quando uma janela é reexecutada;
- `raw_asset_id` aponta para a versão append-only que foi persistida;
- a janela distingue uma reversão posterior de um replay;
- cursor e ordinal ficam registrados para auditoria, mas não integram a chave,
  pois a paginação da API pode mudar entre execuções;
- status, tipo e valor normalizado do timestamp registram se a ordenação
  temporal é confiável.

Registros históricos permanecem válidos mesmo sem uma linha correspondente
em `raw_observation`. Depois da migração, novas versões persistidas recebem o
metadado sem atualizar ou remover qualquer payload anterior.
