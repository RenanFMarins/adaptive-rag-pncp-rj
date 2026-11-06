from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sqlite3
from typing import Mapping

from app.core.database.connection import database_path
from src.ingestion.adapter_runner import (
    IncrementalAdapterPlan,
    run_adapter_incremental,
)
from src.ingestion.incremental_http import PNCPIncrementalHTTPAdapter
from src.ingestion.dependency_discovery import (
    DependencyDiscoveryError,
    discover_dependency_targets,
)
from src.ingestion.incremental_runner import (
    IncrementalConfigurationError,
    IncrementalRunConfig,
)
from src.ingestion.pncp_client import PNCPClient
from src.ingestion.pncp_incremental_adapters import (
    PNCPEndpointIncrementalAdapter,
    PNCPPCAIncrementalAdapter,
    PNCPRelationshipIncrementalAdapter,
    RELATIONSHIP_ENDPOINTS,
    UPDATE_ENDPOINTS,
)
from src.ingestion.scope_inventory import (
    OrganizationUnit,
    ScopeInventoryError,
    load_scope_inventory,
)
from src.obs import JsonlLogger


PNCP_BASE_URL = "https://pncp.gov.br"
CONTRATACAO_UPDATE_ENDPOINT = UPDATE_ENDPOINTS["contratacao"].endpoint
CONTRATO_UPDATE_ENDPOINT = UPDATE_ENDPOINTS["contrato"].endpoint
ATA_UPDATE_ENDPOINT = UPDATE_ENDPOINTS["ata_registro_preco"].endpoint
CONTRATACAO_ITEM_ENDPOINT = RELATIONSHIP_ENDPOINTS[
    "contratacao_item"
].endpoint
PCA_UPDATE_ENDPOINT = PNCPPCAIncrementalAdapter.DISCOVERY_ENDPOINT
DEFAULT_SCOPE_INVENTORY = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "pncp_rj_scope_inventory.json"
)


def _validate_online_scope(config: IncrementalRunConfig) -> None:
    if config.resource not in {
        "contratacao",
        "contrato",
        "pca",
        "ata_registro_preco",
        "contratacao_item",
    }:
        raise IncrementalConfigurationError(
            "Execução online habilitada somente para contratacao, "
            "contrato, pca, ata_registro_preco e contratacao_item"
        )
    if config.normalized_start != config.normalized_end:
        raise IncrementalConfigurationError(
            "Execução online aceita exatamente uma janela de um dia"
        )
    if config.uf != "RJ":
        raise IncrementalConfigurationError(
            "Execução online permanece restrita à UF RJ"
        )
    if config.resource != "contratacao_item" and config.parent_run_id:
        raise IncrementalConfigurationError(
            "--parent-run-id é aceito somente por recursos dependentes"
        )
    if config.resource == "contratacao":
        if config.modality not in range(1, 15):
            raise IncrementalConfigurationError(
                "Execução online de contratacao requer modalidade "
                "entre 1 e 14"
            )
        return
    if config.resource == "contratacao_item":
        if not config.parent_run_id:
            raise IncrementalConfigurationError(
                "Execução online de contratacao_item requer "
                "--parent-run-id"
            )
        if config.modality is not None:
            raise IncrementalConfigurationError(
                "Execução online de contratacao_item não aceita modalidade"
            )
        if config.organization_cnpj or config.unit_code:
            raise IncrementalConfigurationError(
                "contratacao_item deriva o escopo da execução pai e não "
                "aceita CNPJ/unidade avulsos"
            )
        return
    if config.modality is not None:
        raise IncrementalConfigurationError(
            f"Execução online de {config.resource} não aceita modalidade"
        )


def _inventory_scope(
    config: IncrementalRunConfig,
) -> tuple[IncrementalRunConfig, OrganizationUnit, Mapping[str, object]]:
    try:
        member = OrganizationUnit(
            config.organization_cnpj or "",
            config.unit_code or "",
            config.uf,
        )
        inventory, plan = load_scope_inventory(
            config.scope_inventory_path or DEFAULT_SCOPE_INVENTORY,
            resource=config.resource,
        )
    except ScopeInventoryError as error:
        raise IncrementalConfigurationError(str(error)) from error
    if inventory.uf != config.uf:
        raise IncrementalConfigurationError(
            f"Inventário de {config.resource} não corresponde à UF "
            "solicitada"
        )
    if member not in inventory.members:
        raise IncrementalConfigurationError(
            "CNPJ/unidade não pertence ao inventário congelado do RJ"
        )

    expected_coverage = (
        str(plan["name"]),
        member.member_key,
        inventory.coverage_members,
    )
    supplied_coverage = (
        config.coverage_name,
        config.coverage_member,
        config.coverage_members,
    )
    if any(supplied_coverage) and supplied_coverage != expected_coverage:
        raise IncrementalConfigurationError(
            "Cobertura informada diverge do inventário congelado"
        )
    source_id = config.job_name or (
        f"pncp_incremental_pilot_{config.resource}_rj_"
        f"{member.cnpj}_{member.unit_code}"
    )
    prepared = replace(
        config,
        job_name=source_id,
        coverage_name=expected_coverage[0],
        coverage_member=expected_coverage[1],
        coverage_members=expected_coverage[2],
    )
    return prepared, member, plan


def _contract_scope(
    config: IncrementalRunConfig,
) -> tuple[IncrementalRunConfig, dict[str, str], dict[str, str]]:
    prepared, member, _ = _inventory_scope(config)
    filters = {
        "cnpjOrgao": member.cnpj,
        "codigoUnidadeAdministrativa": member.unit_code,
    }
    validation_scope = {**filters, "uf": config.uf}
    return prepared, filters, validation_scope


