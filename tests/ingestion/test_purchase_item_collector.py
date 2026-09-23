import unittest

from src.ingestion.pncp_collector import PurchaseItemCollector
from src.schema import CollectionCheckpoint, CollectedRecord, SourceConfig


class FakePNCPClient:
    def __init__(self):
        self.requests = []

    def build_url(self, endpoint, params=None, base_url=None):
        page = params.get("pagina") if params else None
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}?pagina={page}"

    def get(self, endpoint, params=None, **kwargs):
        self.requests.append((endpoint, params))
        return [
            {
                "numeroItem": 1,
                "descricao": "Serviço preservado",
                "quantidade": 2,
                "temResultado": True,
            }
        ]


class PurchaseItemCollectorTests(unittest.TestCase):
    def source(self):
        return SourceConfig(
            id="pncp_itens_contratacao_rj",
            base="https://pncp.example",
            endpoint=(
                "/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"
            ),
            collector="pncp_purchase_items",
            resource_type="contratacao_item",
            targets=(
                {
                    "cnpj": "12345678000199",
                    "ano": 2026,
                    "sequencial": 7,
                    "numero_controle": "12345678000199-1-000007/2026",
                },
            ),
            key_fields=("numeroItem",),
        )

    def test_preserves_payload_and_builds_parent_scoped_external_id(self):
        collected = list(
            PurchaseItemCollector(FakePNCPClient()).collect(self.source())
        )
        records = [item for item in collected if isinstance(item, CollectedRecord)]

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].payload["descricao"], "Serviço preservado")
        self.assertEqual(
            records[0].external_id,
            "12345678000199-1-000007/2026|1",
        )
        self.assertEqual(records[0].cursor, "1")
        self.assertEqual(collected[-1], CollectionCheckpoint("1"))

    def test_empty_target_still_emits_checkpoint(self):
        client = FakePNCPClient()
        client.get = lambda *args, **kwargs: []

        collected = list(PurchaseItemCollector(client).collect(self.source()))

        self.assertEqual(collected, [CollectionCheckpoint("1")])

    def test_rejects_target_without_parent_control_number(self):
        source = self.source()
        incomplete = SourceConfig(
            **{
                **source.__dict__,
                "targets": (
                    {"cnpj": "12345678000199", "ano": 2026, "sequencial": 7},
                ),
            }
        )

        with self.assertRaisesRegex(ValueError, "numero_controle"):
            list(PurchaseItemCollector(FakePNCPClient()).collect(incomplete))


if __name__ == "__main__":
    unittest.main()
