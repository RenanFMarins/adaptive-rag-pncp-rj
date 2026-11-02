from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.fetch_corpus import resolve_source_targets
from src.ingestion.scope_inventory import OrganizationUnit, ScopeInventory
from src.schema import Manifest, SourceConfig


class RepositoryMustNotBeUsed:
    def __getattr__(self, name):
        raise AssertionError(f"Repositório RAW não deveria ser usado: {name}")


def _write_inventory(path: Path, *, tampered: bool = False) -> ScopeInventory:
    inventory = ScopeInventory(
        "RJ",
        (
            OrganizationUnit("12345678000199", "000001", "RJ"),
            OrganizationUnit("98765432000199", "000002", "RJ"),
        ),
    )
    identity = "inventory-invalido" if tampered else inventory.inventory_id
    path.write_text(
        json.dumps(
            {
                "scope": {
                    "uf": "RJ",
                    "inventory_id": identity,
                    "members": [member.target for member in inventory.members],
                },
                "coverage_plans": {
                    "ata_registro_preco": {
                        "inventory_id": inventory.inventory_id,
                        "member_count": 2,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return inventory


def _source() -> SourceConfig:
    return SourceConfig(
        id="atas-inventario",
        base="https://pncp.example",
        endpoint="/api/consulta/v1/atas",
        collector="pncp_price_registry",
        resource_type="ata_registro_preco",
        target_inventory_path="inventory.json",
    )


def test_resolves_frozen_inventory_without_scanning_raw(tmp_path: Path) -> None:
    inventory = _write_inventory(tmp_path / "inventory.json")

    resolved = resolve_source_targets(
        RepositoryMustNotBeUsed(),
        _source(),
        manifest_directory=tmp_path,
    )

    assert resolved.targets == inventory.targets


def test_rejects_tampered_inventory_identity(tmp_path: Path) -> None:
    _write_inventory(tmp_path / "inventory.json", tampered=True)

    with pytest.raises(ValueError, match="identidade divergente"):
        resolve_source_targets(
            RepositoryMustNotBeUsed(),
            _source(),
            manifest_directory=tmp_path,
        )


def test_rejects_mixed_inventory_and_raw_target_sources(tmp_path: Path) -> None:
    _write_inventory(tmp_path / "inventory.json")
    mixed = SourceConfig(
        **{**_source().__dict__, "target_source_id": "raw-source"}
    )

    with pytest.raises(ValueError, match="misturar inventário"):
        resolve_source_targets(
            RepositoryMustNotBeUsed(),
            mixed,
            manifest_directory=tmp_path,
        )


def test_expanded_ata_source_uses_homologated_request_policy() -> None:
    manifest_path = Path(__file__).resolve().parents[2] / "corpus_manifest.yaml"
    source = Manifest.load(manifest_path).source(
        "pncp_atas_rj_inventario_2023_ate_2026_10_31"
    )

    assert source.rate_limit_seconds == 2.0
    assert source.max_concurrency == 1
    assert source.max_retries == 5
