from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import date, timedelta
import re
import threading
import time
from typing import Any, Callable, Iterable, Mapping, TypeVar

from ..obs import JsonlLogger
from ..schema import (
    CollectionCheckpoint,
    CollectedRecord,
    SourceConfig,
    records_from_response,
    value_at_path,
)
from .pncp_client import PNCPClient, PNCPClientError


class PNCPCollector:
    record_empty_pages = False

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
            records = (
                []
                if response == []
                else records_from_response(response, source.item_path)
            )
            query_params = {
                **source.audit_context,
                **source.params,
                source.page_param: page,
                source.page_size_param: source.page_size,
            }
            self.logger.event(
                "pncp_page",
                source_id=source.id,
                resource_type=source.resource_type,
                page=page,
                count=len(records),
                **_response_envelope_summary(response),
            )
            if not records:
                if self.record_empty_pages:
                    yield CollectionCheckpoint(str(page))
                break
            for payload in records:
                ordinal += 1
                yield CollectedRecord(
                    source.id,
                    payload,
                    url,
                    str(page),
                    ordinal,
                    query_params=query_params,
                )
            if _is_last_response_page(response, page):
                break
            page += 1
            if source.rate_limit_seconds:
                time.sleep(source.rate_limit_seconds)


class PCACollector(PNCPCollector):
    """Collector PCA que preserva o registro sem normalização."""

    external_id_field = "idPcaPncp"

    def collect(self, source: SourceConfig, start_page: int = 1):
        for record in super().collect(source, start_page):
            if isinstance(record, CollectionCheckpoint):
                yield record
                continue
            if not record.payload.get(self.external_id_field):
                raise ValueError(
                    "Registro PCA sem idPcaPncp; coleta interrompida"
                )
            yield record


