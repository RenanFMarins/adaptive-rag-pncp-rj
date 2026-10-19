from __future__ import annotations

from pathlib import Path

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
)
from src.obs import JsonlLogger


PNCP_BASE_URL = "https://pncp.gov.br"
CONTRATACAO_UPDATE_ENDPOINT = (
    "/api/consulta/v1/contratacoes/atualizacao"
)


def run_online_pilot(config: IncrementalRunConfig):
    """Executa somente o piloto de contratação, protegido pelo runner /tmp."""

    if config.resource != "contratacao":
        raise IncrementalConfigurationError(
            "Piloto online habilitado somente para contratacao"
        )
    if config.normalized_start != config.normalized_end:
        raise IncrementalConfigurationError(
            "Piloto online aceita exatamente uma janela de um dia"
        )
    if config.uf != "RJ":
        raise IncrementalConfigurationError(
            "Piloto online permanece restrito à UF RJ"
        )
    if config.modality not in range(1, 15):
        raise IncrementalConfigurationError(
            "Piloto online requer modalidade entre 1 e 14"
        )
    source_id = config.job_name or (
        f"pncp_incremental_pilot_contratacao_rj_m{config.modality:02d}"
    )
    if config.job_name is None:
        config = IncrementalRunConfig(
            **{**config.__dict__, "job_name": source_id}
        )
    sqlite_path = Path(database_path(config.database_url))
    http_log = sqlite_path.with_suffix(".http.jsonl")
    filters = {
        "codigoModalidadeContratacao": config.modality,
        "uf": config.uf,
    }
    client = PNCPClient(
        base_url=PNCP_BASE_URL,
        timeout_seconds=30.0,
        max_retries=2,
        retry_backoff_seconds=0.5,
        logger=JsonlLogger(http_log),
    )
    adapter = PNCPEndpointIncrementalAdapter(
        PNCPIncrementalHTTPAdapter(client)
    )
    plan = IncrementalAdapterPlan(
        endpoint=CONTRATACAO_UPDATE_ENDPOINT,
        filters=filters,
        event_provider=lambda _: adapter.collect(
            "contratacao",
            source_id,
            config.normalized_start,
            config.normalized_end,
            filters=filters,
            base_url=PNCP_BASE_URL,
            timeout_seconds=30.0,
            max_retries=2,
            retry_backoff_seconds=0.5,
        ),
    )
    return run_adapter_incremental(config, plan)


__all__ = ["run_online_pilot"]
