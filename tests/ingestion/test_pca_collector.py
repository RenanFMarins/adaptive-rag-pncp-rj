import unittest

from src.ingestion.pncp_collector import PCACollector
from src.schema import SourceConfig


class FakePNCPClient:
    def __init__(self):
        self.pages = {
            1: {"data": [{"idPcaPncp": "pca-1", "valor": 10}]},
            2: {"data": [{"idPcaPncp": "pca-2", "valor": 20}]},
            3: {"data": []},
        }

    def fetch_page(self, source, page):
        return self.pages[page], f"{source.url}?pagina={page}"


class PCACollectorTests(unittest.TestCase):
    def source(self):
        return SourceConfig(
            id="pncp_pca_rj",
            base="https://pncp.example",
            endpoint="/api/consulta/v1/pca/atualizacao",
            resource_type="pca",
            item_path="data",
            key_fields=("idPcaPncp",),
        )

    def test_collects_data_page_by_page_without_normalizing_payload(self):
        records = list(PCACollector(FakePNCPClient()).collect(self.source()))

        self.assertEqual([record.cursor for record in records], ["1", "2"])
        self.assertEqual(
            records[0].payload, {"idPcaPncp": "pca-1", "valor": 10}
        )
        self.assertEqual(records[1].payload["idPcaPncp"], "pca-2")

    def test_rejects_pca_record_without_primary_identifier(self):
        client = FakePNCPClient()
        client.pages[1] = {"data": [{"valor": 10}]}

        with self.assertRaises(ValueError):
            list(PCACollector(client).collect(self.source()))


if __name__ == "__main__":
    unittest.main()
