from __future__ import annotations

import json
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..obs import JsonlLogger
from ..schema import SourceConfig


class PNCPClientError(RuntimeError):
    """Erro de comunicação ou desserialização da resposta do PNCP."""


class PNCPClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        logger: JsonlLogger | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.logger = logger or JsonlLogger()

    def build_url(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        base_url: str | None = None,
    ) -> str:
        if endpoint.startswith(("http://", "https://")):
            url = endpoint
        else:
            origin = base_url or self.base_url
            if not origin:
                raise ValueError("PNCPClient requer uma URL base configurada")
            url = f"{origin.rstrip('/')}/{endpoint.lstrip('/')}"
        if params:
            return f"{url}?{urlencode(params, doseq=True)}"
        return url

    def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        url = self.build_url(endpoint, params, base_url)
        request = Request(
            url,
            headers={"Accept": "application/json", **(headers or {})},
            method="GET",
        )
        self.logger.event("pncp_request", method="GET", url=url)
        started = time.perf_counter()
        try:
            with urlopen(
                request,
                timeout=timeout_seconds or self.timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            self.logger.event(
                "pncp_response",
                method="GET",
                url=url,
                status=error.code,
                success=False,
                latency_seconds=time.perf_counter() - started,
            )
            raise PNCPClientError(
                f"PNCP retornou HTTP {error.code} para {url}"
            ) from error
        except (URLError, TimeoutError) as error:
            self.logger.event(
                "pncp_response",
                method="GET",
                url=url,
                success=False,
                error=str(error),
                latency_seconds=time.perf_counter() - started,
            )
            raise PNCPClientError(
                f"Falha de comunicação com o PNCP: {error}"
            ) from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self.logger.event(
                "pncp_response",
                method="GET",
                url=url,
                success=False,
                error="invalid_json",
                latency_seconds=time.perf_counter() - started,
            )
            raise PNCPClientError(
                f"Resposta do PNCP não é JSON válido: {url}"
            ) from error

        self.logger.event(
            "pncp_response",
            method="GET",
            url=url,
            success=True,
            latency_seconds=time.perf_counter() - started,
        )
        return payload

    def fetch_page(self, source: SourceConfig, page: int) -> tuple[Any, str]:
        params = dict(source.params)
        params[source.page_param] = page
        params[source.page_size_param] = source.page_size
        url = self.build_url(source.endpoint, params, source.base)
        payload = self.get(
            source.endpoint,
            params,
            base_url=source.base,
            timeout_seconds=source.timeout_seconds,
            headers=source.headers,
        )
        return payload, url
