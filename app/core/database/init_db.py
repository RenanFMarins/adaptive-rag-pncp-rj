from __future__ import annotations

import sqlite3

from .connection import connect_database


SCHEMA = """
CREATE TABLE IF NOT EXISTS ingestion_run (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    window_start TEXT,
    window_end TEXT,
    pages_processed INTEGER NOT NULL DEFAULT 0,
    records_received INTEGER NOT NULL DEFAULT 0,
    records_inserted INTEGER NOT NULL DEFAULT 0,
    records_updated INTEGER NOT NULL DEFAULT 0,
    records_unchanged INTEGER NOT NULL DEFAULT 0,
    records_failed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_checkpoint (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    last_successful_sync TEXT,
    last_page INTEGER NOT NULL DEFAULT 0,
    last_run_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    updated_at TEXT NOT NULL,
    UNIQUE (source, resource_type),
    FOREIGN KEY (last_run_id) REFERENCES ingestion_run(id)
);

CREATE TABLE IF NOT EXISTS raw_asset (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    base_id TEXT NOT NULL,
    natureza TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    external_id TEXT NOT NULL,
    query_params TEXT NOT NULL,
    payload TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    source_published_at TEXT,
    source_updated_at TEXT,
    fetched_at TEXT NOT NULL,
    corpus_version TEXT NOT NULL,
    sensitivity TEXT NOT NULL,
    ingestion_run_id TEXT NOT NULL,
    previous_version_id TEXT,
    processing_status TEXT NOT NULL DEFAULT 'RAW'
        CHECK (processing_status = 'RAW'),
    created_at TEXT NOT NULL,
    FOREIGN KEY (ingestion_run_id) REFERENCES ingestion_run(id),
    FOREIGN KEY (previous_version_id) REFERENCES raw_asset(id)
);

CREATE TABLE IF NOT EXISTS collection_target_failure (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    target_key TEXT NOT NULL,
    cursor INTEGER NOT NULL,
    target_payload TEXT NOT NULL,
    source_url TEXT,
    error_message TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RESOLVED')),
    first_failed_at TEXT NOT NULL,
    last_failed_at TEXT NOT NULL,
    resolved_at TEXT,
    last_run_id TEXT NOT NULL,
    UNIQUE (source, resource_type, target_key),
    FOREIGN KEY (last_run_id) REFERENCES ingestion_run(id)
);

CREATE INDEX IF NOT EXISTS idx_raw_asset_identity
    ON raw_asset(source, resource_type, external_id);
CREATE INDEX IF NOT EXISTS idx_raw_asset_payload_hash
    ON raw_asset(payload_hash);
CREATE INDEX IF NOT EXISTS idx_raw_asset_ingestion_run
    ON raw_asset(ingestion_run_id);
CREATE INDEX IF NOT EXISTS idx_raw_asset_resource_type
    ON raw_asset(resource_type);
CREATE INDEX IF NOT EXISTS idx_raw_asset_corpus_version
    ON raw_asset(corpus_version);
CREATE INDEX IF NOT EXISTS idx_collection_target_failure_pending
    ON collection_target_failure(source, resource_type, status, cursor);
"""


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()


def initialize_database(database_url: str | None = None) -> sqlite3.Connection:
    connection = connect_database(database_url)
    init_db(connection)
    return connection
