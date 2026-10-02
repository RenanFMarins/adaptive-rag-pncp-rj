import unittest

from src.ingestion.pncp_collector import PublishedContractCollector
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

    def test_skips_contract_outside_target_unit(self):
        contract = self.contract(unit="999999")
        client = FakePNCPClient({1: {"data": [contract], "totalPaginas": 1}})

        collected = list(PublishedContractCollector(client).collect(self.source()))

        self.assertEqual(collected, [CollectionCheckpoint("1")])

    def test_rejects_contract_outside_target_state(self):
        contract = self.contract(uf="SP")
        client = FakePNCPClient({1: {"data": [contract], "totalPaginas": 1}})

        with self.assertRaisesRegex(ValueError, "fora do órgão/UF"):
            list(PublishedContractCollector(client).collect(self.source()))


if __name__ == "__main__":
    unittest.main()
