"""Audita contratos acima de R$ 1 bilhão sem modificar os bancos."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

LIMIT_CENTS = 100_000_000_000
DEFAULT_NORMALIZED_DB = Path("data/normalized/pncp_rj_normalized.db")
DEFAULT_RAW_DB = Path("data/debug/pncp_contracts_2023_t1_all.db")
DEFAULT_OUTPUT = Path("/tmp/pncp_billion_contracts_audit.json")


def _uri(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(2, "Banco SQLite não encontrado", str(path))
    return f"{path.resolve().as_uri()}?mode=ro"


def _classify(
    global_cents: int,
    initial_cents: int | None,
    parent_estimated_cents: int | None,
    parent_awarded_cents: int | None,
) -> str:
    if initial_cents and global_cents >= initial_cents * 10:
        return "GLOBAL_GT_10X_INITIAL"
    parent_reference = max(parent_estimated_cents or 0, parent_awarded_cents or 0)
    if parent_reference and global_cents >= parent_reference * 10:
        return "GLOBAL_GT_10X_PARENT"
    return "INTERNALLY_CONSISTENT"


def audit_billion_contracts(normalized_db: Path, raw_db: Path) -> dict[str, Any]:
    db = sqlite3.connect(_uri(normalized_db), uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute("ATTACH DATABASE ? AS rawdb", (_uri(raw_db),))
        rows = db.execute(
            """
            SELECT contract.numero_controle_pncp,
                   contract.valor_global_centavos,
                   contract.valor_inicial_centavos,
                   contract.current_source_payload_hash,
                   procurement.valor_total_estimado_centavos,
                   procurement.valor_total_homologado_centavos,
                   raw.base_id, raw.resource_type, raw.external_id,
                   raw.payload_hash, raw.source,
                   json_extract(raw.payload, '$.valorGlobal') AS raw_global,
                   json_extract(raw.payload, '$.valorInicial') AS raw_initial,
                   json_extract(raw.payload, '$.moeda') AS raw_currency
            FROM contrato AS contract
            LEFT JOIN contratacao AS procurement
              ON procurement.numero_controle_pncp = contract.contratacao_id
            LEFT JOIN rawdb.raw_asset AS raw
              ON raw.id = contract.current_source_raw_asset_id
            WHERE contract.valor_global_centavos > ?
            ORDER BY contract.valor_global_centavos DESC
            """,
            (LIMIT_CENTS,),
        ).fetchall()
        classes: Counter[str] = Counter()
        sources: Counter[str] = Counter()
        raw_found = hash_exact = global_exact = initial_exact = 0
        versions: Counter[int] = Counter()
        year_changes = 0
        for row in rows:
            classes[_classify(
                int(row["valor_global_centavos"]),
                row["valor_inicial_centavos"],
                row["valor_total_estimado_centavos"],
                row["valor_total_homologado_centavos"],
            )] += 1
            sources[str(row["source"] or "MISSING_RAW")] += 1
            if row["external_id"] is not None:
                raw_found += 1
            if row["current_source_payload_hash"] == row["payload_hash"]:
                hash_exact += 1
            if row["raw_global"] is not None and round(float(row["raw_global"]) * 100) == row["valor_global_centavos"]:
                global_exact += 1
            if row["raw_initial"] is not None and round(float(row["raw_initial"]) * 100) == row["valor_inicial_centavos"]:
                initial_exact += 1
            observations = db.execute(
                """
                SELECT json_extract(payload, '$.valorGlobal') AS raw_global
                FROM rawdb.raw_asset
                WHERE base_id = ? AND resource_type = ? AND external_id = ?
                """,
                (row["base_id"], row["resource_type"], row["external_id"]),
            ).fetchall()
            versions[len(observations)] += 1
            if len({item["raw_global"] for item in observations}) > 1:
                year_changes += 1
        total = len(rows)
        return {
            "schema_version": "billion_contracts_audit_v1",
            "threshold_brl": "1000000000.00",
            "totals": {"contracts": total, "classifications": dict(sorted(classes.items()))},
            "raw_consistency": {
                "raw_assets_found": raw_found,
                "payload_hash_exact_matches": hash_exact,
                "global_value_cent_conversion_exact": global_exact,
                "initial_value_cent_conversion_exact": initial_exact,
                "entities_with_global_value_changes_across_versions": year_changes,
                "versions_per_entity": {str(k): v for k, v in sorted(versions.items())},
                "currency_field_absent": sum(row["raw_currency"] is None for row in rows),
                "all_values_are_faithful_to_raw": (
                    raw_found == hash_exact == global_exact == initial_exact == total
                ),
            },
            "sources": dict(sorted(sources.items())),
            "interpretation": {
                "requires_source_review": classes["GLOBAL_GT_10X_INITIAL"] + classes["GLOBAL_GT_10X_PARENT"],
                "internally_consistent_not_externally_confirmed": classes["INTERNALLY_CONSISTENT"],
            },
            "conclusion": "SOURCE_VALUES_PRESERVED_WITH_QUALITY_WARNINGS",
        }
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized-db", type=Path, default=DEFAULT_NORMALIZED_DB)
    parser.add_argument("--raw-db", type=Path, default=DEFAULT_RAW_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = audit_billion_contracts(args.normalized_db, args.raw_db)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), **report["totals"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
