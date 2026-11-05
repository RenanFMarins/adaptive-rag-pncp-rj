# Relatório de qualidade e cobertura PNCP/RJ — 05/11/2026

- **Schema do relatório:** `pncp_quality_coverage_report_v1`
- **Snapshot:** `5308d5e5897768d2c52439145c0ab77fb8dc3b8a44c4d2c48f2ae4412538870a`
- **Transformação:** `normalized-v2-incremental`
- **Referência:** `2026-11-05T16:01:47.312464+00:00`
- **Execução:** SQLite em modo somente leitura; saída exclusivamente agregada.

## Resumo

- Recursos marcados como completos: **5**
- Recursos parciais: **2**
- Lacunas conhecidas: **4**
- Divergências entre registro de cobertura e tabela: **0**
- Violações de chave estrangeira: **0**
- Entidades com mais de uma linhagem marcada como atual: **0**

## Contagens por tabela

| Tabela | Registros |
| --- | ---: |
| `orgao` | 618 |
| `unidade` | 2.117 |
| `fornecedor` | 42.766 |
| `contratacao` | 180.419 |
| `contratacao_item` | 557.211 |
| `resultado_item` | 417.675 |
| `contrato` | 151.898 |
| `empenho` | 1.900 |
| `ata_registro_preco` | 82.713 |
| `pca` | 567 |
| `pca_item` | 228.469 |
| `pca_contratacao_link` | 0 |

## Cobertura declarada

| Recurso | Estado | Registros | Lacunas | Confere |
| --- | --- | ---: | ---: | :---: |
| `ata_registro_preco` | PARTIAL | 82.713 | 0 | sim |
| `contratacao` | COMPLETE | 180.419 | 0 | sim |
| `contratacao_item` | COMPLETE | 557.211 | 0 | sim |
| `contrato` | COMPLETE | 151.898 | 0 | sim |
| `empenho` | PARTIAL | 1.900 | 4 | sim |
| `pca` | COMPLETE | 567 | 0 | sim |
| `resultado_item` | COMPLETE | 417.675 | 0 | sim |

`COMPLETE` significa completo em relação ao snapshot e ao inventário do
projeto, não em relação a todo o universo histórico do PNCP.

## Ampliação das atas

- Inventário congelado: **617 CNPJs e 2.116 pares órgão–unidade**.
- Janelas anuais: **4**, entre 01/01/2023 e 31/10/2026.
- Alvos concluídos: **8.464 de 8.464**.
- Atas antes da ampliação: **80.761**.
- Atas após a ampliação: **82.713**.
- Novas entidades normalizadas: **1.952**.
- Cobertura temporal: 3.862 atas de 2023, 22.999 de 2024, 32.969 de 2025,
  22.782 de 2026 e 101 com ano anômalo `2424` preservado da fonte.

As dimensões possuem uma entidade adicional em relação ao inventário:
o CNPJ `28176998000441` e a unidade `927255`, do Corpo de Bombeiros/Defesa
Civil. Essa entidade veio de outra fonte normalizada; todos os membros do
inventário congelado estão presentes.

## Indicadores de qualidade

- Resultados com data suspeita: **72**
- Contratos com ano posterior a 2100: **4**
- Atas com ano posterior a 2100: **101**
- Contratos acima de R$ 1 bilhão: **14**
- Valores financeiros negativos: **1**

As anomalias confirmadas na RAW são preservadas e sinalizadas, sem correção
silenciosa.

## Integridade dos relacionamentos

| Verificação | Órfãos/inconsistências |
| --- | ---: |
| `contratacao_item_without_contratacao` | 0 |
| `resultado_without_item` | 0 |
| `resolved_contract_without_contratacao` | 0 |
| `empenho_without_contract` | 0 |
| `ata_with_missing_resolved_parent` | 0 |
| `pca_item_without_pca` | 0 |

## Auditorias contra a RAW

Estado: **COMPLETED**.

- Datas suspeitas: `SOURCE_DATA_ANOMALY`
- Anos anômalos: `SOURCE_DATA_ANOMALY`
- Contratos bilionários: `SOURCE_VALUES_PRESERVED_WITH_QUALITY_WARNINGS`

## Limitações

- Atas e empenhos possuem cobertura parcial.
- `pca_contratacao_link` vazio não autoriza inferir associações.
- O inventário de atas foi derivado das contratações históricas e não
  representa necessariamente todos os órgãos do PNCP.
- Os bancos operacionais e seus backups permanecem fora do versionamento Git.
