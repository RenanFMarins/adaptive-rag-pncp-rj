from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fetch_incremental import safe_sqlite_database_path  # noqa: E402
from src.ingestion.coverage_orchestrator import (  # noqa: E402
    DEFAULT_COVERAGE_NAME,
    MINIMUM_SHARD_DELAY_SECONDS,
    execute_contracting_schedule,
    plan_contracting_schedule,
)
from src.ingestion.incremental_runner import (  # noqa: E402
    IncrementalConfigurationError,
)


OPERATIONAL_TIMEZONE = "America/Sao_Paulo"


def last_closed_date(now: datetime | None = None) -> str:
    zone = ZoneInfo(OPERATIONAL_TIMEZONE)
    current = now or datetime.now(zone)
    if current.tzinfo is None:
        current = current.replace(tzinfo=zone)
    else:
        current = current.astimezone(zone)
    return (current.date() - timedelta(days=1)).isoformat()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Planeja e executa janelas fechadas da cobertura incremental "
            "de contratações do PNCP/RJ"
        )
    )
    parser.add_argument("--initial-start", required=True)
    parser.add_argument(
        "--through",
        default=None,
        help=(
            "Último dia fechado; por padrão usa ontem em "
            f"{OPERATIONAL_TIMEZONE}"
        ),
    )
    parser.add_argument(
        "--db-path", required=True, type=safe_sqlite_database_path
    )
    parser.add_argument(
        "--coverage-name", default=DEFAULT_COVERAGE_NAME
    )
    parser.add_argument(
        "--inter-shard-seconds",
        type=int,
        default=MINIMUM_SHARD_DELAY_SECONDS,
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--confirm-operational-database",
        type=safe_sqlite_database_path,
        default=None,
    )
    parser.add_argument("--log-path", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    through = args.through or last_closed_date()
    try:
        schedule = plan_contracting_schedule(
            args.db_path,
            args.initial_start,
            through,
            coverage_name=args.coverage_name,
        )
        output = {"schedule": asdict(schedule), "executions": []}
        if args.execute:
            if args.confirm_operational_database is None:
                raise IncrementalConfigurationError(
                    "--execute requer --confirm-operational-database"
                )
            if args.log_path is None:
                raise IncrementalConfigurationError(
                    "--execute requer --log-path"
                )
            executions = execute_contracting_schedule(
                schedule,
                confirmed_database=args.confirm_operational_database,
                log_path=args.log_path,
                inter_shard_seconds=args.inter_shard_seconds,
            )
            output["executions"] = [asdict(item) for item in executions]
    except (IncrementalConfigurationError, ValueError, RuntimeError) as error:
        print(
            json.dumps(
                {"status": "FAILED", "error": str(error)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
