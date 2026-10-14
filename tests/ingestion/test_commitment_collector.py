import unittest

from src.ingestion.pncp_collector import CommitmentCollector
from src.schema import CollectionCheckpoint, CollectedRecord, SourceConfig


class FakePNCPClient:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def build_url(self, endpoint, params=None, base_url=None):
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None, **kwargs):
        self.requests.append((endpoint, dict(params or {}), kwargs))
        return self.response


class FakeLogger:
    def __init__(self):
        self.events = []

    def event(self, event, **fields):
        self.events.append((event, fields))


class CommitmentCollectorTests(unittest.TestCase):
    CNPJ = "12345678000199"
    CONTRACT = "12345678000199-2-000007/2023"

    def source(self):
        return SourceConfig(
            id="pncp_empenhos_contratos_rj_2023_t1",
            base="https://pncp.example",
            endpoint=(
                "/api/pncp/v1/orgaos/{cnpj}/contratos/{ano}/"
                "{sequencial}/empenhos"
            ),
            collector="pncp_commitments",
            resource_type="empenho",
            targets=({"numero_controle": self.CONTRACT},),
            audit_context={"uf": "RJ", "ano_publicacao": 2023},
            item_path="data",
            page_size=50,
            max_concurrency=1,
            key_fields=("cnpj", "ano", "sequencialContrato", "sequencialEmpenho"),
        )

    def commitment(self, sequence=3):
        return {
            "cnpj": self.CNPJ,
            "ano": 2023,
            "sequencialContrato": 7,
            "sequencialEmpenho": sequence,
            "numeroEmpenho": "2023NE000001",
            "valorTotal": 125.50,
            "campoExtra": {"preservado": True},
        }

    def test_collects_commitment_and_preserves_parent_identity(self):
        payload = self.commitment()
        client = FakePNCPClient({"data": [payload], "totalPaginas": 1})

        collected = list(CommitmentCollector(client).collect(self.source()))
        records = [item for item in collected if isinstance(item, CollectedRecord)]

        self.assertEqual(len(records), 1)
        self.assertIs(records[0].payload, payload)
        self.assertEqual(records[0].external_id, f"{self.CONTRACT}|3")
        self.assertEqual(records[0].query_params["numeroControlePNCPContrato"], self.CONTRACT)
        self.assertTrue(client.requests[0][0].endswith("/2023/7/empenhos"))
        self.assertTrue(client.requests[0][2]["not_found_as_empty"])
        self.assertEqual(collected[-1], CollectionCheckpoint("1"))

    def test_no_commitments_still_advances_checkpoint(self):
        collected = list(CommitmentCollector(FakePNCPClient([])).collect(self.source()))

        self.assertEqual(collected, [CollectionCheckpoint("1")])

    def test_rejects_commitment_from_another_contract(self):
        payload = self.commitment()
        payload["sequencialContrato"] = 8
        client = FakePNCPClient({"data": [payload], "totalPaginas": 1})

        with self.assertRaisesRegex(ValueError, "fora do contrato alvo"):
            list(CommitmentCollector(client).collect(self.source()))

    def test_queries_abnormal_parent_year_without_changing_identity(self):
        malformed_contract = f"{self.CNPJ}-2-000007/20024"
        source = self.source()
        source = SourceConfig(
            **{
                **source.__dict__,
                "targets": ({"numero_controle": malformed_contract},),
            }
        )
        client = FakePNCPClient([])
        logger = FakeLogger()

        collected = list(CommitmentCollector(client, logger=logger).collect(source))

        self.assertEqual(collected, [CollectionCheckpoint("1")])
        self.assertTrue(client.requests[0][0].endswith("/20024/7/empenhos"))
        self.assertEqual(
            logger.events[0][0],
            "pncp_commitment_parent_control_number_anomaly",
        )
        self.assertEqual(logger.events[0][1]["control_year"], "20024")
        self.assertEqual(logger.events[0][1]["action"], "queried_as_received")


if __name__ == "__main__":
    unittest.main()
