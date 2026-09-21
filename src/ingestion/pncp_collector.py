from __future__ import annotations

import time

from ..obs import JsonlLogger
from ..schema import CollectedRecord, SourceConfig, records_from_response
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


class ItemResultCollector:

    required_target_fields = ("cnpj", "ano", "sequencial")
    required_result_fields = (
        "numeroControlePNCPCompra",
        "numeroItem",
        "sequencialResultado",
    )

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.items_endpoint_template:
            raise ValueError(
                "Fonte resultado_item sem items_endpoint_template"
            )
        if not source.targets:
            raise ValueError("Fonte resultado_item sem targets configurados")

        ordinal = 0
        targets = source.targets[start_page - 1 :]
        if source.max_pages is not None:
            targets = targets[: source.max_pages]

        for target_index, target in enumerate(targets, start=start_page):
            context = self._target_context(target)
            items_endpoint = source.items_endpoint_template.format(**context)
            items = self._collect_items(source, items_endpoint)
            if source.max_items_per_purchase is not None:
                items = items[: source.max_items_per_purchase]

            result_count = 0
            for item in items:
                if item.get("temResultado") is False:
                    continue
                numero_item = item.get("numeroItem")
                if numero_item is None:
                    raise ValueError(
                        f"Item PNCP sem numeroItem em {items_endpoint}"
                    )

                result_context = {**context, "numeroItem": numero_item}
                result_endpoint = source.endpoint.format(**result_context)
                result_url = self.client.build_url(
                    result_endpoint, base_url=source.base
                )
                response = self.client.get(
                    result_endpoint,
                    base_url=source.base,
                    timeout_seconds=source.timeout_seconds,
                    headers=source.headers,
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
                    )
                if source.rate_limit_seconds:
                    time.sleep(source.rate_limit_seconds)

            self.logger.event(
                "pncp_purchase_results",
                source_id=source.id,
                purchase=context,
                items_count=len(items),
                results_count=result_count,
            )

    def _collect_items(self, source: SourceConfig, endpoint: str):
        if source.items_page_size < 1:
            raise ValueError("items_page_size deve ser maior que zero")

        items = []
        page = 1
        while True:
            params = {
                "pagina": page,
                "tamanhoPagina": source.items_page_size,
            }
            payload = self.client.get(
                endpoint,
                params,
                base_url=source.base,
                timeout_seconds=source.timeout_seconds,
                headers=source.headers,
            )
            page_items = records_from_response(payload)
            items.extend(page_items)
            if len(page_items) < source.items_page_size:
                return items
            page += 1
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

        cnpj = str(target["cnpj"])
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise ValueError("Target PNCP com CNPJ inválido")
        return {
            "cnpj": cnpj,
            "ano": int(target["ano"]),
            "sequencial": int(target["sequencial"]),
        }
