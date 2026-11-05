from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Mapping

from app.core.database.connection import database_path
from src.ingestion.adapter_runner import (
    IncrementalAdapterPlan,
    run_adapter_incremental,
)
from src.ingestion.incremental_http import PNCPIncrementalHTTPAdapter
from src.ingestion.incremental_runner import (
    IncrementalConfigurationError,
    IncrementalRunConfig,
)
from src.ingestion.pncp_client import PNCPClient
from src.ingestion.pncp_incremental_adapters import (
    PNCPEndpointIncrementalAdapter,
    PNCPPCAIncrementalAdapter,
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
PCA_UPDATE_ENDPOINT = PNCPPCAIncrementalAdapter.DISCOVERY_ENDPOINT
DEFAULT_SCOPE_INVENTORY = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "pncp_rj_scope_inventory.json"
)


def _validate_online_scope(config: IncrementalRunConfig) -> None:
    if config.resource not in {"contratacao", "contrato", "pca"}:
        raise IncrementalConfigurationError(
            "Execução online habilitada somente para contratacao, "
            "contrato e pca"
        )
    if config.normalized_start != config.normalized_end:
        raise IncrementalConfigurationError(
            "Execução online aceita exatamente uma janela de um dia"
        )
    if config.uf != "RJ":
        raise IncrementalConfigurationError(
            "Execução online permanece restrita à UF RJ"
        )
    if config.resource == "contratacao":
        if config.modality not in range(1, 15):
            raise IncrementalConfigurationError(
                "Execução online de contratacao requer modalidade "
                "entre 1 e 14"
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


def _run_online_endpoint(
    config: IncrementalRunConfig,
    *,
    confirmed_operational_database: Path | None = None,
):
    _validate_online_scope(config)
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
    else:
        config, filters = _pca_scope(config)
        validation_scope = filters
        source_id = str(config.job_name)
    sqlite_path = Path(database_path(config.database_url)).resolve()
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
