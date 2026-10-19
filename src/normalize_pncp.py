from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from src.normalization.runner import normalize_core


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normaliza um snapshot RAW PNCP em outro banco SQLite."
    )
    parser.add_argument("--raw-database", required=True)
    parser.add_argument("--output-database", required=True)
    parser.add_argument(
        "--transform-version",
        default=None,
    )
    parser.add_argument(
        "--scope-inventory",
        default="config/pncp_rj_scope_inventory.json",
    )
    parser.add_argument(
        "--known-empenho-gaps",
        type=int,
        default=0,
        help="Quantidade auditada de alvos de empenho com lacuna conhecida",
    )
    args = parser.parse_args()
    transform_version = args.transform_version or "normalized-v1"
    result = normalize_core(
        args.raw_database,
        args.output_database,
        transform_version=transform_version,
        scope_inventory_path=args.scope_inventory,
        known_commitment_gap_count=args.known_empenho_gaps,
    )
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
