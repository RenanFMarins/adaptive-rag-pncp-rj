# Auditoria de anos anômalos em contratos e atas

## Resultado

A base normalizada possui quatro contratos com anos claramente inválidos e
101 atas com `ano_ata=2424`:

| Entidade | Ano observado | Linhas | Ano coerente pelas datas/identificador |
| --- | ---: | ---: | ---: |
| contrato | 2302 | 1 | 2023 |
| contrato | 2950 | 1 | 2024 |
| contrato | 4761 | 1 | 2023 |
| contrato | 20024 | 1 | 2024 |
| ata | 2424 | 101 | 2024 |

Os 194 contratos de 2021 e 2022 não são automaticamente erros: todos possuem o
mesmo ano no identificador PNCP e 139 também coincidem com o ano de assinatura.
Os demais podem ter assinatura posterior ao ano identificador. Eles aparecem no
snapshot porque foram publicados ou atualizados dentro do universo coletado.

## Origem e linhagem

Nos 105 registros anômalos:

- o ativo RAW corrente foi localizado;
- o ano normalizado é idêntico ao campo `anoContrato` ou `anoAta` da RAW;
- o hash normalizado coincide com o hash do payload RAW;
- existe uma única versão RAW por identidade, sem ano alternativo corrigido.

Nos quatro contratos, o ano incorreto também integra o
`numeroControlePNCP`. Nas atas, o identificador contém `/2024-...` e as datas
são de 2024, mas o campo de origem informa `2424`. Isso torna o erro das atas
um provável erro de digitação no sistema de origem.

## Impacto

- filtros entre 2023 e 2026 deixam de retornar 4 contratos e 101 atas;
- contagens anuais por `ano_contrato` ou `ano_ata` ficam subestimadas;
- as datas de assinatura e publicação continuam utilizáveis quando filtradas
  explicitamente, mas não devem substituir silenciosamente o ano informado;
- corrigir o ano sem nova evidência quebraria a fidelidade da camada RAW.

## Decisão

Preservar os valores originais e classificá-los no relatório de qualidade. Uma
futura coluna de ano inferido pode ser adicionada separadamente, com método e
confiança explícitos, sem sobrescrever o campo de origem.

Comando reproduzível, somente leitura:

```bash
.venv/bin/python scripts/audit_anomalous_entity_years.py
```

A saída agregada é gravada em
`/tmp/pncp_anomalous_entity_years_audit.json`.