class PCAFullCollector:
    """Descobre PCAs por órgão e preserva cada plano completo com seus itens."""

    required_target_fields = ("cnpj",)
    control_number_pattern = re.compile(
        r"^(?P<cnpj>\d{14})-0-(?P<sequencial>\d+)/(?P<ano>\d{4})$"
    )

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.targets:
            raise ValueError("Fonte PCA sem órgãos RAW configurados como targets")
        if not source.discovery_endpoint_template:
            raise ValueError("Fonte PCA sem endpoint de descoberta")
        try:
            ano = int(source.params["anoPca"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Fonte PCA sem anoPca válido") from error

        targets = list(
            enumerate(source.targets[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            targets = targets[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)

        def request(endpoint: str, not_found_as_empty: bool = False):
            url = self.client.build_url(endpoint, base_url=source.base)
            pacer.wait()
            payload = self.client.get(
                endpoint,
                base_url=source.base,
                timeout_seconds=source.timeout_seconds,
                headers=source.headers,
                max_retries=source.max_retries,
                retry_backoff_seconds=source.retry_backoff_seconds,
                not_found_as_empty=not_found_as_empty,
            )
            return payload, url

        def fetch(indexed_target):
            target_index, target = indexed_target
            cnpj = self._target_cnpj(target)
            discovery_endpoint = source.discovery_endpoint_template.format(
                cnpj=cnpj, ano=ano
            )
            discovery, _ = request(
                discovery_endpoint, not_found_as_empty=True
            )
            summaries = records_from_response(discovery)
            plans = []
            seen = set()
            for summary in summaries:
                sequencial = summary.get("sequencialPca")
                numero_controle = summary.get("numeroControlePNCP")
                context = self._plan_context(
                    cnpj, ano, sequencial, numero_controle
                )
                if numero_controle in seen:
                    continue
                seen.add(numero_controle)
                endpoint = source.endpoint.format(**context)
                payload, url = request(endpoint)
                self._validate_payload(payload, context, url)
                plans.append((context, url, payload))
            return target_index, cnpj, plans

        ordinal = 0
        for target_index, cnpj, plans in _ordered_parallel_map(
            fetch, targets, source.max_concurrency
        ):
            for context, source_url, payload in plans:
                ordinal += 1
                yield CollectedRecord(
                    source.id,
                    payload,
                    source_url,
                    str(target_index),
                    ordinal,
                    external_id=context["numero_controle"],
                    query_params={
                        **source.audit_context,
                        "anoPca": ano,
                        "cnpj": cnpj,
                        "sequencialPca": context["sequencial"],
                        "numeroControlePNCP": context["numero_controle"],
                        "target_index": target_index,
                    },
                )
            self.logger.event(
                "pncp_pca_plans",
                source_id=source.id,
                target_index=target_index,
                cnpj=cnpj,
                ano_pca=ano,
                plans_count=len(plans),
            )
            yield CollectionCheckpoint(str(target_index))

    def _target_cnpj(self, target) -> str:
        missing = [
            field
            for field in self.required_target_fields
            if target.get(field) in (None, "")
        ]
        if missing:
            raise ValueError("Target PCA incompleto: " + ", ".join(missing))
        cnpj = str(target["cnpj"])
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise ValueError("Target PCA com CNPJ inválido")
        return cnpj

    def _plan_context(self, cnpj, ano, sequencial, numero_controle):
        if sequencial is None or not numero_controle:
            raise ValueError("Resumo de PCA sem identificador obrigatório")
        match = self.control_number_pattern.fullmatch(str(numero_controle))
        if not match:
            raise ValueError("Resumo de PCA com numeroControlePNCP inválido")
        if (
            match.group("cnpj") != cnpj
            or int(match.group("ano")) != ano
            or int(match.group("sequencial")) != int(sequencial)
        ):
            raise ValueError("Resumo de PCA inconsistente com o órgão/ano alvo")
        return {
            "cnpj": cnpj,
            "ano": ano,
            "sequencial": int(sequencial),
            "numero_controle": str(numero_controle),
        }

    @staticmethod
    def _validate_payload(payload, context, source_url):
        if not isinstance(payload, Mapping):
            raise ValueError(f"PCA completo não retornou objeto em {source_url}")
        items = payload.get("itens")
        if not isinstance(items, list):
            raise ValueError(f"PCA completo sem lista de itens em {source_url}")
        for item in items:
            if not isinstance(item, Mapping):
                raise ValueError(f"PCA completo possui item inválido em {source_url}")
            if (
                str(item.get("cnpj")) != context["cnpj"]
                or int(item.get("anoPca", -1)) != context["ano"]
                or int(item.get("sequencialPca", -1))
                != context["sequencial"]
            ):
                raise ValueError(f"Item fora do PCA esperado em {source_url}")


class PriceRegistryCollector:
    """Coleta atas vigentes por unidade do RJ em janelas anuais."""

    required_target_fields = ("cnpj", "codigo_unidade", "uf")

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.targets:
            raise ValueError("Fonte de atas sem unidades RAW configuradas")
        expected_uf = str(source.audit_context.get("uf") or "")
        if not expected_uf:
            raise ValueError("Fonte de atas sem UF de auditoria")
        windows = _annual_date_windows(
            source.params.get("dataInicial"),
            source.params.get("dataFinal"),
        )
        work_items = [
            (target, window_index, window_start, window_end)
            for target in source.targets
            for window_index, (window_start, window_end) in enumerate(
                windows, start=1
            )
        ]
        indexed_items = list(
            enumerate(work_items[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            indexed_items = indexed_items[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)

        def fetch(indexed_item):
            work_index, item = indexed_item
            target, window_index, window_start, window_end = item
            context = self._target_context(target, expected_uf)
            page = 1
            found = []
            pages_requested = 0
            while True:
                params = {
                    "dataInicial": window_start,
                    "dataFinal": window_end,
                    "cnpj": context["cnpj"],
                    "codigoUnidadeAdministrativa": context[
                        "codigo_unidade"
                    ],
                    source.page_param: page,
                    source.page_size_param: source.page_size,
                }
                url = self.client.build_url(
                    source.endpoint, params, base_url=source.base
                )
                pacer.wait()
                response = self.client.get(
                    source.endpoint,
                    params,
                    base_url=source.base,
                    timeout_seconds=source.timeout_seconds,
                    headers=source.headers,
                    max_retries=source.max_retries,
                    retry_backoff_seconds=source.retry_backoff_seconds,
                )
                pages_requested += 1
                records = (
                    []
                    if response == []
                    else records_from_response(response, source.item_path)
                )
                for payload in records:
                    external_id = self._validate_ata(payload, context, url)
                    if external_id is not None:
                        found.append((payload, external_id, url, params))
                if not records or _is_last_response_page(response, page):
                    break
                page += 1
            return (
                work_index,
                context,
                window_index,
                window_start,
                window_end,
                found,
                pages_requested,
            )

        ordinal = 0
        for (
            work_index,
            context,
            window_index,
            window_start,
            window_end,
            records,
            pages_requested,
        ) in _ordered_parallel_map(
            fetch, indexed_items, source.max_concurrency
        ):
            for payload, external_id, url, params in records:
                ordinal += 1
                yield CollectedRecord(
                    source.id,
                    payload,
                    url,
                    str(work_index),
                    ordinal,
                    external_id=external_id,
                    query_params={
                        **source.audit_context,
                        **params,
                        "window_index": window_index,
                        "target_index": (work_index - 1) // len(windows) + 1,
                    },
                )
            self.logger.event(
                "pncp_price_registry",
                source_id=source.id,
                work_index=work_index,
                cnpj=context["cnpj"],
                codigo_unidade=context["codigo_unidade"],
                uf=context["uf"],
                window_index=window_index,
                window_start=window_start,
                window_end=window_end,
                pages_requested=pages_requested,
                records_count=len(records),
            )
            yield CollectionCheckpoint(str(work_index))

    def _target_context(self, target, expected_uf):
        missing = [
            field
            for field in self.required_target_fields
            if target.get(field) in (None, "")
        ]
        if missing:
            raise ValueError("Target de ata incompleto: " + ", ".join(missing))
        cnpj = str(target["cnpj"])
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise ValueError("Target de ata com CNPJ inválido")
        actual_uf = str(target["uf"])
        if actual_uf != expected_uf:
            raise ValueError(
                f"Unidade fora do recorte: esperado={expected_uf}, "
                f"recebido={actual_uf}"
            )
        return {
            "cnpj": cnpj,
            "codigo_unidade": str(target["codigo_unidade"]),
            "uf": actual_uf,
        }

    def _validate_ata(self, payload, context, source_url):
        external_id = payload.get("numeroControlePNCPAta")
        actual_cnpj = payload.get("cnpjOrgao")
        actual_unit = payload.get("codigoUnidadeOrgao")
        if not external_id:
            raise ValueError(f"Ata sem número de controle em {source_url}")
        if (
            str(actual_cnpj) != context["cnpj"]
            or not str(external_id).startswith(context["cnpj"] + "-")
        ):
            raise ValueError(f"Ata fora do órgão alvo em {source_url}")
        if str(actual_unit) != context["codigo_unidade"]:
            self.logger.event(
                "pncp_ata_scope_mismatch",
                external_id=str(external_id),
                expected_unit=context["codigo_unidade"],
                actual_unit=str(actual_unit),
                action="skipped_for_current_target",
            )
            return None
        return str(external_id)


class PublishedContractCollector:
    """Coleta contratos publicados por órgão/unidade do recorte estadual."""

    required_target_fields = ("cnpj", "codigo_unidade", "uf")
    control_number_pattern = re.compile(
        r"^(?P<cnpj>\d{14})-2-(?P<sequencial>\d+)/(?P<ano>\d{4})$"
    )

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.targets:
            raise ValueError("Fonte contrato sem unidades RAW configuradas")
        expected_uf = source.audit_context.get("uf")
        if not expected_uf:
            raise ValueError("Fonte contrato sem UF de auditoria")

        targets = list(
            enumerate(source.targets[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            targets = targets[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)

        def fetch(indexed_target):
            target_index, target = indexed_target
            context = self._target_context(target, str(expected_uf))
            page = 1
            found = []
            pages_requested = 0
            while True:
                query_unit = self._query_unit_code(
                    context["codigo_unidade"]
                )
                params = {
                    **source.params,
                    "cnpjOrgao": context["cnpj"],
                    "codigoUnidadeAdministrativa": query_unit,
                    source.page_param: page,
                    source.page_size_param: source.page_size,
                }
                url = self.client.build_url(
                    source.endpoint, params, base_url=source.base
                )
                pacer.wait()
                try:
                    response = self._request(source, params)
                    record_params = {
                        **params,
                        "codigoUnidadeAdministrativaOriginal": context[
                            "codigo_unidade"
                        ],
                        "consultaSemFiltroUnidade": False,
                    }
                except PNCPClientError as error:
                    if error.status_code != 422:
                        raise
                    fallback_params = dict(params)
                    fallback_params.pop("codigoUnidadeAdministrativa")
                    url = self.client.build_url(
                        source.endpoint,
                        fallback_params,
                        base_url=source.base,
                    )
                    self.logger.event(
                        "pncp_contract_unit_fallback",
                        source_id=source.id,
                        target_index=target_index,
                        cnpj=context["cnpj"],
                        codigo_unidade=context["codigo_unidade"],
                        codigo_unidade_consulta=query_unit,
                        page=page,
                        status_original=422,
                        action="retry_without_unit_filter",
                    )
                    pacer.wait()
                    response = self._request(source, fallback_params)
                    record_params = {
                        **fallback_params,
                        "codigoUnidadeAdministrativaOriginal": context[
                            "codigo_unidade"
                        ],
                        "consultaSemFiltroUnidade": True,
                    }
                pages_requested += 1
                records = (
                    []
                    if response == []
                    else records_from_response(response, source.item_path)
                )
                for payload in records:
                    external_id = self._validate_contract(
                        payload, context, url
                    )
                    if external_id is not None:
                        found.append(
                            (payload, external_id, url, record_params)
                        )
                if not records or _is_last_response_page(response, page):
                    break
                page += 1
            return target_index, context, found, pages_requested

        ordinal = 0
        for target_index, context, contracts, pages_requested in (
            _ordered_parallel_map(fetch, targets, source.max_concurrency)
        ):
            for payload, external_id, url, params in contracts:
                ordinal += 1
                yield CollectedRecord(
                    source.id,
                    payload,
                    url,
                    str(target_index),
                    ordinal,
                    external_id=external_id,
                    query_params={
                        **source.audit_context,
                        **params,
                        "target_index": target_index,
                    },
                )
            self.logger.event(
                "pncp_published_contracts",
                source_id=source.id,
                target_index=target_index,
                cnpj=context["cnpj"],
                codigo_unidade=context["codigo_unidade"],
                uf=context["uf"],
                pages_requested=pages_requested,
                contracts_count=len(contracts),
            )
            yield CollectionCheckpoint(str(target_index))

    def _target_context(self, target, expected_uf):
        missing = [
            field
            for field in self.required_target_fields
            if target.get(field) in (None, "")
        ]
        if missing:
            raise ValueError("Target de contrato incompleto: " + ", ".join(missing))
        cnpj = str(target["cnpj"])
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise ValueError("Target de contrato com CNPJ inválido")
        actual_uf = str(target["uf"])
        if actual_uf != expected_uf:
            raise ValueError(
                f"Unidade fora do recorte: esperado={expected_uf}, recebido={actual_uf}"
            )
        return {
            "cnpj": cnpj,
            "codigo_unidade": str(target["codigo_unidade"]),
            "uf": actual_uf,
        }

    def _request(self, source, params):
        return self.client.get(
            source.endpoint,
            params,
            base_url=source.base,
            timeout_seconds=source.timeout_seconds,
            headers=source.headers,
            max_retries=source.max_retries,
            retry_backoff_seconds=source.retry_backoff_seconds,
        )

    @staticmethod
    def _query_unit_code(unit_code: str) -> str:
        if len(unit_code) > 6 and unit_code.isdigit():
            return str(int(unit_code))
        return unit_code

    @staticmethod
    def _same_unit_code(actual: object, expected: str) -> bool:
        actual_text = str(actual)
        if actual_text == expected:
            return True
        if actual_text.isdigit() and expected.isdigit():
            return int(actual_text) == int(expected)
        return False

    def _validate_contract(self, payload, context, source_url):
        external_id = payload.get("numeroControlePNCP")
        match = self.control_number_pattern.fullmatch(str(external_id or ""))
        if not match:
            raise ValueError(f"Contrato sem número de controle válido em {source_url}")
        actual_cnpj = value_at_path(payload, "orgaoEntidade.cnpj")
        actual_unit = value_at_path(payload, "unidadeOrgao.codigoUnidade")
        actual_uf = value_at_path(payload, "unidadeOrgao.ufSigla")
        if (
            match.group("cnpj") != context["cnpj"]
            or str(actual_cnpj) != context["cnpj"]
            or str(actual_uf) != context["uf"]
        ):
            raise ValueError(f"Contrato fora do órgão/UF alvo em {source_url}")
        if not self._same_unit_code(actual_unit, context["codigo_unidade"]):
            self.logger.event(
                "pncp_contract_scope_mismatch",
                external_id=str(external_id),
                expected_unit=context["codigo_unidade"],
                actual_unit=str(actual_unit),
                action="skipped_for_current_target",
            )
            return None
        return str(external_id)


class CommitmentCollector:
    """Coleta empenhos paginados para os contratos preservados na RAW."""

    control_number_pattern = re.compile(
        r"^(?P<cnpj>\d{14})-2-(?P<sequencial>\d+)/(?P<ano>\d{4})$"
    )
    required_fields = ("cnpj", "ano", "sequencialContrato", "sequencialEmpenho")

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        if not source.targets:
            raise ValueError("Fonte empenho sem contratos RAW configurados")
        targets = list(
            enumerate(source.targets[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            targets = targets[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)

        def fetch(indexed_target):
            target_index, target = indexed_target
            context = self._target_context(target)
            endpoint = source.endpoint.format(**context)
            page = 1
            found = []
            pages_requested = 0
            while True:
                params = {
                    source.page_param: page,
                    source.page_size_param: source.page_size,
                }
                url = self.client.build_url(
                    endpoint, params, base_url=source.base
                )
                pacer.wait()
                response = self.client.get(
                    endpoint,
                    params,
                    base_url=source.base,
                    timeout_seconds=source.timeout_seconds,
                    headers=source.headers,
                    max_retries=source.max_retries,
                    retry_backoff_seconds=source.retry_backoff_seconds,
                    not_found_as_empty=True,
                )
                pages_requested += 1
                records = (
                    []
                    if response == []
                    else records_from_response(response, source.item_path)
                )
                for payload in records:
                    external_id = self._validate_commitment(
                        payload, context, url
                    )
                    found.append((payload, external_id, url, params))
                if not records or _is_last_response_page(response, page):
                    break
                page += 1
            return target_index, context, found, pages_requested

        ordinal = 0
        for target_index, context, commitments, pages_requested in (
            _ordered_parallel_map(fetch, targets, source.max_concurrency)
        ):
            for payload, external_id, url, params in commitments:
                ordinal += 1
                yield CollectedRecord(
                    source.id,
                    payload,
                    url,
                    str(target_index),
                    ordinal,
                    external_id=external_id,
                    query_params={
                        **source.audit_context,
                        **params,
                        "numeroControlePNCPContrato": context["numero_controle"],
                        "target_index": target_index,
                    },
                )
            self.logger.event(
                "pncp_commitments",
                source_id=source.id,
                target_index=target_index,
                numero_controle=context["numero_controle"],
                pages_requested=pages_requested,
                commitments_count=len(commitments),
            )
            yield CollectionCheckpoint(str(target_index))

    def _target_context(self, target):
        numero_controle = str(target.get("numero_controle") or "")
        match = self.control_number_pattern.fullmatch(numero_controle)
        if not match:
            raise ValueError("Target de empenho com contrato pai inválido")
        return {
            "cnpj": match.group("cnpj"),
            "ano": int(match.group("ano")),
            "sequencial": int(match.group("sequencial")),
            "numero_controle": numero_controle,
        }

    def _validate_commitment(self, payload, context, source_url):
        missing = [field for field in self.required_fields if payload.get(field) is None]
        if missing:
            raise ValueError(
                "Empenho sem identificador obrigatório: " + ", ".join(missing)
            )
        if (
            str(payload["cnpj"]) != context["cnpj"]
            or int(payload["ano"]) != context["ano"]
            or int(payload["sequencialContrato"]) != context["sequencial"]
        ):
            raise ValueError(f"Empenho fora do contrato alvo em {source_url}")
        return (
            f"{context['numero_controle']}|{int(payload['sequencialEmpenho'])}"
        )


class ContractTimelineCollector:
    """Coleta contratações por trimestre e modalidade com checkpoint composto."""

    external_id_field = "numeroControlePNCP"
    uf_field_path = "unidadeOrgao.ufSigla"

    def __init__(
        self, client: PNCPClient, logger: JsonlLogger | None = None
    ) -> None:
        self.client = client
        self.logger = logger or JsonlLogger()

    def collect(self, source: SourceConfig, start_page: int = 1):
        expected_uf = str(source.params.get("uf") or "")
        if not expected_uf:
            raise ValueError("Fonte histórica sem parâmetro uf")
        try:
            modalities = tuple(
                int(value) for value in source.params["modalidades"]
            )
        except (KeyError, TypeError, ValueError):
            raise ValueError(
                "Fonte histórica requer lista de modalidades"
            ) from None
        if not modalities or len(set(modalities)) != len(modalities):
            raise ValueError("Fonte histórica possui modalidades inválidas")
        windows = _quarter_date_windows(
            source.params.get("dataInicial"),
            source.params.get("dataFinal"),
        )
        work_items = [
            (window_index, window_start, window_end, modality)
            for window_index, (window_start, window_end) in enumerate(
                windows, start=1
            )
            for modality in modalities
        ]
        indexed_items = list(
            enumerate(work_items[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            indexed_items = indexed_items[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)
        base_params = {
            key: value
            for key, value in source.params.items()
            if key not in {"dataInicial", "dataFinal", "modalidades"}
        }
        ordinal = 0

        for work_index, work_item in indexed_items:
            window_index, window_start, window_end, modality = work_item
            page = 1
            pages_requested = 0
            records_count = 0
            while True:
                params = {
                    **base_params,
                    "dataInicial": window_start,
                    "dataFinal": window_end,
                    "codigoModalidadeContratacao": modality,
                    source.page_param: page,
                    source.page_size_param: source.page_size,
                }
                url = self.client.build_url(
                    source.endpoint, params, base_url=source.base
                )
                pacer.wait()
                response = self.client.get(
                    source.endpoint,
                    params,
                    base_url=source.base,
                    timeout_seconds=source.timeout_seconds,
                    headers=source.headers,
                    max_retries=source.max_retries,
                    retry_backoff_seconds=source.retry_backoff_seconds,
                )
                pages_requested += 1
                records = (
                    []
                    if response == []
                    else records_from_response(response, source.item_path)
                )
                for payload in records:
                    external_id = payload.get(self.external_id_field)
                    actual_uf = value_at_path(payload, self.uf_field_path)
                    if external_id in (None, ""):
                        raise ValueError(
                            f"Contratação sem numeroControlePNCP em {url}"
                        )
                    if actual_uf != expected_uf:
                        raise ValueError(
                            "Contratação fora do recorte estadual: "
                            f"esperado={expected_uf}, recebido={actual_uf}"
                        )
                    ordinal += 1
                    records_count += 1
                    yield CollectedRecord(
                        source.id,
                        payload,
                        url,
                        str(work_index),
                        ordinal,
                        external_id=str(external_id),
                        query_params={
                            **source.audit_context,
                            **params,
                            "ano": int(window_start[:4]),
                            "trimestre": (int(window_start[4:6]) - 1) // 3 + 1,
                            "window_index": window_index,
                            "work_index": work_index,
                        },
                    )
                if not records or _is_last_response_page(response, page):
                    break
                page += 1
            self.logger.event(
                "pncp_contract_timeline",
                source_id=source.id,
                work_index=work_index,
                window_index=window_index,
                window_start=window_start,
                window_end=window_end,
                modality=modality,
                pages_requested=pages_requested,
                records_count=records_count,
            )
            yield CollectionCheckpoint(str(work_index))


class ContractCollector(PNCPCollector):
    """Coleta contratações RAW e valida identidade e recorte estadual."""

    external_id_field = "numeroControlePNCP"
    uf_field_path = "unidadeOrgao.ufSigla"
    record_empty_pages = True

    def collect(self, source: SourceConfig, start_page: int = 1):
        expected_uf = source.params.get("uf")
        if not expected_uf:
            raise ValueError("Fonte de contratações sem parâmetro uf")

        for record in super().collect(source, start_page):
            if isinstance(record, CollectionCheckpoint):
                yield record
                continue

            external_id = record.payload.get(self.external_id_field)
            actual_uf = value_at_path(record.payload, self.uf_field_path)
            if external_id in (None, ""):
                self._inconsistency(
                    record, "missing_external_id", expected_uf, actual_uf
                )
                raise ValueError(
                    "Contratação sem numeroControlePNCP; coleta interrompida"
                )
            if actual_uf != expected_uf:
                self._inconsistency(
                    record, "unexpected_uf", expected_uf, actual_uf
                )
                raise ValueError(
                    "Contratação fora do recorte estadual: "
                    f"esperado={expected_uf}, recebido={actual_uf}"
                )
            yield replace(record, external_id=str(external_id))

    def _inconsistency(
        self,
        record: CollectedRecord,
        reason: str,
        expected_uf: Any,
        actual_uf: Any,
    ) -> None:
        self.logger.event(
            "pncp_contract_inconsistency",
            source_id=record.source_id,
            resource_type="contratacao",
            page=int(record.cursor),
            ordinal=record.ordinal,
            reason=reason,
            expected_uf=expected_uf,
            actual_uf=actual_uf,
        )


def _response_envelope_summary(response: Any) -> dict[str, Any]:
    if not isinstance(response, Mapping):
        return {"response_type": type(response).__name__}
    summary = {"response_keys": sorted(str(key) for key in response)}
    for key in (
        "totalRegistros",
        "totalPaginas",
        "numeroPagina",
        "paginasRestantes",
    ):
        if key in response:
            summary[key] = response[key]
    return summary


def _is_last_response_page(response: Any, current_page: int) -> bool:
    if not isinstance(response, Mapping):
        return False
    total_pages = response.get("totalPaginas")
    try:
        return total_pages is not None and current_page >= int(total_pages)
    except (TypeError, ValueError):
        return False


def _quarter_date_windows(
    initial_value: Any, final_value: Any
) -> tuple[tuple[str, str], ...]:
    """Divide um intervalo inclusivo em trimestres civis."""
    try:
        initial_text = str(initial_value)
        final_text = str(final_value)
        if len(initial_text) != 8 or len(final_text) != 8:
            raise ValueError
        initial = date.fromisoformat(
            f"{initial_text[:4]}-{initial_text[4:6]}-{initial_text[6:8]}"
        )
        final = date.fromisoformat(
            f"{final_text[:4]}-{final_text[4:6]}-{final_text[6:8]}"
        )
    except (TypeError, ValueError):
        raise ValueError(
            "Fonte histórica requer dataInicial e dataFinal em yyyyMMdd"
        ) from None
    if final < initial:
        raise ValueError("Fonte histórica possui intervalo de datas invertido")
    windows = []
    cursor = initial
    while cursor <= final:
        quarter_last_month = ((cursor.month - 1) // 3 + 1) * 3
        if quarter_last_month == 12:
            quarter_end = date(cursor.year, 12, 31)
        else:
            quarter_end = date(cursor.year, quarter_last_month + 1, 1) - timedelta(days=1)
        end = min(quarter_end, final)
        windows.append((cursor.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
        cursor = end + timedelta(days=1)
    return tuple(windows)


def _annual_date_windows(
    initial_value: Any, final_value: Any
) -> tuple[tuple[str, str], ...]:
    """Divide um intervalo inclusivo por ano civil (máximo 365 dias)."""
    try:
        initial = date.fromisoformat(
            f"{str(initial_value)[:4]}-{str(initial_value)[4:6]}-"
            f"{str(initial_value)[6:8]}"
        )
        final = date.fromisoformat(
            f"{str(final_value)[:4]}-{str(final_value)[4:6]}-"
            f"{str(final_value)[6:8]}"
        )
    except (TypeError, ValueError):
        raise ValueError(
            "Fonte de atas requer dataInicial e dataFinal em yyyyMMdd"
        ) from None
    if final < initial:
        raise ValueError("Fonte de atas possui intervalo de datas invertido")
    windows = []
    cursor = initial
    while cursor <= final:
        end = min(date(cursor.year, 12, 31), final)
        windows.append((cursor.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
        cursor = end + timedelta(days=1)
    return tuple(windows)


ResultT = TypeVar("ResultT")


class _RequestPacer:
    """Limita globalmente o início das chamadas feitas por várias threads."""

    def __init__(self, interval_seconds: float) -> None:
        self.interval_seconds = interval_seconds
        self._next_request_at = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        if not self.interval_seconds:
            return
        with self._lock:
            now = time.monotonic()
            delay = max(0.0, self._next_request_at - now)
            self._next_request_at = (
                max(now, self._next_request_at) + self.interval_seconds
            )
        if delay:
            time.sleep(delay)


def _ordered_parallel_map(
    function: Callable[[Any], ResultT],
    values: Iterable[Any],
    max_workers: int,
) -> Iterable[ResultT]:
    """Executa HTTP em paralelo e entrega resultados na ordem dos alvos."""
    if max_workers == 1:
        for value in values:
            yield function(value)
        return

    iterator = iter(values)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        pending = deque()
        for _ in range(max_workers):
            try:
                value = next(iterator)
            except StopIteration:
                break
            pending.append(executor.submit(function, value))

        while pending:
            yield pending.popleft().result()
            try:
                value = next(iterator)
            except StopIteration:
                continue
            pending.append(executor.submit(function, value))


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

        targets = list(
            enumerate(source.targets[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            targets = targets[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)

        def fetch(indexed_target):
            target_index, target = indexed_target
            context = self._target_context(target)
            endpoint = source.endpoint.format(**context)
            source_url = self.client.build_url(endpoint, base_url=source.base)
            pacer.wait()
            response = self.client.get(
                endpoint,
                base_url=source.base,
                timeout_seconds=source.timeout_seconds,
                headers=source.headers,
                max_retries=source.max_retries,
                retry_backoff_seconds=source.retry_backoff_seconds,
                not_found_as_empty=True,
            )
            return (
                target_index,
                context,
                source_url,
                records_from_response(response),
            )

        ordinal = 0
        for target_index, context, source_url, items in _ordered_parallel_map(
            fetch, targets, source.max_concurrency
        ):
            query_params = {
                **source.audit_context,
                "numeroControlePNCP": context["numero_controle"],
                "target_index": target_index,
            }
            for payload in items:
                numero_item = payload.get("numeroItem")
                if numero_item is None:
                    raise ValueError(
                        f"Item PNCP sem numeroItem em {source_url}"
                    )
                ordinal += 1
                yield CollectedRecord(
                    source.id,
                    payload,
                    source_url,
                    str(target_index),
                    ordinal,
                    external_id=(
                        f"{context['numero_controle']}|{numero_item}"
                    ),
                    query_params=query_params,
                )

            self.logger.event(
                "pncp_purchase_items",
                source_id=source.id,
                target_index=target_index,
                numero_controle=context["numero_controle"],
                items_count=len(items),
            )
            yield CollectionCheckpoint(str(target_index))

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

        targets = list(
            enumerate(source.targets[start_page - 1 :], start=start_page)
        )
        if source.max_pages is not None:
            targets = targets[: source.max_pages]
        pacer = _RequestPacer(source.rate_limit_seconds)

        def fetch(indexed_target):
            target_index, target = indexed_target
            context = self._target_context(target)
            requested = target.get("tem_resultado") is not False
            if not requested:
                return target_index, context, False, None, []
            endpoint = source.endpoint.format(**context)
            source_url = self.client.build_url(endpoint, base_url=source.base)
            pacer.wait()
            response = self.client.get(
                endpoint,
                base_url=source.base,
                timeout_seconds=source.timeout_seconds,
                headers=source.headers,
                max_retries=source.max_retries,
                retry_backoff_seconds=source.retry_backoff_seconds,
                not_found_as_empty=True,
            )
            return (
                target_index,
                context,
                True,
                source_url,
                records_from_response(response),
            )

        ordinal = 0
        for (
            target_index,
            context,
            requested,
            result_url,
            results,
        ) in _ordered_parallel_map(fetch, targets, source.max_concurrency):
            query_params = {
                **source.audit_context,
                "numeroControlePNCP": context["numero_controle"],
                "numeroItem": context["numeroItem"],
                "target_index": target_index,
            }
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
                    query_params=query_params,
                )

            self.logger.event(
                "pncp_item_results",
                source_id=source.id,
                target_index=target_index,
                numero_controle=context["numero_controle"],
                numero_item=context["numeroItem"],
                requested=requested,
                results_count=len(results),
            )
            yield CollectionCheckpoint(str(target_index))

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
