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
from src.ingestion.online_pilot import run_online_pilot  # noqa: E402


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
            "Ingestão incremental PNCP protegida por checkpoint v2"
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
        type=Path,
        help="Arquivo JSON contendo páginas ou alvos simulados (offline)",
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
        "--reconciliation-cadence-days",
        type=int,
        default=None,
        help="Sobrescreve a cadência padrão do recurso dependente",
    )
    parser.add_argument(
        "--reconciliation-horizon-days",
        type=int,
        default=None,
        help="Sobrescreve o horizonte padrão do recurso dependente",
    )
    parser.add_argument(
        "--coverage-name",
        default=None,
        help="Nome estável do manifesto de cobertura composta",
    )
    parser.add_argument(
        "--coverage-member",
        default=None,
        help="Membro/shard processado por esta execução",
    )
    parser.add_argument(
        "--coverage-members",
        nargs="+",
        default=(),
        help="Conjunto completo e congelado de membros esperados",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Executa somente a fixture local, sem acesso à rede",
    )
    parser.add_argument(
        "--online-pilot",
        action="store_true",
        help=(
            "Habilita explicitamente o piloto real de contratações: RJ, "
            "uma modalidade, um dia e banco em /tmp"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.offline and args.online_pilot:
        print(
            "ERRO: --offline e --online-pilot são mutuamente exclusivos.",
            file=sys.stderr,
        )
        return 2
    if not args.offline and not args.online_pilot:
        print(
            "ERRO: escolha explicitamente --offline ou --online-pilot.",
            file=sys.stderr,
        )
        return 2
    if args.offline and (args.fixture is None or not args.fixture.is_file()):
        print(
            f"ERRO: fixture offline não encontrada: {args.fixture}",
            file=sys.stderr,
        )
        return 2
    if args.online_pilot and args.fixture is not None:
        print(
            "ERRO: --online-pilot não aceita --fixture.",
            file=sys.stderr,
        )
        return 2
    database_url = f"sqlite:///{args.db_path}"
    try:
        config = IncrementalRunConfig(
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
            reconciliation_cadence_days=(
                args.reconciliation_cadence_days
            ),
            reconciliation_horizon_days=(
                args.reconciliation_horizon_days
            ),
            coverage_name=args.coverage_name,
            coverage_member=args.coverage_member,
            coverage_members=tuple(args.coverage_members),
        )
        report = (
            run_offline_incremental(config)
            if args.offline
            else run_online_pilot(config)
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
