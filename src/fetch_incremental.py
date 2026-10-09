from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ingestion.incremental_runner import (  # noqa: E402
    INCREMENTAL_RESOURCES,
    IncrementalConfigurationError,
    IncrementalRunConfig,
    OfflineFixtureError,
    run_offline_incremental,
)


def safe_offline_database_path(value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise argparse.ArgumentTypeError(
            "--db-path deve ser absoluto e apontar para uma cópia em /tmp"
        )
    resolved = candidate.resolve()
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temporary_root)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Nesta etapa, --db-path deve permanecer dentro de /tmp"
        ) from error
    if resolved.is_dir():
        raise argparse.ArgumentTypeError("--db-path não pode ser diretório")
    if resolved.suffix.lower() not in {".db", ".sqlite"}:
        raise argparse.ArgumentTypeError(
            "Use um arquivo SQLite com extensão .db ou .sqlite"
        )
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Simulação offline da ingestão incremental PNCP com checkpoint v2"
        )
    )
    resources = sorted((*INCREMENTAL_RESOURCES.keys(), "ata"))
    parser.add_argument("--resource", required=True, choices=resources)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--uf", required=True)
    parser.add_argument("--modality", type=int, default=None)
    parser.add_argument(
        "--db-path",
        required=True,
        type=safe_offline_database_path,
        help="Banco temporário/cópia isolada; obrigatoriamente dentro de /tmp",
    )
    parser.add_argument(
        "--fixture",
        required=True,
        type=Path,
        help="Arquivo JSON contendo páginas ou alvos simulados",
    )
    parser.add_argument(
        "--job-name",
        default=None,
        help="Nome lógico; o job_id final continua sendo determinístico",
    )
    parser.add_argument("--worker-id", default="offline-worker")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--resume", action="store_true")
    action.add_argument("--reprocess", action="store_true")
    parser.add_argument("--lease-seconds", type=float, default=300.0)
    parser.add_argument(
        "--lease-renewal-seconds", type=float, default=120.0
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Obrigatório: a integração online ainda não está habilitada",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.offline:
        print(
            "ERRO: a coleta incremental online ainda não foi habilitada; "
            "execute somente com --offline e uma fixture local.",
            file=sys.stderr,
        )
        return 2
    if not args.fixture.is_file():
        print(
            f"ERRO: fixture offline não encontrada: {args.fixture}",
            file=sys.stderr,
        )
        return 2
    database_url = f"sqlite:///{args.db_path}"
    try:
        report = run_offline_incremental(
            IncrementalRunConfig(
                resource=args.resource,
                start_date=args.start_date,
                end_date=args.end_date,
                uf=args.uf,
                modality=args.modality,
                database_url=database_url,
                fixture_path=args.fixture,
                job_name=args.job_name,
                worker_id=args.worker_id,
                resume=args.resume,
                reprocess=args.reprocess,
                lease_seconds=args.lease_seconds,
                lease_renewal_seconds=args.lease_renewal_seconds,
            )
        )
    except (
        IncrementalConfigurationError,
        OfflineFixtureError,
        RuntimeError,
    ) as error:
        print(
            json.dumps(
                {"status": "FAILED", "error": str(error)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
