from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from scripts.generate_quality_coverage_report import (
    generate_quality_coverage_report,
    render_markdown,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _create_snapshot(path: Path) -> None:
    with sqlite3.connect(path) as db:
        db.executescript(
            """
            CREATE TABLE normalization_run (
                id TEXT, source_snapshot_sha256 TEXT, transform_version TEXT,
                started_at TEXT, finished_at TEXT, status TEXT,
                records_seen INTEGER, records_written INTEGER,
                records_skipped INTEGER, records_rejected INTEGER
            );
            INSERT INTO normalization_run VALUES
                ('run-1', 'snapshot-sha', 'v1', '2026-01-01', '2026-01-02',
                 'SUCCESS', 10, 10, 0, 0);
            CREATE TABLE normalization_coverage (
                resource_type TEXT, coverage_status TEXT, period_start TEXT,
                period_end TEXT, expected_parent_count INTEGER,
                processed_parent_count INTEGER, record_count INTEGER,
                known_gap_count INTEGER, inventory_id TEXT, notes TEXT,
                updated_at TEXT
            );

            CREATE TABLE orgao (cnpj TEXT);
            CREATE TABLE unidade (orgao_cnpj TEXT, codigo_unidade TEXT);
            CREATE TABLE fornecedor (ni_fornecedor TEXT);
            CREATE TABLE contratacao (
                numero_controle_pncp TEXT PRIMARY KEY, ano_compra INTEGER,
                data_publicacao_pncp TEXT,
                valor_total_estimado_centavos INTEGER,
                valor_total_homologado_centavos INTEGER,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE contratacao_item (
                numero_controle_pncp TEXT, numero_item INTEGER,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE resultado_item (
                numero_controle_pncp TEXT, numero_item INTEGER,
                data_resultado TEXT, data_quality_status TEXT,
                valor_unitario_homologado_centavos INTEGER,
                valor_total_homologado_centavos INTEGER,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE contrato (
                numero_controle_pncp TEXT PRIMARY KEY, contratacao_id TEXT,
                ano_contrato INTEGER, data_publicacao_pncp TEXT,
                valor_inicial_centavos INTEGER, valor_global_centavos INTEGER,
                valor_acumulado_centavos INTEGER, valor_parcela_centavos INTEGER,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE empenho (
                numero_controle_contrato TEXT, ano INTEGER, data_emissao TEXT,
                valor_total_centavos INTEGER,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE ata_registro_preco (
                numero_controle_pncp_ata TEXT, contratacao_id TEXT,
                ano_ata INTEGER, data_publicacao_pncp TEXT,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE pca (
                id_pca_pncp TEXT PRIMARY KEY, ano_pca INTEGER,
                data_publicacao_pncp TEXT,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE pca_item (
                id_pca_pncp TEXT, data_desejada TEXT,
                valor_unitario_planejado_centavos INTEGER,
                valor_total_planejado_centavos INTEGER,
                valor_orcamento_exercicio_centavos INTEGER,
                current_source_raw_asset_id TEXT,
                current_source_payload_hash TEXT
            );
            CREATE TABLE pca_contratacao_link (id_pca_pncp TEXT);

            INSERT INTO contratacao VALUES
                ('compra-1', 2026, '2026-01-01', 100, 90, 'raw-c', 'hash-c');
            INSERT INTO contratacao_item VALUES
                ('compra-1', 1, 'raw-i', 'hash-i'),
                ('compra-ausente', 2, 'raw-i2', 'hash-i2');
            INSERT INTO resultado_item VALUES
                ('compra-1', 1, '2027-01-01', 'SUSPECT_DATE', 10, 10,
                 'raw-r', 'hash-r');
            INSERT INTO contrato VALUES
                ('contrato-1', 'compra-1', 2302, '2026-01-02', 10,
                 100000000001, 10, 10, 'raw-ct', 'hash-ct');
            INSERT INTO empenho VALUES
                ('contrato-1', 2026, '2026-01-03', 10, 'raw-e', 'hash-e');
            INSERT INTO ata_registro_preco VALUES
                ('ata-1', NULL, 2424, '2026-01-04', 'raw-a', 'hash-a');
            INSERT INTO pca VALUES
                ('pca-1', 2026, '2026-01-05', 'raw-p', 'hash-p');
            INSERT INTO pca_item VALUES
                ('pca-1', '2026-06-01', 10, 10, 10, 'raw-pi', 'hash-pi');

            INSERT INTO normalization_coverage VALUES
                ('contratacao', 'COMPLETE', NULL, NULL, NULL, NULL, 1, 0,
                 NULL, 'snapshot', '2026-01-02'),
                ('empenho', 'PARTIAL', NULL, NULL, NULL, NULL, 1, 4,
                 NULL, 'parcial', '2026-01-02');
            """
        )


def test_report_is_aggregated_reproducible_and_read_only(tmp_path: Path) -> None:
    database = tmp_path / "snapshot.db"
    _create_snapshot(database)
    before = _sha256(database)

    report = generate_quality_coverage_report(
        database, raw_db=None, include_raw_audits=False
    )

    assert _sha256(database) == before
    assert report["snapshot"]["report_reference_at"] == "2026-01-02"
    assert report["table_counts"]["contratacao_item"] == 2
    assert report["coverage_summary"] == {
        "complete_resources": 1,
        "partial_resources": 1,
        "known_gaps": 4,
        "registry_count_mismatches": 0,
    }
    assert report["quality_indicators"]["contracts_with_year_after_2100"] == 1
    assert report["quality_indicators"]["atas_with_year_after_2100"] == 1
    assert report["quality_indicators"]["contracts_above_one_billion_brl"] == 1
    assert report["relationship_integrity"]["contratacao_item_without_contratacao"] == 1
    assert report["raw_lineage_audits"] == {
        "status": "NOT_RUN",
        "reason": "DISABLED_BY_CALLER",
    }


def test_markdown_exposes_aggregates_not_record_payloads(tmp_path: Path) -> None:
    database = tmp_path / "snapshot.db"
    _create_snapshot(database)
    report = generate_quality_coverage_report(
        database, raw_db=None, include_raw_audits=False
    )

    markdown = render_markdown(report)

    assert "snapshot-sha" in markdown
    assert "Resultados com data suspeita: **1**" in markdown
    assert "compra-1" not in markdown
    assert "raw-c" not in markdown
