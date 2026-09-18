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
