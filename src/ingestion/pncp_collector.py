from __future__ import annotations

import re
import time

from ..obs import JsonlLogger
from ..schema import (
    CollectionCheckpoint,
    CollectedRecord,
    SourceConfig,
    records_from_response,
)
from .pncp_client import PNCPClient


class PNCPCollector:
    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        ordinal = 0
        page = start_page
        while source.max_pages is None or page < start_page + source.max_pages:
            response, url = self.client.fetch_page(source, page)
            records = records_from_response(response, source.item_path)
            if not records:
                break
            for payload in records:
                ordinal += 1
                yield CollectedRecord(
                    source.id, payload, url, str(page), ordinal
                )
            self.logger.event(
                "pncp_page",
                source_id=source.id,
                page=page,
                count=len(records),
            )
            page += 1
            if source.rate_limit_seconds:
                time.sleep(source.rate_limit_seconds)


class PCACollector(PNCPCollector):
    """Collector PCA que preserva o registro sem normalização."""

    external_id_field = "idPcaPncp"

    def collect(self, source: SourceConfig, start_page: int = 1):
        for record in super().collect(source, start_page):
            if not record.payload.get(self.external_id_field):
                raise ValueError(
                    "Registro PCA sem idPcaPncp; coleta interrompida"
                )
            yield record


class PurchaseItemCollector:
    """Coleta e preserva os itens pertencentes a contratações RAW."""

    required_target_fields = ("cnpj", "ano", "sequencial", "numero_controle")

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.targets:
            raise ValueError(
                "Fonte contratacao_item sem contratações-alvo configuradas"
            )
        if source.items_page_size < 1:
            raise ValueError("items_page_size deve ser maior que zero")

        ordinal = 0
        targets = source.targets[start_page - 1 :]
        if source.max_pages is not None:
            targets = targets[: source.max_pages]

        for target_index, target in enumerate(targets, start=start_page):
            context = self._target_context(target)
            endpoint = source.endpoint.format(**context)
            page = 1
            target_items = 0

            while True:
                params = {
                    "pagina": page,
                    "tamanhoPagina": source.items_page_size,
                }
                source_url = self.client.build_url(
                    endpoint, params, base_url=source.base
                )
                response = self.client.get(
                    endpoint,
                    params,
                    base_url=source.base,
                    timeout_seconds=source.timeout_seconds,
                    headers=source.headers,
                    max_retries=source.max_retries,
                    retry_backoff_seconds=source.retry_backoff_seconds,
                )
                items = records_from_response(response)
                for payload in items:
                    numero_item = payload.get("numeroItem")
                    if numero_item is None:
                        raise ValueError(
                            f"Item PNCP sem numeroItem em {endpoint}"
                        )
                    ordinal += 1
                    target_items += 1
                    yield CollectedRecord(
                        source.id,
                        payload,
                        source_url,
                        str(target_index),
                        ordinal,
                        external_id=(
                            f"{context['numero_controle']}|{numero_item}"
                        ),
                    )

                self.logger.event(
                    "pncp_purchase_items_page",
                    source_id=source.id,
                    target_index=target_index,
                    page=page,
                    count=len(items),
                )
                if len(items) < source.items_page_size:
                    break
                page += 1
                if source.rate_limit_seconds:
                    time.sleep(source.rate_limit_seconds)

            self.logger.event(
                "pncp_purchase_items",
                source_id=source.id,
                target_index=target_index,
                items_count=target_items,
            )
            yield CollectionCheckpoint(str(target_index))
            if source.rate_limit_seconds:
                time.sleep(source.rate_limit_seconds)

    def _target_context(self, target):
        missing = [
            field
            for field in self.required_target_fields
            if target.get(field) in (None, "")
        ]
        if missing:
            raise ValueError(
                "Target PNCP incompleto para itens: " + ", ".join(missing)
            )

        cnpj = str(target["cnpj"])
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise ValueError("Target PNCP com CNPJ inválido")
        return {
            "cnpj": cnpj,
            "ano": int(target["ano"]),
            "sequencial": int(target["sequencial"]),
            "numero_controle": str(target["numero_controle"]),
        }


class ItemResultCollector:
    """Coleta resultados usando os itens já preservados na camada RAW."""

    required_target_fields = ("numero_controle", "numero_item")
    required_result_fields = (
        "numeroControlePNCPCompra",
        "numeroItem",
        "sequencialResultado",
    )
    control_number_pattern = re.compile(
        r"^(?P<cnpj>\d{14})-\d+-(?P<sequencial>\d+)/(?P<ano>\d{4})$"
    )

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.targets:
            raise ValueError(
                "Fonte resultado_item sem itens RAW configurados como targets"
            )

        ordinal = 0
        targets = source.targets[start_page - 1 :]
        if source.max_pages is not None:
            targets = targets[: source.max_pages]

        for target_index, target in enumerate(targets, start=start_page):
            context = self._target_context(target)
            result_count = 0
            if target.get("tem_resultado") is not False:
                result_endpoint = source.endpoint.format(**context)
                result_url = self.client.build_url(
                    result_endpoint, base_url=source.base
                )
                response = self.client.get(
                    result_endpoint,
                    base_url=source.base,
                    timeout_seconds=source.timeout_seconds,
                    headers=source.headers,
                    max_retries=source.max_retries,
                    retry_backoff_seconds=source.retry_backoff_seconds,
                )
                results = records_from_response(response)
                for payload in results:
                    missing = [
                        field
                        for field in self.required_result_fields
                        if payload.get(field) is None
                    ]
                    if missing:
                        raise ValueError(
                            "Resultado de item sem identificador obrigatório: "
                            + ", ".join(missing)
                        )
                    ordinal += 1
                    result_count += 1
                    yield CollectedRecord(
                        source.id,
                        payload,
                        result_url,
                        str(target_index),
                        ordinal,
                        external_id=(
                            f"{context['numero_controle']}|"
                            f"{context['numeroItem']}|"
                            f"{payload['sequencialResultado']}"
                        ),
                    )

            self.logger.event(
                "pncp_item_results",
                source_id=source.id,
                target_index=target_index,
                numero_controle=context["numero_controle"],
                numero_item=context["numeroItem"],
                requested=target.get("tem_resultado") is not False,
                results_count=result_count,
            )
            yield CollectionCheckpoint(str(target_index))
            if source.rate_limit_seconds:
                time.sleep(source.rate_limit_seconds)

    def _target_context(self, target):
        missing = [
            field
            for field in self.required_target_fields
            if target.get(field) in (None, "")
        ]
        if missing:
            raise ValueError(
                "Target PNCP incompleto: " + ", ".join(missing)
            )

        numero_controle = str(target["numero_controle"])
        match = self.control_number_pattern.fullmatch(numero_controle)
        if not match:
            raise ValueError(
                "Item RAW com numeroControlePNCP do pai inválido"
            )
        return {
            "cnpj": match.group("cnpj"),
            "ano": int(match.group("ano")),
            "sequencial": int(match.group("sequencial")),
            "numeroItem": int(target["numero_item"]),
            "numero_controle": numero_controle,
        }
