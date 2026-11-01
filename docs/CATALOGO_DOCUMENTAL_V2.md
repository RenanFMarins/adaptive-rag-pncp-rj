# Catálogo documental PNCP v2

O catálogo registra os arquivos anunciados pelo PNCP sem baixar ou processar
seu conteúdo. A identidade lógica permanece:

```text
(tipo_entidade, numero_controle_pncp, sequencial_documento)
```

O inventário é identificado pelo SHA-256 do conjunto ordenado de manifestos e
de seus conteúdos. A tabela de membros preserva as observações históricas e o
estado atual informa se a fonte continua disponível.

## Validação segura em uma cópia

Pare a API e qualquer processo que escreva no SQLite. Use a API de backup do
SQLite, pois copiar somente `app.db` pode ignorar transações presentes no WAL:

```bash
sqlite3 app.db ".backup '/tmp/pncp-app-backup.db'"
cp --reflink=auto /tmp/pncp-app-backup.db /tmp/pncp-catalog-test.db
sqlite3 /tmp/pncp-catalog-test.db < migrations/102_document_catalog_v2.sql
```

Reconcilie todos os manifestos locais somente na cópia:

```bash
.venv/bin/python -m \
  src.base_estruturada.pipelines.pipeline_persistencia_catalogo_documentos \
  --todos-manifestos-locais \
  --tipo todos \
  --snapshot-completo \
  --database-url sqlite:////tmp/pncp-catalog-test.db
```

Valide antes e depois:

```bash
sqlite3 -readonly /tmp/pncp-catalog-test.db \
  "PRAGMA integrity_check; PRAGMA foreign_key_check;"
```

`--snapshot-completo` exige `--todos-manifestos-locais --tipo todos`. Essa
proteção impede que um recorte mensal marque os demais documentos como
removidos.

## Resultado operacional

Em 01/11/2026, a reconciliação foi primeiro homologada em uma cópia isolada e
depois aplicada ao `app.db` local. Foram lidos 90 manifestos mensais, 329.750
entidades e 549.171 referências documentais:

| Tipo da entidade | Referências |
| --- | ---: |
| Contratação | 335.565 |
| Contrato | 213.606 |
| **Total** | **549.171** |

A validação retornou `integrity_check=ok`, zero violações de chave
estrangeira, zero chaves de negócio duplicadas, zero registros sem URL e zero
documentos inválidos. A segunda execução classificou as 549.171 referências
como inalteradas e não inseriu nenhuma linha, confirmando a idempotência.

O backup anterior à importação foi criado pela API de backup do SQLite e
mantido localmente em `data/backups/`, diretório ignorado pelo Git. O banco e o
backup não fazem parte do commit.

Os metadados preservam valores fornecidos pelo PNCP. A auditoria encontrou três
referências com ano `2950` e uma com ano `20024`; elas devem ser tratadas como
anomalias de qualidade, não corrigidas silenciosamente no catálogo.

Catálogo e corpus processado têm finalidades diferentes: as 549.171 entradas
indicam arquivos disponíveis e suas URLs. Em 01/11/2026, o corpus operacional
contém 15 documentos e 849 chunks: 13 documentos/794 chunks normativos e 2
documentos/55 chunks estruturados. Consultar o conteúdo dos demais arquivos
catalogados ainda depende da fila de processamento sob demanda.

## Diagnósticos offline sem copiar o banco operacional

Os testes factuais e de regressão normativa aceitam um snapshot explícito:

```bash
PNCP_REGRESSION_SNAPSHOT=data/debug/pncp_normative_demo.db \
  python -m pytest -q
```

Quando a variável é informada, o snapshot é aberto em modo somente leitura e
não é copiado. Sem a variável, os testes ainda podem criar uma cópia isolada
do `app.db`, mas recusam automaticamente essa operação quando o arquivo excede
512 MiB. Essa proteção impede que um catálogo grande esgote o disco durante a
suíte.
