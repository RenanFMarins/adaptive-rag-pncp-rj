from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from app.core.database.init_db import initialize_database
from app.core.database.repositories import SyncRepository
from src.ingestion.checkpoint import (
    CoveragePlanSpec,
    CoverageWindowSpec,
    SyncWindowSpec,
)
from src.ingestion.coverage_orchestrator import (
    CONTRACTING_MODALITIES,
    DEFAULT_COVERAGE_NAME,
    ContractingCoverageSchedule,
    ContractingCoveragePlan,
    CoverageMemberAction,
    contracting_job_spec,
    coverage_members,
    execute_contracting_coverage,
    execute_contracting_schedule,
    plan_contracting_coverage,
    plan_contracting_schedule,
)
from src.ingestion.incremental_runner import (
    IncrementalConfigurationError,
    IncrementalRunReport,
)


class CoverageOrchestratorTests(unittest.TestCase):
    DAY = "2026-10-16"

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.database = Path(self.temporary.name) / "coverage.db"
        connection = initialize_database(f"sqlite:///{self.database}")
        connection.close()

    def tearDown(self):
        self.temporary.cleanup()

    def create_coverage(self):
        connection = initialize_database(f"sqlite:///{self.database}")
        sync = SyncRepository(connection)
        spec = CoveragePlanSpec(
            DEFAULT_COVERAGE_NAME,
            "pncp",
            "contratacao",
            "RJ",
            coverage_members(),
        )
        sync.register_coverage_plan(spec)
        window = CoverageWindowSpec(spec.plan_id, self.DAY, self.DAY)
        sync.create_coverage_window(window)
        return connection, sync, window

    def attach_member(self, sync, coverage_window, modality, status):
        job = contracting_job_spec(modality)
        window = SyncWindowSpec(job.job_id, self.DAY, self.DAY)
        sync.register_job(job)
        sync.create_window(window)
        sync.attach_coverage_member(
            coverage_window.window_id,
            f"modalidade:{modality}",
            job.job_id,
            window.window_id,
        )
        sync.connection.execute(
            "UPDATE sync_window SET status=?, attempt_count=1 WHERE id=?",
            (status, window.window_id),
        )
        if status == "COMPLETED":
            sync.connection.execute(
                "UPDATE sync_coverage_member SET status='COMPLETED' "
                "WHERE coverage_window_id=? AND member_key=?",
                (coverage_window.window_id, f"modalidade:{modality}"),
            )
        sync.connection.commit()

    def test_new_coverage_plans_all_modalities_without_writing(self):
        plan = plan_contracting_coverage(self.database, self.DAY)

        self.assertTrue(plan.ready)
        self.assertEqual(plan.pending_count, 14)
        self.assertEqual(
            {item.action for item in plan.members}, {"RUN"}
        )
        connection = initialize_database(f"sqlite:///{self.database}")
        self.assertEqual(
            connection.execute(
                "SELECT COUNT(*) FROM sync_coverage_plan"
            ).fetchone()[0],
            0,
        )
        connection.close()

    def test_planner_skips_completed_resumes_failed_and_blocks_running(self):
        connection, sync, window = self.create_coverage()
        self.attach_member(sync, window, 1, "FAILED")
        self.attach_member(sync, window, 6, "COMPLETED")
        self.attach_member(sync, window, 8, "RUNNING")
        connection.close()

        plan = plan_contracting_coverage(self.database, self.DAY)
        actions = {item.modality: item.action for item in plan.members}

        self.assertFalse(plan.ready)
        self.assertEqual(actions[1], "RESUME")
        self.assertEqual(actions[6], "SKIP")
        self.assertEqual(actions[8], "BLOCK")
        self.assertEqual(actions[14], "RUN")

    def test_overlap_marks_completed_members_for_reprocessing(self):
        connection, sync, window = self.create_coverage()
        self.attach_member(sync, window, 6, "COMPLETED")
        connection.close()

        plan = plan_contracting_coverage(
            self.database, self.DAY, reprocess_completed=True
        )
        modality_six = next(
            item for item in plan.members if item.modality == 6
        )

        self.assertEqual(modality_six.action, "REPROCESS")
        self.assertTrue(plan.ready)

    def test_frozen_manifest_with_other_members_is_rejected(self):
        connection = initialize_database(f"sqlite:///{self.database}")
        sync = SyncRepository(connection)
        sync.register_coverage_plan(
            CoveragePlanSpec(
                DEFAULT_COVERAGE_NAME,
                "pncp",
                "contratacao",
                "RJ",
                ("modalidade:6",),
            )
        )
        connection.close()

        with self.assertRaisesRegex(
            IncrementalConfigurationError, "outros membros"
        ):
            plan_contracting_coverage(self.database, self.DAY)

    def test_unlinked_failed_window_is_resumed_and_completed_is_blocked(self):
        connection = initialize_database(f"sqlite:///{self.database}")
        sync = SyncRepository(connection)
        for modality, status in ((1, "FAILED"), (2, "COMPLETED")):
            job = contracting_job_spec(modality)
            window = SyncWindowSpec(job.job_id, self.DAY, self.DAY)
            sync.register_job(job)
            sync.create_window(window)
            connection.execute(
                "UPDATE sync_window SET status=?, attempt_count=1 WHERE id=?",
                (status, window.window_id),
            )
        connection.commit()
        connection.close()

        plan = plan_contracting_coverage(self.database, self.DAY)
        actions = {item.modality: item.action for item in plan.members}

        self.assertEqual(actions[1], "RESUME")
        self.assertEqual(actions[2], "BLOCK")
        self.assertFalse(plan.ready)

    def test_executor_skips_completed_resumes_failed_and_waits_between_shards(self):
        database = self.database.resolve()
        members = (
            CoverageMemberAction(
                1, "modalidade:1", "RUN", "novo", "job-1", "window-1"
            ),
            CoverageMemberAction(
                6,
                "modalidade:6",
                "SKIP",
                "concluído",
                "job-6",
                "window-6",
            ),
            CoverageMemberAction(
                8,
                "modalidade:8",
                "RESUME",
                "falhou",
                "job-8",
                "window-8",
            ),
            CoverageMemberAction(
                9,
                "modalidade:9",
                "REPROCESS",
                "sobreposição",
                "job-9",
                "window-9",
            ),
        )
        plan = ContractingCoveragePlan(
            str(database),
            DEFAULT_COVERAGE_NAME,
            self.DAY,
            "coverage-window-1",
            True,
            members,
        )
        report = IncrementalRunReport(
            job_id="job",
            window_id="window",
            run_id="run",
            resource="contratacao",
            strategy="endpoint",
            status="SUCCEEDED",
            records_seen=0,
            new=0,
            updated=0,
            unchanged=0,
            lease_renewals=0,
            watermark_value=f"{self.DAY}T23:59:59.999999",
            resumed=False,
            reprocessed=False,
        )
        runner = Mock(return_value=report)
        sleeper = Mock()

        reports = execute_contracting_coverage(
            plan,
            confirmed_database=database,
            log_path=database.with_suffix(".jsonl"),
            runner=runner,
            sleeper=sleeper,
        )

        self.assertEqual(len(reports), 3)
        self.assertEqual(runner.call_count, 3)
        first = runner.call_args_list[0].args[0]
        second = runner.call_args_list[1].args[0]
        third = runner.call_args_list[2].args[0]
        self.assertFalse(first.resume)
        self.assertTrue(second.resume)
        self.assertTrue(third.reprocess)
        self.assertEqual(
            first.coverage_members, coverage_members((1, 6, 8, 9))
        )
        self.assertEqual(sleeper.call_count, 2)

    def test_executor_rejects_short_delay_and_blocked_plan(self):
        plan = ContractingCoveragePlan(
            str(self.database.resolve()),
            DEFAULT_COVERAGE_NAME,
            self.DAY,
            "coverage-window-1",
            False,
            (
                CoverageMemberAction(
                    1,
                    "modalidade:1",
                    "BLOCK",
                    "ativo",
                    "job-1",
                    "window-1",
                ),
            ),
        )
        with self.assertRaisesRegex(
            IncrementalConfigurationError, "pelo menos 30"
        ):
            execute_contracting_coverage(
                plan,
                confirmed_database=self.database,
                log_path=self.database.with_suffix(".jsonl"),
                inter_shard_seconds=29,
            )

    def test_schedule_plans_closed_days_without_writing(self):
        schedule = plan_contracting_schedule(
            self.database,
            "2026-10-16",
            "2026-10-18",
        )

        self.assertTrue(schedule.ready)
        self.assertIsNone(schedule.confirmed_watermark)
        self.assertEqual(
            tuple(window.date for window in schedule.windows),
            ("2026-10-16", "2026-10-17", "2026-10-18"),
        )
        self.assertEqual(schedule.pending_count, 42)
        connection = initialize_database(f"sqlite:///{self.database}")
        self.assertEqual(
            connection.execute(
                "SELECT COUNT(*) FROM sync_coverage_plan"
            ).fetchone()[0],
            0,
        )
        connection.close()

    def test_schedule_reprocesses_overlap_and_runs_new_days(self):
        connection, sync, coverage_window = self.create_coverage()
        for modality in CONTRACTING_MODALITIES:
            self.attach_member(
                sync, coverage_window, modality, "COMPLETED"
            )
        watermark = f"{self.DAY}T23:59:59.999999"
        connection.execute(
            "UPDATE sync_coverage_window SET status='COMPLETED' WHERE id=?",
            (coverage_window.window_id,),
        )
        connection.execute(
            "INSERT INTO sync_coverage_watermark "
            "(plan_id,watermark_value,last_window_id,updated_at) "
            "VALUES (?,?,?,?)",
            (
                coverage_window.plan_id,
                watermark,
                coverage_window.window_id,
                watermark,
            ),
        )
        connection.commit()
        connection.close()

        schedule = plan_contracting_schedule(
            self.database,
            self.DAY,
            "2026-10-18",
        )

        self.assertEqual(schedule.confirmed_watermark, watermark)
        actions = [
            {member.action for member in window.members}
            for window in schedule.windows
        ]
        self.assertEqual(actions[0], {"REPROCESS"})
        self.assertEqual(actions[1:], [{"RUN"}, {"RUN"}])

    def test_schedule_executor_preserves_order_and_inter_window_delay(self):
        database = self.database.resolve()
        windows = tuple(
            ContractingCoveragePlan(
                str(database),
                DEFAULT_COVERAGE_NAME,
                day,
                f"coverage-{day}",
                True,
                (),
            )
            for day in ("2026-10-16", "2026-10-17")
        )
        schedule = ContractingCoverageSchedule(
            str(database),
            DEFAULT_COVERAGE_NAME,
            "2026-10-16",
            "2026-10-17",
            None,
            True,
            windows,
        )
        executor = Mock(side_effect=((), ()))
        sleeper = Mock()

        executions = execute_contracting_schedule(
            schedule,
            confirmed_database=database,
            log_path=database.with_suffix(".jsonl"),
            executor=executor,
            sleeper=sleeper,
        )

        self.assertEqual(
            tuple(execution.date for execution in executions),
            ("2026-10-16", "2026-10-17"),
        )
        self.assertEqual(executor.call_count, 2)
        sleeper.assert_called_once_with(30.0)

    def test_schedule_executor_rejects_blocked_window(self):
        database = self.database.resolve()
        blocked = ContractingCoveragePlan(
            str(database),
            DEFAULT_COVERAGE_NAME,
            self.DAY,
            "coverage-blocked",
            False,
            (
                CoverageMemberAction(
                    1,
                    "modalidade:1",
                    "BLOCK",
                    "execução ativa",
                    "job-1",
                    "window-1",
                ),
            ),
        )
        schedule = ContractingCoverageSchedule(
            str(database),
            DEFAULT_COVERAGE_NAME,
            self.DAY,
            self.DAY,
            None,
            False,
            (blocked,),
        )

        with self.assertRaisesRegex(
            IncrementalConfigurationError, "janela bloqueada"
        ):
            execute_contracting_schedule(
                schedule,
                confirmed_database=database,
                log_path=database.with_suffix(".jsonl"),
            )


if __name__ == "__main__":
    unittest.main()
