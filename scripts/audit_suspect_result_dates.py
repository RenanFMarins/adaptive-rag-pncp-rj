"""Audita datas suspeitas de resultados sem modificar RAW ou normalizada.

A saída é agregada: não copia payloads, fornecedores ou valores financeiros.
Ambos os SQLite são abertos explicitamente com ``mode=ro``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_NORMALIZED_DB = Path("data/normalized/pncp_rj_normalized.db")
DEFAULT_RAW_DB = Path("data/debug/pncp_contracts_2023_t1_all.db")
DEFAULT_OUTPUT = Path("/tmp/pncp_suspect_result_dates_audit.json")


def _readonly_uri(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(2, "Banco SQLite não encontrado", str(path))
    return f"{path.resolve().as_uri()}?mode=ro"


def _classify_date(
    result_value: str,
    publication_value: str | None,
    reference_date: date,
) -> str:
    result_date = date.fromisoformat(result_value[:10])
    if result_date.year > reference_date.year + 10:
        return "OUTLIER_YEAR_GT_10Y"
    if result_date > reference_date:
        return "AFTER_REFERENCE_DATE"
    if publication_value and result_date < date.fromisoformat(publication_value[:10]):
        return "BEFORE_PUBLICATION"
    return "FLAGGED_OTHER"


def audit_suspect_result_dates(
    normalized_db: Path,
    raw_db: Path,
    *,
    reference_date: date | None = None,
) -> dict[str, Any]:
    connection = sqlite3.connect(_readonly_uri(normalized_db), uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("ATTACH DATABASE ? AS rawdb", (_readonly_uri(raw_db),))
        if reference_date is None:
            normalized_at = connection.execute(
                """
                SELECT MAX(normalized_at)
                FROM resultado_item
                WHERE data_quality_status = 'SUSPECT_DATE'
                """
            ).fetchone()[0]
            if not normalized_at:
                raise ValueError("Nenhum resultado SUSPECT_DATE foi encontrado")
            reference_date = date.fromisoformat(str(normalized_at)[:10])

        rows = connection.execute(
            """
            SELECT
                result.numero_controle_pncp,
                result.numero_item,
                result.sequencial_resultado,
                result.data_resultado,
                result.current_source_payload_hash,
                result.current_source_raw_asset_id,
                procurement.data_publicacao_pncp,
                organization.razao_social,
                substr(result.numero_controle_pncp, 1, 14) AS cnpj_orgao,
                raw.base_id,
                raw.external_id,
                raw.resource_type,
                raw.payload_hash,
                raw.previous_version_id,
                raw.source,
                json_extract(raw.payload, '$.dataResultado') AS raw_date,
                json_extract(raw.payload, '$.numeroControlePNCPCompra') AS raw_control,
                json_extract(raw.payload, '$.numeroItem') AS raw_item,
                json_extract(raw.payload, '$.sequencialResultado') AS raw_sequence
            FROM resultado_item AS result
            JOIN contratacao AS procurement
              ON procurement.numero_controle_pncp = result.numero_controle_pncp
            LEFT JOIN orgao AS organization
              ON organization.cnpj = substr(result.numero_controle_pncp, 1, 14)
            LEFT JOIN rawdb.raw_asset AS raw
              ON raw.id = result.current_source_raw_asset_id
            WHERE result.data_quality_status = 'SUSPECT_DATE'
            ORDER BY
                result.numero_controle_pncp,
                result.numero_item,
                result.sequencial_resultado
            """
        ).fetchall()
        if not rows:
            raise ValueError("Nenhum resultado SUSPECT_DATE foi encontrado")

        classifications: Counter[str] = Counter()
        dates: Counter[str] = Counter()
        sources: Counter[str] = Counter()
        organizations: Counter[tuple[str, str]] = Counter()
        procurements: set[str] = set()
        raw_found = date_exact = hash_exact = identity_exact = 0
        version_counts: Counter[int] = Counter()
        entities_with_date_changes = 0

        for row in rows:
            classification = _classify_date(
                str(row["data_resultado"]),
                row["data_publicacao_pncp"],
                reference_date,
            )
            classifications[classification] += 1
            dates[str(row["data_resultado"])] += 1
            sources[str(row["source"] or "MISSING_RAW")] += 1
            organizations[(
                str(row["cnpj_orgao"]),
                str(row["razao_social"] or "NAO_INFORMADO"),
            )] += 1
            procurements.add(str(row["numero_controle_pncp"]))

            if row["external_id"] is not None:
                raw_found += 1
            if row["data_resultado"] == row["raw_date"]:
                date_exact += 1
            if row["current_source_payload_hash"] == row["payload_hash"]:
                hash_exact += 1
            if (
                row["numero_controle_pncp"] == row["raw_control"]
                and row["numero_item"] == row["raw_item"]
                and row["sequencial_resultado"] == row["raw_sequence"]
            ):
                identity_exact += 1

            versions = connection.execute(
                """
                SELECT json_extract(payload, '$.dataResultado') AS raw_date
                FROM rawdb.raw_asset
                WHERE base_id = ?
                  AND resource_type = 'resultado_item'
                  AND external_id = ?
                """,
                (row["base_id"], row["external_id"]),
            ).fetchall()
            version_counts[len(versions)] += 1
            if len({version["raw_date"] for version in versions}) > 1:
                entities_with_date_changes += 1

        run = connection.execute(
            """
            SELECT id, source_snapshot_sha256, transform_version, finished_at
            FROM normalization_run
            WHERE status = 'SUCCESS'
            ORDER BY finished_at DESC
            LIMIT 1
            """
        ).fetchone()
        total = len(rows)
        return {
            "schema_version": "suspect_result_dates_audit_v1",
            "reference_date": reference_date.isoformat(),
            "normalization_run": dict(run) if run else None,
            "totals": {
                "suspect_results": total,
                "procurements": len(procurements),
                "organizations": len(organizations),
            },
            "classifications": dict(sorted(classifications.items())),
            "raw_consistency": {
                "raw_assets_found": raw_found,
                "date_exact_matches": date_exact,
                "payload_hash_exact_matches": hash_exact,
                "identity_exact_matches": identity_exact,
                "entities_with_date_changes_across_versions": entities_with_date_changes,
                "versions_per_entity": {
                    str(count): entities
                    for count, entities in sorted(version_counts.items())
                },
                "all_current_values_are_faithful_to_raw": (
                    raw_found == date_exact == hash_exact == identity_exact == total
                ),
            },
            "sources": dict(sorted(sources.items())),
            "date_frequencies": dict(sorted(dates.items())),
            "organizations": [
                {"cnpj": cnpj, "name": name, "suspect_results": count}
                for (cnpj, name), count in sorted(
                    organizations.items(), key=lambda item: (-item[1], item[0])
                )
            ],
            "conclusion": (
                "SOURCE_DATA_ANOMALY"
                if raw_found == date_exact == hash_exact == identity_exact == total
                else "LINEAGE_OR_TRANSFORMATION_MISMATCH"
            ),
        }
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized-db", type=Path, default=DEFAULT_NORMALIZED_DB)
    parser.add_argument("--raw-db", type=Path, default=DEFAULT_RAW_DB)
    parser.add_argument("--reference-date", type=date.fromisoformat)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = audit_suspect_result_dates(
        args.normalized_db,
        args.raw_db,
        reference_date=args.reference_date,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output),
        "totals": report["totals"],
        "classifications": report["classifications"],
        "conclusion": report["conclusion"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
