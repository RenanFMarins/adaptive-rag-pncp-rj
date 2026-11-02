"""Gera um relatório agregado e reproduzível de qualidade e cobertura.

Os bancos SQLite são abertos exclusivamente em modo somente leitura. A saída
não inclui payloads RAW, nomes de fornecedores ou registros individuais.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from scripts.audit_anomalous_entity_years import audit_anomalous_years
from scripts.audit_billion_contracts import audit_billion_contracts
from scripts.audit_suspect_result_dates import audit_suspect_result_dates

DEFAULT_NORMALIZED_DB = Path("data/normalized/pncp_rj_normalized.db")
DEFAULT_RAW_DB = Path("data/debug/pncp_contracts_2023_t1_all.db")
DEFAULT_JSON_OUTPUT = Path("/tmp/pncp_quality_coverage_report.json")
DEFAULT_MARKDOWN_OUTPUT = Path("/tmp/pncp_quality_coverage_report.md")

ENTITY_TABLES = (
    "orgao",
    "unidade",
    "fornecedor",
    "contratacao",
    "contratacao_item",
    "resultado_item",
    "contrato",
    "empenho",
    "ata_registro_preco",
    "pca",
    "pca_item",
    "pca_contratacao_link",
)

TEMPORAL_FIELDS = {
    "contratacao": ("data_publicacao_pncp", "ano_compra"),
    "resultado_item": ("data_resultado", None),
    "contrato": ("data_publicacao_pncp", "ano_contrato"),
    "empenho": ("data_emissao", "ano"),
    "ata_registro_preco": ("data_publicacao_pncp", "ano_ata"),
    "pca": ("data_publicacao_pncp", "ano_pca"),
    "pca_item": ("data_desejada", None),
}

RELATIONSHIP_CHECKS = {
    "contratacao_item_without_contratacao": """
        SELECT COUNT(*) FROM contratacao_item child
        LEFT JOIN contratacao parent
          ON parent.numero_controle_pncp = child.numero_controle_pncp
        WHERE parent.numero_controle_pncp IS NULL
    """,
    "resultado_without_item": """
        SELECT COUNT(*) FROM resultado_item child
        LEFT JOIN contratacao_item parent
          ON parent.numero_controle_pncp = child.numero_controle_pncp
         AND parent.numero_item = child.numero_item
        WHERE parent.numero_controle_pncp IS NULL
    """,
    "resolved_contract_without_contratacao": """
        SELECT COUNT(*) FROM contrato child
        LEFT JOIN contratacao parent
          ON parent.numero_controle_pncp = child.contratacao_id
        WHERE child.contratacao_id IS NOT NULL
          AND parent.numero_controle_pncp IS NULL
    """,
    "empenho_without_contract": """
        SELECT COUNT(*) FROM empenho child
        LEFT JOIN contrato parent
          ON parent.numero_controle_pncp = child.numero_controle_contrato
        WHERE parent.numero_controle_pncp IS NULL
    """,
    "ata_with_missing_resolved_parent": """
        SELECT COUNT(*) FROM ata_registro_preco child
        LEFT JOIN contratacao parent
          ON parent.numero_controle_pncp = child.contratacao_id
        WHERE child.contratacao_id IS NOT NULL
          AND parent.numero_controle_pncp IS NULL
    """,
    "pca_item_without_pca": """
        SELECT COUNT(*) FROM pca_item child
        LEFT JOIN pca parent ON parent.id_pca_pncp = child.id_pca_pncp
        WHERE parent.id_pca_pncp IS NULL
    """,
}

LINEAGE_TABLES = (
    "contratacao",
    "contratacao_item",
    "resultado_item",
    "contrato",
    "empenho",
    "ata_registro_preco",
    "pca",
    "pca_item",
)


def _readonly_uri(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(2, "Banco SQLite não encontrado", str(path))
    return f"{path.resolve().as_uri()}?mode=ro"


def _connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(_readonly_uri(path), uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def _scalar(connection: sqlite3.Connection, query: str, parameters: Iterable[Any] = ()) -> int:
    value = connection.execute(query, tuple(parameters)).fetchone()[0]
    return int(value or 0)


def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
    return connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def _latest_run(connection: sqlite3.Connection) -> dict[str, Any] | None:
    if not _table_exists(connection, "normalization_run"):
        return None
    row = connection.execute(
        """
        SELECT id, source_snapshot_sha256, transform_version, started_at,
               finished_at, status, records_seen, records_written,
               records_skipped, records_rejected
        FROM normalization_run
        ORDER BY COALESCE(finished_at, started_at) DESC
        LIMIT 1
        """
    ).fetchone()
    return dict(row) if row else None


def _table_counts(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        table: _scalar(connection, f'SELECT COUNT(*) FROM "{table}"')
        for table in ENTITY_TABLES
        if _table_exists(connection, table)
    }


def _coverage_registry(
    connection: sqlite3.Connection, table_counts: dict[str, int]
) -> list[dict[str, Any]]:
    if not _table_exists(connection, "normalization_coverage"):
        return []
    rows = connection.execute(
        """
        SELECT resource_type, coverage_status, period_start, period_end,
               expected_parent_count, processed_parent_count, record_count,
               known_gap_count, inventory_id, notes, updated_at
        FROM normalization_coverage
        ORDER BY resource_type
        """
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        actual = table_counts.get(str(item["resource_type"]))
        item["actual_record_count"] = actual
        item["record_count_matches_table"] = (
            actual is None or actual == item["record_count"]
        )
        result.append(item)
    return result


def _temporal_coverage(connection: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for table, (date_field, year_field) in TEMPORAL_FIELDS.items():
        if not _table_exists(connection, table):
            continue
        row = connection.execute(
            f"""
            SELECT MIN({date_field}) AS first_date,
                   MAX({date_field}) AS last_date,
                   SUM({date_field} IS NULL) AS missing_dates
            FROM {table}
            """
        ).fetchone()
        item: dict[str, Any] = {
            "first_date": row["first_date"],
            "last_date": row["last_date"],
            "missing_dates": int(row["missing_dates"] or 0),
        }
        if year_field:
            years = connection.execute(
                f"""
                SELECT CAST({year_field} AS TEXT) AS year, COUNT(*) AS records
                FROM {table}
                GROUP BY {year_field}
                ORDER BY {year_field}
                """
            ).fetchall()
            item["records_by_year"] = {
                str(year["year"]): int(year["records"]) for year in years
            }
        result[table] = item
    return result


def _quality_indicators(connection: sqlite3.Connection) -> dict[str, Any]:
    result_status = {
        str(row["status"]): int(row["records"])
        for row in connection.execute(
            """
            SELECT COALESCE(data_quality_status, 'NULL') AS status,
                   COUNT(*) AS records
            FROM resultado_item
            GROUP BY COALESCE(data_quality_status, 'NULL')
            ORDER BY status
            """
        )
    }
    return {
        "resultado_item_by_quality_status": result_status,
        "contracts_with_year_after_2100": _scalar(
            connection, "SELECT COUNT(*) FROM contrato WHERE ano_contrato > 2100"
        ),
        "atas_with_year_after_2100": _scalar(
            connection, "SELECT COUNT(*) FROM ata_registro_preco WHERE ano_ata > 2100"
        ),
        "contracts_above_one_billion_brl": _scalar(
            connection,
            "SELECT COUNT(*) FROM contrato WHERE valor_global_centavos > ?",
            (100_000_000_000,),
        ),
        "negative_financial_values": {
            "contratacao": _scalar(
                connection,
                """SELECT COUNT(*) FROM contratacao
                   WHERE valor_total_estimado_centavos < 0
                      OR valor_total_homologado_centavos < 0""",
            ),
            "resultado_item": _scalar(
                connection,
                """SELECT COUNT(*) FROM resultado_item
                   WHERE valor_unitario_homologado_centavos < 0
                      OR valor_total_homologado_centavos < 0""",
            ),
            "contrato": _scalar(
                connection,
                """SELECT COUNT(*) FROM contrato
                   WHERE valor_inicial_centavos < 0 OR valor_global_centavos < 0
                      OR valor_acumulado_centavos < 0 OR valor_parcela_centavos < 0""",
            ),
            "empenho": _scalar(
                connection,
                "SELECT COUNT(*) FROM empenho WHERE valor_total_centavos < 0",
            ),
            "pca_item": _scalar(
                connection,
                """SELECT COUNT(*) FROM pca_item
                   WHERE valor_unitario_planejado_centavos < 0
                      OR valor_total_planejado_centavos < 0
                      OR valor_orcamento_exercicio_centavos < 0""",
            ),
        },
    }


def _relationship_integrity(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        name: _scalar(connection, query)
        for name, query in RELATIONSHIP_CHECKS.items()
    }


def _lineage_completeness(connection: sqlite3.Connection) -> dict[str, dict[str, int]]:
    result = {}
    for table in LINEAGE_TABLES:
        if not _table_exists(connection, table):
            continue
        row = connection.execute(
            f"""
            SELECT COUNT(*) AS records,
                   SUM(current_source_raw_asset_id IS NULL) AS missing_raw_id,
                   SUM(current_source_payload_hash IS NULL) AS missing_payload_hash
            FROM {table}
            """
        ).fetchone()
        result[table] = {
            "records": int(row["records"] or 0),
            "missing_raw_asset_id": int(row["missing_raw_id"] or 0),
            "missing_payload_hash": int(row["missing_payload_hash"] or 0),
        }
    return result


def _database_checks(connection: sqlite3.Connection) -> dict[str, Any]:
    integrity_rows = [row[0] for row in connection.execute("PRAGMA integrity_check")]
    foreign_key_rows = list(connection.execute("PRAGMA foreign_key_check"))
    return {
        "integrity_check": integrity_rows,
        "foreign_key_violations": len(foreign_key_rows),
    }


def _raw_lineage_audits(normalized_db: Path, raw_db: Path | None) -> dict[str, Any]:
    if raw_db is None or not raw_db.is_file():
        return {
            "status": "NOT_RUN",
            "reason": "RAW_DATABASE_NOT_PROVIDED",
        }
    suspect = audit_suspect_result_dates(normalized_db, raw_db)
    years = audit_anomalous_years(normalized_db, raw_db)
    billion = audit_billion_contracts(normalized_db, raw_db)
    return {
        "status": "COMPLETED",
        "suspect_result_dates": {
            "totals": suspect["totals"],
            "classifications": suspect["classifications"],
            "raw_consistency": suspect["raw_consistency"],
            "conclusion": suspect["conclusion"],
        },
        "anomalous_entity_years": {
            "totals": years["totals"],
            "observed_years": years["observed_years"],
            "raw_consistency": years["raw_consistency"],
            "conclusion": years["conclusion"],
        },
        "billion_contracts": {
            "totals": billion["totals"],
            "raw_consistency": billion["raw_consistency"],
            "interpretation": billion["interpretation"],
            "conclusion": billion["conclusion"],
        },
    }


def generate_quality_coverage_report(
    normalized_db: Path,
    raw_db: Path | None = None,
    *,
    include_raw_audits: bool = True,
) -> dict[str, Any]:
    """Gera o relatório sem alterar o snapshot informado."""

    connection = _connect_readonly(normalized_db)
    try:
        run = _latest_run(connection)
        counts = _table_counts(connection)
        coverage = _coverage_registry(connection, counts)
        report = {
            "schema_version": "pncp_quality_coverage_report_v1",
            "snapshot": {
                "normalized_database": normalized_db.name,
                "normalization_run": run,
                "report_reference_at": run.get("finished_at") if run else None,
            },
            "database_checks": _database_checks(connection),
            "table_counts": counts,
            "coverage_registry": coverage,
            "coverage_summary": {
                "complete_resources": sum(
                    item["coverage_status"] == "COMPLETE" for item in coverage
                ),
                "partial_resources": sum(
                    item["coverage_status"] != "COMPLETE" for item in coverage
                ),
                "known_gaps": sum(int(item["known_gap_count"] or 0) for item in coverage),
                "registry_count_mismatches": sum(
                    not item["record_count_matches_table"] for item in coverage
                ),
            },
            "temporal_coverage": _temporal_coverage(connection),
            "quality_indicators": _quality_indicators(connection),
            "relationship_integrity": _relationship_integrity(connection),
            "lineage_completeness": _lineage_completeness(connection),
            "raw_lineage_audits": (
                _raw_lineage_audits(normalized_db, raw_db)
                if include_raw_audits
                else {"status": "NOT_RUN", "reason": "DISABLED_BY_CALLER"}
            ),
            "limitations": [
                "COMPLETE significa completo em relação ao snapshot, não a todo o PNCP.",
                "Atas e empenhos possuem cobertura parcial.",
                "pca_contratacao_link vazio não autoriza inferir associações.",
                "Anomalias fiéis à RAW são preservadas e não corrigidas silenciosamente.",
            ],
        }
        return report
    finally:
        connection.close()


def render_markdown(report: dict[str, Any]) -> str:
    snapshot = report["snapshot"]
    run = snapshot.get("normalization_run") or {}
    coverage = report["coverage_summary"]
    lines = [
        "# Relatório automático de qualidade e cobertura PNCP/RJ",
        "",
        f"- **Schema do relatório:** `{report['schema_version']}`",
        f"- **Snapshot:** `{run.get('source_snapshot_sha256', 'não informado')}`",
        f"- **Transformação:** `{run.get('transform_version', 'não informada')}`",
        f"- **Referência:** `{snapshot.get('report_reference_at') or 'não informada'}`",
        "- **Execução:** SQLite em modo somente leitura; saída exclusivamente agregada.",
        "",
        "## Resumo",
        "",
        f"- Recursos marcados como completos: **{coverage['complete_resources']}**",
        f"- Recursos parciais: **{coverage['partial_resources']}**",
        f"- Lacunas conhecidas: **{coverage['known_gaps']}**",
        f"- Divergências entre registro de cobertura e tabela: **{coverage['registry_count_mismatches']}**",
        f"- Violações de chave estrangeira: **{report['database_checks']['foreign_key_violations']}**",
        "",
        "## Contagens por tabela",
        "",
        "| Tabela | Registros |",
        "| --- | ---: |",
    ]
    for table, count in report["table_counts"].items():
        lines.append(f"| `{table}` | {count:,} |".replace(",", "."))

    lines.extend(["", "## Cobertura declarada", "", "| Recurso | Estado | Registros | Lacunas | Confere |", "| --- | --- | ---: | ---: | :---: |"]) 
    for item in report["coverage_registry"]:
        lines.append(
            f"| `{item['resource_type']}` | {item['coverage_status']} | "
            f"{int(item['record_count']):,} | {int(item['known_gap_count'] or 0)} | "
            f"{'sim' if item['record_count_matches_table'] else 'não'} |".replace(",", ".")
        )

    quality = report["quality_indicators"]
    suspect = quality["resultado_item_by_quality_status"].get("SUSPECT_DATE", 0)
    lines.extend(
        [
            "",
            "## Indicadores de qualidade",
            "",
            f"- Resultados com data suspeita: **{suspect}**",
            f"- Contratos com ano posterior a 2100: **{quality['contracts_with_year_after_2100']}**",
            f"- Atas com ano posterior a 2100: **{quality['atas_with_year_after_2100']}**",
            f"- Contratos acima de R$ 1 bilhão: **{quality['contracts_above_one_billion_brl']}**",
            f"- Valores financeiros negativos: **{sum(quality['negative_financial_values'].values())}**",
            "",
            "## Integridade dos relacionamentos",
            "",
            "| Verificação | Órfãos/inconsistências |",
            "| --- | ---: |",
        ]
    )
    for check, count in report["relationship_integrity"].items():
        lines.append(f"| `{check}` | {count} |")

    raw = report["raw_lineage_audits"]
    lines.extend(["", "## Auditorias contra a RAW", "", f"Estado: **{raw['status']}**."])
    if raw["status"] == "COMPLETED":
        lines.extend(
            [
                "",
                f"- Datas suspeitas: `{raw['suspect_result_dates']['conclusion']}`",
                f"- Anos anômalos: `{raw['anomalous_entity_years']['conclusion']}`",
                f"- Contratos bilionários: `{raw['billion_contracts']['conclusion']}`",
            ]
        )
    else:
        lines.append(f"Motivo: `{raw.get('reason', 'não informado')}`.")

    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized-db", type=Path, default=DEFAULT_NORMALIZED_DB)
    parser.add_argument("--raw-db", type=Path, default=DEFAULT_RAW_DB)
    parser.add_argument("--without-raw-audits", action="store_true")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    report = generate_quality_coverage_report(
        args.normalized_db,
        args.raw_db,
        include_raw_audits=not args.without_raw_audits,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
                "snapshot": report["snapshot"].get("report_reference_at"),
                "table_counts": report["table_counts"],
                "coverage_summary": report["coverage_summary"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
