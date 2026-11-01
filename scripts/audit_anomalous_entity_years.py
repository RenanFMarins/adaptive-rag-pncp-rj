"""Audita anos muito futuros de contratos e atas em SQLite somente leitura."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_NORMALIZED_DB = Path("data/normalized/pncp_rj_normalized.db")
DEFAULT_RAW_DB = Path("data/debug/pncp_contracts_2023_t1_all.db")
DEFAULT_OUTPUT = Path("/tmp/pncp_anomalous_entity_years_audit.json")


def _uri(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(2, "Banco SQLite não encontrado", str(path))
    return f"{path.resolve().as_uri()}?mode=ro"


def _expected_year(entity: str, identifier: str, signed_at: str | None, published_at: str | None) -> int | None:
    if entity == "ata":
        match = re.search(r"/(\d{4})-", identifier)
        if match:
            return int(match.group(1))
    for value in (signed_at, published_at):
        if value and re.match(r"^20\d{2}", value):
            return int(value[:4])
    return None


def audit_anomalous_years(normalized_db: Path, raw_db: Path) -> dict[str, Any]:
    db = sqlite3.connect(_uri(normalized_db), uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute("ATTACH DATABASE ? AS rawdb", (_uri(raw_db),))
        definitions = (
            ("contrato", "contrato", "numero_controle_pncp", "ano_contrato", "anoContrato"),
            ("ata", "ata_registro_preco", "numero_controle_pncp_ata", "ano_ata", "anoAta"),
        )
        totals: Counter[str] = Counter()
        years: dict[str, Counter[int]] = {}
        expected: dict[str, Counter[int]] = {}
        raw_found = year_exact = hash_exact = version_changes = 0
        version_counts: Counter[int] = Counter()

        for entity, table, id_column, year_column, raw_year_field in definitions:
            rows = db.execute(
                f"""
                SELECT entity.{id_column} AS entity_id,
                       entity.{year_column} AS entity_year,
                       entity.data_assinatura,
                       entity.data_publicacao_pncp,
                       entity.current_source_payload_hash,
                       raw.base_id, raw.external_id, raw.payload_hash,
                       raw.resource_type,
                       json_extract(raw.payload, '$.{raw_year_field}') AS raw_year
                FROM {table} AS entity
                LEFT JOIN rawdb.raw_asset AS raw
                  ON raw.id = entity.current_source_raw_asset_id
                WHERE entity.{year_column} > 2100
                ORDER BY entity.{id_column}
                """
            ).fetchall()
            totals[entity] = len(rows)
            years[entity] = Counter(int(row["entity_year"]) for row in rows)
            expected[entity] = Counter()
            for row in rows:
                if row["external_id"] is not None:
                    raw_found += 1
                if row["entity_year"] == row["raw_year"]:
                    year_exact += 1
                if row["current_source_payload_hash"] == row["payload_hash"]:
                    hash_exact += 1
                inferred = _expected_year(
                    entity,
                    str(row["entity_id"]),
                    row["data_assinatura"],
                    row["data_publicacao_pncp"],
                )
                if inferred is not None:
                    expected[entity][inferred] += 1
                versions = db.execute(
                    """
                    SELECT json_extract(payload, ?) AS raw_year
                    FROM rawdb.raw_asset
                    WHERE base_id = ? AND resource_type = ? AND external_id = ?
                    """,
                    (
                        f"$.{raw_year_field}",
                        row["base_id"],
                        row["resource_type"],
                        row["external_id"],
                    ),
                ).fetchall()
                version_counts[len(versions)] += 1
                if len({version["raw_year"] for version in versions}) > 1:
                    version_changes += 1

        old_contracts = db.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(substr(numero_controle_pncp, -4) = CAST(ano_contrato AS TEXT))
                    AS identifier_matches,
                SUM(substr(data_assinatura, 1, 4) = CAST(ano_contrato AS TEXT))
                    AS signature_matches
            FROM contrato
            WHERE ano_contrato IN (2021, 2022)
            """
        ).fetchone()
        total = sum(totals.values())
        return {
            "schema_version": "anomalous_entity_years_audit_v1",
            "totals": dict(totals),
            "observed_years": {
                entity: {str(year): count for year, count in sorted(values.items())}
                for entity, values in years.items()
            },
            "expected_years_from_identifier_or_dates": {
                entity: {str(year): count for year, count in sorted(values.items())}
                for entity, values in expected.items()
            },
            "raw_consistency": {
                "raw_assets_found": raw_found,
                "year_exact_matches": year_exact,
                "payload_hash_exact_matches": hash_exact,
                "entities_with_year_changes_across_versions": version_changes,
                "versions_per_entity": {
                    str(count): entities for count, entities in sorted(version_counts.items())
                },
                "all_anomalous_years_are_faithful_to_raw": (
                    raw_found == year_exact == hash_exact == total
                ),
            },
            "legacy_contracts_2021_2022": {
                "total": int(old_contracts["total"]),
                "identifier_year_matches": int(old_contracts["identifier_matches"]),
                "signature_year_matches": int(old_contracts["signature_matches"]),
            },
            "impact": {
                "excluded_from_2023_2026_filters": total,
                "contract_rows": totals["contrato"],
                "ata_rows": totals["ata"],
            },
            "conclusion": "SOURCE_DATA_ANOMALY",
        }
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized-db", type=Path, default=DEFAULT_NORMALIZED_DB)
    parser.add_argument("--raw-db", type=Path, default=DEFAULT_RAW_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = audit_anomalous_years(args.normalized_db, args.raw_db)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), **report["totals"], "conclusion": report["conclusion"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
