from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

from scripts.audit_suspect_result_dates import audit_suspect_result_dates


def _create_fixture(normalized: Path, raw: Path) -> None:
    with sqlite3.connect(normalized) as db:
        db.executescript(
            """
            CREATE TABLE normalization_run (
                id TEXT, source_snapshot_sha256 TEXT, transform_version TEXT,
                finished_at TEXT, status TEXT
            );
            CREATE TABLE orgao (cnpj TEXT PRIMARY KEY, razao_social TEXT);
            CREATE TABLE contratacao (
                numero_controle_pncp TEXT PRIMARY KEY,
                data_publicacao_pncp TEXT
            );
            CREATE TABLE resultado_item (
                numero_controle_pncp TEXT, numero_item INTEGER,
                sequencial_resultado INTEGER, data_resultado TEXT,
                data_quality_status TEXT, current_source_payload_hash TEXT,
                current_source_raw_asset_id TEXT, normalized_at TEXT
            );
            INSERT INTO normalization_run VALUES
                ('run-1', 'snapshot', 'v1', '2026-10-20', 'SUCCESS');
            INSERT INTO orgao VALUES ('11111111000191', 'ORGAO TESTE');
            """
        )
        cases = [
            ("a", "2013-09-13", "2025-02-01"),
            ("b", "2027-04-30", "2026-05-01"),
            ("c", "2202-12-29", "2026-05-01"),
        ]
        for sequence, result_date, publication in cases:
            control = f"11111111000191-1-00000{len(sequence)}/2026-{sequence}"
            db.execute("INSERT INTO contratacao VALUES (?, ?)", (control, publication))
            db.execute(
                "INSERT INTO resultado_item VALUES (?, 1, 1, ?, 'SUSPECT_DATE', ?, ?, '2026-10-20')",
                (control, result_date, f"hash-{sequence}", f"raw-{sequence}"),
            )

    with sqlite3.connect(raw) as db:
        db.execute(
            """
            CREATE TABLE raw_asset (
                id TEXT PRIMARY KEY, base_id TEXT, resource_type TEXT,
                external_id TEXT, payload_hash TEXT, previous_version_id TEXT,
                source TEXT, payload TEXT
            )
            """
        )
        db.execute(
            "CREATE INDEX idx_fixture_identity ON raw_asset(base_id, resource_type, external_id)"
        )
        rows = sqlite3.connect(normalized).execute(
            "SELECT numero_controle_pncp, data_resultado, current_source_payload_hash, current_source_raw_asset_id FROM resultado_item"
        ).fetchall()
        for control, result_date, payload_hash, raw_id in rows:
            payload = {
                "numeroControlePNCPCompra": control,
                "numeroItem": 1,
                "sequencialResultado": 1,
                "dataResultado": result_date,
            }
            db.execute(
                "INSERT INTO raw_asset VALUES (?, 'pncp', 'resultado_item', ?, ?, NULL, 'source', ?)",
                (raw_id, f"{control}|1|1", payload_hash, json.dumps(payload)),
            )


def test_audit_classifies_and_confirms_raw_lineage(tmp_path: Path) -> None:
    normalized = tmp_path / "normalized.db"
    raw = tmp_path / "raw.db"
    _create_fixture(normalized, raw)

    report = audit_suspect_result_dates(
        normalized,
        raw,
        reference_date=date(2026, 10, 20),
    )

    assert report["classifications"] == {
        "AFTER_REFERENCE_DATE": 1,
        "BEFORE_PUBLICATION": 1,
        "OUTLIER_YEAR_GT_10Y": 1,
    }
    assert report["raw_consistency"] == {
        "raw_assets_found": 3,
        "date_exact_matches": 3,
        "payload_hash_exact_matches": 3,
        "identity_exact_matches": 3,
        "entities_with_date_changes_across_versions": 0,
        "versions_per_entity": {"1": 3},
        "all_current_values_are_faithful_to_raw": True,
    }
    assert report["conclusion"] == "SOURCE_DATA_ANOMALY"


def test_audit_requires_existing_files(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    try:
        audit_suspect_result_dates(missing, missing)
    except FileNotFoundError as error:
        assert error.filename == str(missing)
    else:
        raise AssertionError("FileNotFoundError esperado")
