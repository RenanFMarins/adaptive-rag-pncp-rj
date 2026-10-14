import unittest

from src.ingestion.pncp_collector import PublishedContractCollector
from src.ingestion.pncp_client import PNCPClientError
from src.schema import CollectionCheckpoint, CollectedRecord, SourceConfig


class FakePNCPClient:
    def __init__(self, pages):
        self.pages = pages
        self.requests = []

    def build_url(self, endpoint, params=None, base_url=None):
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None, **kwargs):
        self.requests.append((endpoint, dict(params or {})))
        return self.pages[params["pagina"]]


class FallbackPNCPClient(FakePNCPClient):
    def __init__(self, fallback_response):
        super().__init__({})
        self.fallback_response = fallback_response

    def get(self, endpoint, params=None, **kwargs):
        self.requests.append((endpoint, dict(params or {})))
        if "codigoUnidadeAdministrativa" in params:
            raise PNCPClientError("HTTP 422", status_code=422)
        return self.fallback_response


class FakeLogger:
    def __init__(self):
        self.events = []

    def event(self, event, **fields):
        self.events.append((event, fields))


class PublishedContractCollectorTests(unittest.TestCase):
    CNPJ = "12345678000199"
    UNIT = "000001"

    def source(self, targets=None):
        return SourceConfig(
            id="pncp_contratos_rj_2023_t1",
            base="https://pncp.example",
            endpoint="/api/consulta/v1/contratos",
            collector="pncp_published_contracts",
            resource_type="contrato",
            params={"dataInicial": "20230101", "dataFinal": "20230331"},
            audit_context={"uf": "RJ", "ano_publicacao": 2023},
            targets=targets or ({
                "cnpj": self.CNPJ,
                "codigo_unidade": self.UNIT,
                "uf": "RJ",
            },),
            item_path="data",
            page_size=50,
            max_concurrency=1,
            key_fields=("numeroControlePNCP",),
        )

    def contract(self, sequence=1, uf="RJ", unit=None):
        return {
            "numeroControlePNCP": f"{self.CNPJ}-2-{sequence:06d}/2023",
            "orgaoEntidade": {"cnpj": self.CNPJ, "razaoSocial": "Órgão"},
            "unidadeOrgao": {
                "codigoUnidade": unit or self.UNIT,
                "ufSigla": uf,
            },
            "campoExtra": {"preservado": True},
        }

    def test_paginates_and_preserves_complete_payload(self):
        first = self.contract(1)
        second = self.contract(2)
        client = FakePNCPClient({
            1: {"data": [first], "totalPaginas": 2, "numeroPagina": 1},
            2: {"data": [second], "totalPaginas": 2, "numeroPagina": 2},
        })

        collected = list(PublishedContractCollector(client).collect(self.source()))
        records = [item for item in collected if isinstance(item, CollectedRecord)]

        self.assertEqual([request[1]["pagina"] for request in client.requests], [1, 2])
        self.assertEqual([record.payload for record in records], [first, second])
        self.assertEqual(records[0].external_id, f"{self.CNPJ}-2-000001/2023")
        self.assertEqual(records[0].query_params["codigoUnidadeAdministrativa"], self.UNIT)
        self.assertEqual(records[0].query_params["uf"], "RJ")
        self.assertEqual(collected[-1], CollectionCheckpoint("1"))

    def test_empty_target_still_advances_checkpoint(self):
        client = FakePNCPClient({1: {"data": [], "totalPaginas": 0}})

        collected = list(PublishedContractCollector(client).collect(self.source()))

        self.assertEqual(collected, [CollectionCheckpoint("1")])

    def test_normalizes_numeric_unit_code_for_the_request(self):
        client = FakePNCPClient({
            1: {"data": [], "totalPaginas": 0},
        })
        source = self.source(targets=({
            "cnpj": self.CNPJ,
            "codigo_unidade": "000000001",
            "uf": "RJ",
        },))

        collected = list(PublishedContractCollector(client).collect(source))

        self.assertEqual(collected, [CollectionCheckpoint("1")])
        self.assertEqual(
            client.requests[0][1]["codigoUnidadeAdministrativa"], "1"
        )

    def test_falls_back_without_unit_filter_after_http_422(self):
        contract = self.contract()
        client = FallbackPNCPClient({
            "data": [contract],
            "totalPaginas": 1,
            "numeroPagina": 1,
        })

        collected = list(PublishedContractCollector(client).collect(self.source()))
        records = [item for item in collected if isinstance(item, CollectedRecord)]

        self.assertEqual(len(client.requests), 2)
        self.assertIn("codigoUnidadeAdministrativa", client.requests[0][1])
        self.assertNotIn("codigoUnidadeAdministrativa", client.requests[1][1])
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0].query_params["consultaSemFiltroUnidade"])
        self.assertEqual(
            records[0].query_params["codigoUnidadeAdministrativaOriginal"],
            self.UNIT,
        )

    def test_skips_contract_outside_target_unit(self):
        contract = self.contract(unit="999999")
        client = FakePNCPClient({1: {"data": [contract], "totalPaginas": 1}})

        collected = list(PublishedContractCollector(client).collect(self.source()))

        self.assertEqual(collected, [CollectionCheckpoint("1")])

    def test_skips_and_audits_contract_outside_target_state(self):
        contract = self.contract(uf="SP")
        client = FakePNCPClient({1: {"data": [contract], "totalPaginas": 1}})
        logger = FakeLogger()

        collected = list(
            PublishedContractCollector(client, logger=logger).collect(self.source())
        )

        self.assertEqual(collected, [CollectionCheckpoint("1")])
        self.assertEqual(logger.events[0][0], "pncp_contract_scope_mismatch")
        self.assertEqual(logger.events[0][1]["expected_uf"], "RJ")
        self.assertEqual(logger.events[0][1]["actual_uf"], "SP")
        self.assertEqual(
            logger.events[0][1]["action"], "skipped_for_current_target"
        )

    def test_preserves_and_audits_contract_with_abnormal_year(self):
        contract = self.contract()
        malformed_id = f"{self.CNPJ}-2-000001/20024"
        contract["numeroControlePNCP"] = malformed_id
        contract["anoContrato"] = 20024
        client = FakePNCPClient({
            1: {"data": [contract], "totalPaginas": 1, "numeroPagina": 1},
        })
        logger = FakeLogger()

        collected = list(
            PublishedContractCollector(client, logger=logger).collect(self.source())
        )
        records = [item for item in collected if isinstance(item, CollectedRecord)]

        self.assertEqual(len(records), 1)
        self.assertIs(records[0].payload, contract)
        self.assertEqual(records[0].external_id, malformed_id)
        anomaly = next(
            fields
            for event, fields in logger.events
            if event == "pncp_contract_control_number_anomaly"
        )
        self.assertEqual(anomaly["control_year"], "20024")
        self.assertEqual(anomaly["payload_year"], "20024")
        self.assertEqual(anomaly["action"], "preserved_raw")


if __name__ == "__main__":
    unittest.main()
