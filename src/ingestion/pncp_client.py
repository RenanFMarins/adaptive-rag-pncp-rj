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
    RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        logger: JsonlLogger | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
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
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> Any:
        url = self.build_url(endpoint, params, base_url)
        request = Request(
            url,
            headers={"Accept": "application/json", **(headers or {})},
            method="GET",
        )
        retry_limit = self.max_retries if max_retries is None else max_retries
        backoff = (
            self.retry_backoff_seconds
            if retry_backoff_seconds is None
            else retry_backoff_seconds
        )
        if retry_limit < 0:
            raise ValueError("max_retries não pode ser negativo")
        if backoff < 0:
            raise ValueError("retry_backoff_seconds não pode ser negativo")

        attempt = 0
        while True:
            self.logger.event(
                "pncp_request",
                method="GET",
                url=url,
                attempt=attempt + 1,
            )
            started = time.perf_counter()
            try:
                with urlopen(
                    request,
                    timeout=(
                        self.timeout_seconds
                        if timeout_seconds is None
                        else timeout_seconds
                    ),
                ) as response:
                    status = getattr(response, "status", None)
                    raw_payload = response.read()
                    if status == 204:
                        payload = []
                    else:
                        payload = json.loads(raw_payload.decode("utf-8"))
            except HTTPError as error:
                should_retry = (
                    error.code in self.RETRYABLE_HTTP_STATUS
                    and attempt < retry_limit
                )
                self.logger.event(
                    "pncp_response",
                    method="GET",
                    url=url,
                    status=error.code,
                    success=False,
                    retrying=should_retry,
                    attempt=attempt + 1,
                    latency_seconds=time.perf_counter() - started,
                )
                if should_retry:
                    self._wait_before_retry(backoff, attempt)
                    attempt += 1
                    continue
                raise PNCPClientError(
                    f"PNCP retornou HTTP {error.code} para {url}"
                ) from error
            except (URLError, TimeoutError) as error:
                should_retry = attempt < retry_limit
                self.logger.event(
                    "pncp_response",
                    method="GET",
                    url=url,
                    success=False,
                    error=str(error),
                    retrying=should_retry,
                    attempt=attempt + 1,
                    latency_seconds=time.perf_counter() - started,
                )
                if should_retry:
                    self._wait_before_retry(backoff, attempt)
                    attempt += 1
                    continue
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
                    attempt=attempt + 1,
                    latency_seconds=time.perf_counter() - started,
                )
                raise PNCPClientError(
                    f"Resposta do PNCP não é JSON válido: {url}"
                ) from error

            self.logger.event(
                "pncp_response",
                method="GET",
                url=url,
                status=status,
                success=True,
                attempt=attempt + 1,
                latency_seconds=time.perf_counter() - started,
            )
            return payload

    @staticmethod
    def _wait_before_retry(backoff: float, attempt: int) -> None:
        delay = backoff * (2**attempt)
        if delay:
            time.sleep(delay)

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
            max_retries=source.max_retries,
            retry_backoff_seconds=source.retry_backoff_seconds,
        )
        return payload, url
