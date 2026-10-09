from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from app.core.database.repositories import SyncRepository
from src.fetch_incremental import build_parser, main
from src.ingest import RawRepository, ingest_records
from src.ingestion.incremental_runner import (
    IncrementalRunConfig,
    run_offline_incremental,
)
from src.schema import CollectedRecord


class SilentLogger:
    def event(self, event, **fields):
        pass


class IncrementalRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.database = self.root / "incremental.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_fixture(self, document, name="fixture.json"):
        path = self.root / name
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    @staticmethod
    def record(external_id="compra-1", state="A", timestamp=None):
        return {
            "external_id": external_id,
            "payload": {
                "numeroControlePNCP": external_id,
                "estado": state,
                "dataAtualizacaoGlobal": timestamp
                or "2023-04-10T10:00:00Z",
            },
        }

    def endpoint_fixture(
        self, records=None, name="fixture.json", **extra
    ):
        return self.write_fixture(
            {
                "strategy": "endpoint",
                "pages": [{"cursor": "1", "records": records or []}],
                **extra,
            },
            name,
        )

    def config(self, fixture, **changes):
        values = {
            "resource": "contratacao",
            "start_date": "2023-04-01",
            "end_date": "2023-04-30",
            "uf": "RJ",
            "database_url": f"sqlite:///{self.database}",
            "fixture_path": fixture,
            "worker_id": "test-worker",
        }
        values.update(changes)
        return IncrementalRunConfig(**values)

    def test_cli_incremental_offline_executes_and_reports_job(self):
        fixture = self.endpoint_fixture([self.record()])
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            status = main(
                [
                    "--resource",
                    "contratacao",
                    "--start-date",
                    "2023-04-01",
                    "--end-date",
                    "2023-04-30",
                    "--uf",
                    "RJ",
                    "--db-path",
                    str(self.database),
                    "--fixture",
                    str(fixture),
                    "--offline",
                ]
            )

        report = json.loads(stdout.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(report["status"], "SUCCEEDED")
        self.assertEqual((report["new"], report["records_seen"]), (1, 1))
        self.assertTrue(report["job_id"].startswith("job-"))

    def test_cli_rejects_online_execution(self):
        fixture = self.endpoint_fixture([])
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            status = main(
                [
                    "--resource",
                    "contratacao",
                    "--start-date",
                    "2023-04-01",
                    "--end-date",
                    "2023-04-30",
                    "--uf",
                    "RJ",
                    "--db-path",
                    str(self.database),
                    "--fixture",
                    str(fixture),
                ]
            )

        self.assertEqual(status, 2)
        self.assertIn("online ainda não foi habilitada", stderr.getvalue())
        self.assertFalse(self.database.exists())

    def test_cli_rejects_operational_database_path(self):
        fixture = self.endpoint_fixture([])
        parser = build_parser()
        operational = Path(__file__).parents[2] / "data" / "operational.db"
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "--resource",
                    "contratacao",
                    "--start-date",
                    "2023-04-01",
                    "--end-date",
                    "2023-04-30",
                    "--uf",
                    "RJ",
                    "--db-path",
                    str(operational),
                    "--fixture",
                    str(fixture),
                    "--offline",
                ]
            )

    def test_configuration_changes_produce_independent_jobs(self):
        fixture = self.endpoint_fixture([])
        first = run_offline_incremental(
            self.config(fixture, modality=6)
        )
        second = run_offline_incremental(
            self.config(fixture, modality=8)
        )

        self.assertNotEqual(first.job_id, second.job_id)
        connection = sqlite3.connect(self.database)
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM sync_job").fetchone()[0],
            2,
        )
        connection.close()

    def test_same_job_has_independent_windows(self):
        fixture = self.endpoint_fixture([])
        april = run_offline_incremental(self.config(fixture))
        may = run_offline_incremental(
            self.config(
                fixture,
                start_date="2023-05-01",
                end_date="2023-05-31",
            )
        )

        self.assertEqual(april.job_id, may.job_id)
        self.assertNotEqual(april.window_id, may.window_id)

    def test_lease_is_renewed_during_operation_longer_than_initial_lease(self):
        fixture = self.write_fixture(
            {
                "strategy": "endpoint",
                "delay_seconds": 0.025,
                "pages": [
                    {"cursor": str(index), "records": [self.record(str(index))]}
                    for index in range(1, 4)
                ],
            }
        )

        report = run_offline_incremental(
            self.config(
                fixture,
                lease_seconds=0.08,
                lease_renewal_seconds=0.02,
            )
        )

        self.assertGreater(report.lease_renewals, 0)
        self.assertEqual(report.status, "SUCCEEDED")

    def test_lost_lease_stops_old_worker_without_watermark(self):
        fixture = self.write_fixture(
            {
                "strategy": "endpoint",
                "delay_seconds": 0.07,
                "pages": [{"cursor": "1", "records": [self.record()]}],
            }
        )

        with self.assertRaisesRegex(Exception, "Lease"):
            run_offline_incremental(
                self.config(
                    fixture,
                    lease_seconds=0.04,
                    lease_renewal_seconds=0.01,
                )
            )

        connection = sqlite3.connect(self.database)
        window = connection.execute(
            "SELECT status, lease_expires_at FROM sync_window"
        ).fetchone()
        watermark_count = connection.execute(
            "SELECT COUNT(*) FROM sync_watermark"
        ).fetchone()[0]
        connection.close()
        self.assertEqual(window[0], "RUNNING")
        self.assertIsNotNone(window[1])
        self.assertEqual(watermark_count, 0)

    def test_failure_after_raw_persistence_does_not_confirm_page(self):
        fixture = self.endpoint_fixture(
            [self.record()], fail_after_records=1
        )

        with self.assertRaisesRegex(RuntimeError, "persistência RAW"):
            run_offline_incremental(self.config(fixture))

        connection = sqlite3.connect(self.database)
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM raw_asset").fetchone()[0],
            1,
        )
        window = connection.execute(
            "SELECT status, progress_cursor FROM sync_window"
        ).fetchone()
        self.assertEqual(window, ("FAILED", None))
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM sync_watermark").fetchone()[0],
            0,
        )
        connection.close()

    def test_failure_and_resume_are_idempotent(self):
        failing = self.endpoint_fixture(
            [self.record()], fail_after_records=1
        )
        with self.assertRaises(RuntimeError):
            run_offline_incremental(self.config(failing))
        recovered = self.endpoint_fixture([self.record()], name="recovered.json")

        report = run_offline_incremental(
            self.config(recovered, resume=True, worker_id="recovery-worker")
        )

        self.assertEqual((report.new, report.unchanged), (0, 1))
        connection = sqlite3.connect(self.database)
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM raw_asset").fetchone()[0],
            1,
        )
        self.assertEqual(
            connection.execute("SELECT status FROM sync_window").fetchone()[0],
            "COMPLETED",
        )
        connection.close()

    def test_existing_entity_is_updated_in_later_window(self):
        first = self.endpoint_fixture([self.record(state="A")], name="a.json")
        second = self.endpoint_fixture(
            [
                self.record(
                    state="B", timestamp="2023-05-10T10:00:00Z"
                )
            ],
            name="b.json",
        )
        initial = run_offline_incremental(self.config(first))
        changed = run_offline_incremental(
            self.config(
                second,
                start_date="2023-05-01",
                end_date="2023-05-31",
            )
        )

        self.assertEqual((initial.new, changed.updated), (1, 1))
        connection = sqlite3.connect(self.database)
        chain = connection.execute(
            "SELECT id, previous_version_id FROM raw_asset ORDER BY rowid"
        ).fetchall()
        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[1][1], chain[0][0])
        connection.close()

    def test_relationship_resource_confirms_stable_target(self):
        fixture = self.write_fixture(
            {
                "strategy": "relationship",
                "targets": [
                    {
                        "target": {"numero_controle": "compra-1"},
                        "pages": [
                            {
                                "cursor": "page-1",
                                "records": [
                                    {
                                        "external_id": "compra-1|1",
                                        "payload": {
                                            "numeroItem": 1,
                                            "descricao": "item",
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        )

        report = run_offline_incremental(
            self.config(fixture, resource="contratacao_item")
        )

        self.assertEqual((report.strategy, report.new), ("relationship", 1))
        connection = sqlite3.connect(self.database)
        target = connection.execute(
            "SELECT target_key, status, processed_fingerprint "
            "FROM sync_target_progress"
        ).fetchone()
        self.assertEqual(target[0:2], ("compra-1", "COMPLETED"))
        self.assertIsNotNone(target[2])
        connection.close()

    def test_new_relationship_target_before_completed_one_is_processed(self):
        original = self.write_fixture(
            {
                "strategy": "relationship",
                "targets": [
                    {
                        "target": {"numero_controle": "B"},
                        "pages": [{"records": []}],
                    }
                ],
            },
            "targets-1.json",
        )
        first = run_offline_incremental(
            self.config(original, resource="contratacao_item")
        )
        expanded = self.write_fixture(
            {
                "strategy": "relationship",
                "targets": [
                    {
                        "target": {"numero_controle": "A"},
                        "pages": [{"records": []}],
                    },
                    {
                        "target": {"numero_controle": "B"},
                        "pages": [{"records": []}],
                    },
                ],
            },
            "targets-2.json",
        )

        replay = run_offline_incremental(
            self.config(
                expanded,
                resource="contratacao_item",
                reprocess=True,
            )
        )

        self.assertTrue(replay.reprocessed)
        connection = sqlite3.connect(self.database)
        keys = {
            row[0]
            for row in connection.execute(
                "SELECT target_key FROM sync_target_progress"
            )
        }
        connection.close()
        self.assertEqual(keys, {"A", "B"})
        self.assertEqual(first.status, "SUCCEEDED")

    def test_historical_fetch_entrypoint_remains_legacy(self):
        import inspect
        from src import fetch_corpus

        signature = inspect.signature(fetch_corpus.run)
        source = inspect.getsource(fetch_corpus.run)

        self.assertEqual(
            list(signature.parameters),
            ["manifest_path", "source_id", "mode", "database_url"],
        )
        self.assertIn("repository.get_checkpoint", source)
        self.assertNotIn("run_offline_incremental", source)

    def test_incremental_run_does_not_change_legacy_checkpoint(self):
        repository = RawRepository(f"sqlite:///{self.database}")
        ingest_records(
            repository,
            "legacy",
            ("numeroControlePNCP",),
            [
                CollectedRecord(
                    "legacy",
                    {
                        "numeroControlePNCP": "legacy-1",
                        "dataAtualizacaoGlobal": "2023-01-01T00:00:00Z",
                    },
                    "offline://legacy",
                    "7",
                    1,
                    external_id="legacy-1",
                )
            ],
            logger=SilentLogger(),
            resource_type="contratacao",
        )
        before = tuple(
            repository.connection.execute(
                "SELECT * FROM sync_checkpoint"
            ).fetchone()
        )
        repository.close()
        fixture = self.endpoint_fixture([self.record()])

        run_offline_incremental(self.config(fixture))

        connection = sqlite3.connect(self.database)
        after = tuple(connection.execute("SELECT * FROM sync_checkpoint").fetchone())
        connection.close()
        self.assertEqual(after, before)

    def test_offline_runner_does_not_call_network(self):
        fixture = self.endpoint_fixture([self.record()])
        with patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("network called"),
        ) as network:
            report = run_offline_incremental(self.config(fixture))

        network.assert_not_called()
        self.assertEqual(report.status, "SUCCEEDED")

    def test_multiple_pages_are_processed_and_checkpointed(self):
        fixture = self.write_fixture(
            {
                "strategy": "endpoint",
                "pages": [
                    {"cursor": "page-a", "records": [self.record("A")]},
                    {"cursor": "page-b", "records": [self.record("B")]},
                ],
            }
        )

        report = run_offline_incremental(self.config(fixture))

        self.assertEqual((report.records_seen, report.new), (2, 2))
        connection = sqlite3.connect(self.database)
        self.assertEqual(
            connection.execute(
                "SELECT progress_cursor FROM sync_window"
            ).fetchone()[0],
            "page-b",
        )
        connection.close()

    def test_explicit_reprocessing_is_idempotent(self):
        fixture = self.endpoint_fixture([self.record()])
        first = run_offline_incremental(self.config(fixture))
        replay = run_offline_incremental(
            self.config(fixture, reprocess=True, worker_id="reprocess-worker")
        )

        self.assertEqual((first.new, replay.unchanged), (1, 1))
        connection = sqlite3.connect(self.database)
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM raw_asset").fetchone()[0],
            1,
        )
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM ingestion_run").fetchone()[0],
            2,
        )
        connection.close()


if __name__ == "__main__":
    unittest.main()
