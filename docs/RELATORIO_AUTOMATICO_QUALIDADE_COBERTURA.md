# Relatório automático de qualidade e cobertura

O comando abaixo gera, para um snapshot normalizado, um relatório JSON
adequado a automações e uma versão Markdown para revisão humana:

```bash
python3 -m scripts.generate_quality_coverage_report
```

Saídas padrão:

- `/tmp/pncp_quality_coverage_report.json`;
- `/tmp/pncp_quality_coverage_report.md`.

O processo abre tanto a base normalizada quanto a RAW com `mode=ro` e
`PRAGMA query_only=ON`. Os arquivos gerados contêm somente contagens e
classificações agregadas. Payloads, perguntas, fornecedores e registros
individuais não são copiados para o relatório.

## O que é verificado

- `PRAGMA integrity_check` e `PRAGMA foreign_key_check`;
- contagem real das tabelas e comparação com `normalization_coverage`;
- intervalo temporal e distribuição anual dos recursos;
- lacunas conhecidas e estados `COMPLETE`/`PARTIAL`;
- completude da linhagem RAW;
- relacionamentos órfãos;
- datas suspeitas de resultados;
- anos anômalos de contratos e atas;
- contratos acima de R$ 1 bilhão;
- valores financeiros negativos.

As três auditorias detalhadas são executadas contra a RAW e resumidas no
relatório. Quando somente a release normalizada estiver disponível, ainda é
possível gerar a parte independente da RAW:

```bash
python3 -m scripts.generate_quality_coverage_report --without-raw-audits
```

## Reprodutibilidade

A referência temporal do relatório vem de `normalization_run.finished_at`, e
não do relógio da máquina. O identificador do snapshot e a versão da
transformação também são registrados. Assim, duas execuções sobre o mesmo
snapshot produzem os mesmos dados de auditoria.

`COMPLETE` significa completo em relação ao snapshot declarado. Não significa
cobertura de todo o histórico do PNCP.