def _pca_scope(
    config: IncrementalRunConfig,
) -> tuple[IncrementalRunConfig, dict[str, str]]:
    prepared, member, _ = _inventory_scope(config)
    return prepared, {
        "cnpj": member.cnpj,
        "codigoUnidade": member.unit_code,
    }


def _price_registry_scope(
    config: IncrementalRunConfig,
) -> tuple[IncrementalRunConfig, dict[str, str]]:
    prepared, member, _ = _inventory_scope(config)
    return prepared, {
        "cnpj": member.cnpj,
        "codigoUnidadeAdministrativa": member.unit_code,
    }


def _dependency_discoveries(
    config: IncrementalRunConfig,
    sqlite_path: Path,
) -> tuple[dict[str, object], ...]:
    connection = None
    try:
        connection = sqlite3.connect(
            f"{sqlite_path.as_uri()}?mode=ro",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        return discover_dependency_targets(
            connection,
            str(config.parent_run_id),
            config.resource,
            expected_uf=config.uf,
        )
    except (DependencyDiscoveryError, sqlite3.Error) as error:
        raise IncrementalConfigurationError(str(error)) from error
    finally:
        if connection is not None:
            connection.close()


def _relationship_events(
    adapter: PNCPRelationshipIncrementalAdapter,
    resource: str,
    source_id: str,
    targets,
):
    for target in targets:
        yield from adapter.collect_target(
            resource,
            source_id,
            target,
            base_url=PNCP_BASE_URL,
            timeout_seconds=30.0,
            max_retries=2,
            retry_backoff_seconds=0.5,
        )


def _run_online_endpoint(
    config: IncrementalRunConfig,
    *,
    confirmed_operational_database: Path | None = None,
):
    if config.resource == "ata":
        config = replace(config, resource="ata_registro_preco")
    _validate_online_scope(config)
    sqlite_path = Path(database_path(config.database_url)).resolve()
    if config.resource == "contratacao":
        source_id = config.job_name or (
            f"pncp_incremental_pilot_contratacao_rj_m{config.modality:02d}"
        )
        config = replace(config, job_name=source_id)
        filters = {
            "codigoModalidadeContratacao": config.modality,
            "uf": config.uf,
        }
        validation_scope = filters
    elif config.resource == "contrato":
        config, filters, validation_scope = _contract_scope(config)
        source_id = str(config.job_name)
    elif config.resource == "pca":
        config, filters = _pca_scope(config)
        validation_scope = filters
        source_id = str(config.job_name)
    elif config.resource == "contratacao_item":
        source_id = config.job_name or "pncp_incremental_contratacao_item_rj"
        config = replace(config, job_name=source_id)
        filters = {"scope": "parentes_incrementais_rj"}
        validation_scope = filters
    else:
        config, filters = _price_registry_scope(config)
        validation_scope = filters
        source_id = str(config.job_name)
    http_log = (
        config.log_path.with_name(
            f"{config.log_path.stem}.http{config.log_path.suffix}"
        )
        if config.log_path is not None
        else sqlite_path.with_suffix(".http.jsonl")
    )
    client = PNCPClient(
        base_url=PNCP_BASE_URL,
        timeout_seconds=30.0,
        max_retries=2,
        retry_backoff_seconds=0.5,
        logger=JsonlLogger(http_log),
    )
    transport = PNCPIncrementalHTTPAdapter(client)
    discoveries = ()
    if config.resource == "pca":
        pca_adapter = PNCPPCAIncrementalAdapter(transport)
        endpoint = PCA_UPDATE_ENDPOINT
        event_provider = lambda _: pca_adapter.collect(
            source_id,
            config.normalized_start,
            config.normalized_end,
            filters=filters,
            base_url=PNCP_BASE_URL,
            timeout_seconds=30.0,
            max_retries=2,
            retry_backoff_seconds=0.5,
        )
    elif config.resource == "contratacao_item":
        relationship_adapter = PNCPRelationshipIncrementalAdapter(transport)
        endpoint = CONTRATACAO_ITEM_ENDPOINT
        discoveries = _dependency_discoveries(config, sqlite_path)
        event_provider = lambda targets: _relationship_events(
            relationship_adapter,
            config.resource,
            source_id,
            targets,
        )
    else:
        endpoint_adapter = PNCPEndpointIncrementalAdapter(transport)
        endpoint = UPDATE_ENDPOINTS[config.resource].endpoint
        event_provider = lambda _: endpoint_adapter.collect(
            config.resource,
            source_id,
            config.normalized_start,
            config.normalized_end,
            filters=filters,
            scope=validation_scope,
            base_url=PNCP_BASE_URL,
            timeout_seconds=30.0,
            max_retries=2,
            retry_backoff_seconds=0.5,
        )
    plan = IncrementalAdapterPlan(
        endpoint=endpoint,
        filters=filters,
        discoveries=discoveries,
        event_provider=event_provider,
    )
    return run_adapter_incremental(
        config,
        plan,
        confirmed_operational_database=confirmed_operational_database,
    )


def run_online_pilot(config: IncrementalRunConfig):
    """Executa um piloto online protegido pelo runner restrito a /tmp."""

    return _run_online_endpoint(config)


def run_online_operational(
    config: IncrementalRunConfig, confirmed_database: Path
):
    """Executa uma janela real com confirmação explícita do banco."""

    if config.log_path is None:
        raise IncrementalConfigurationError(
            "Execução operacional requer --log-path explícito"
        )
    return _run_online_endpoint(
        config,
        confirmed_operational_database=confirmed_database,
    )


__all__ = ["run_online_operational", "run_online_pilot"]
