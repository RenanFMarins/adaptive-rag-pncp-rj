import unittest

from src.fetch_corpus import resolve_source_targets
from src.ingestion.pncp_collector import ItemResultCollector
from src.schema import SourceConfig


class FakePNCPClient:
    def __init__(self):
        self.requested = []

    def build_url(self, endpoint, params=None, base_url=None):
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None, **kwargs):
        self.requested.append(endpoint)
        if endpoint.endswith("/itens"):
            return [
                {"numeroItem": 1, "temResultado": True},
                {"numeroItem": 2, "temResultado": False},
            ]
        return [
            {
                "numeroControlePNCPCompra": "12345678000199-1-000001/2025",
                "numeroItem": 1,
                "sequencialResultado": 1,
                "quantidadeHomologada": 2.0,
                "valorUnitarioHomologado": 10.0,
                "valorTotalHomologado": 20.0,
                "campoOriginal": "preservado",
            }
        ]


class ItemResultCollectorTests(unittest.TestCase):
    def source(self):
        return SourceConfig(
            id="pncp_resultado_item_rj",
            base="https://pncp.example",
            endpoint=(
                "/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}"
                "/itens/{numeroItem}/resultados"
            ),
            collector="pncp_item_results",
            natureza="agregada",
            resource_type="resultado_item",
            targets=(
                {"cnpj": "12345678000199", "ano": 2025, "sequencial": 1},
            ),
            items_endpoint_template=(
                "/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"
            ),
            key_fields=(
                "numeroControlePNCPCompra",
                "numeroItem",
                "sequencialResultado",
            ),
        )

    def test_collects_only_available_results_and_preserves_payload(self):
        client = FakePNCPClient()

        records = list(ItemResultCollector(client).collect(self.source()))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].payload["campoOriginal"], "preservado")
        self.assertEqual(records[0].payload["valorTotalHomologado"], 20.0)
        self.assertEqual(records[0].cursor, "1")
        self.assertEqual(len(client.requested), 2)
        self.assertIn("/itens/1/resultados", client.requested[1])

    def test_paginates_purchase_items(self):
        client = FakePNCPClient()
        calls = []

        def paginated_get(endpoint, params=None, **kwargs):
            if endpoint.endswith("/itens"):
                calls.append(params)
                if params["pagina"] == 1:
                    return [{"numeroItem": 1, "temResultado": False}]
                return []
            raise AssertionError("Não deveria consultar resultados")

        client.get = paginated_get
        source = SourceConfig(
            **{**self.source().__dict__, "items_page_size": 1}
        )

        records = list(ItemResultCollector(client).collect(source))

        self.assertEqual(records, [])
        self.assertEqual(
            calls,
            [
                {"pagina": 1, "tamanhoPagina": 1},
                {"pagina": 2, "tamanhoPagina": 1},
            ],
        )

    def test_rejects_result_without_composite_identifier(self):
        client = FakePNCPClient()
        original_get = client.get

        def incomplete_result(endpoint, params=None, **kwargs):
            if endpoint.endswith("/itens"):
                return original_get(endpoint, params, **kwargs)
            return [{"numeroItem": 1, "sequencialResultado": 1}]

        client.get = incomplete_result

        with self.assertRaisesRegex(ValueError, "numeroControlePNCPCompra"):
            list(ItemResultCollector(client).collect(self.source()))

    def test_rejects_invalid_target_cnpj(self):
        source = self.source()
        invalid = SourceConfig(
            **{
                **source.__dict__,
                "targets": ({"cnpj": "123", "ano": 2025, "sequencial": 1},),
            }
        )

        with self.assertRaisesRegex(ValueError, "CNPJ inválido"):
            list(ItemResultCollector(FakePNCPClient()).collect(invalid))

    def test_structured_raw_replaces_manual_target(self):
        class FakeRepository:
            def latest_payloads(self, source_id, resource_type):
                self.lookup = (source_id, resource_type)
                return [
                    {
                        "orgaoEntidade": {"cnpj": "98765432000199"},
                        "anoCompra": 2026,
                        "sequencialCompra": 42,
                    }
                ]

        source = SourceConfig(
            **{
                **self.source().__dict__,
                "target_source_id": "pncp_contratacoes_rj",
                "target_resource_type": "contratacao",
                "target_field_paths": {
                    "cnpj": "orgaoEntidade.cnpj",
                    "ano": "anoCompra",
                    "sequencial": "sequencialCompra",
                },
            }
        )
        repository = FakeRepository()

        resolved = resolve_source_targets(repository, source)

        self.assertEqual(
            resolved.targets,
            ({"cnpj": "98765432000199", "ano": 2026, "sequencial": 42},),
        )
        self.assertEqual(
            repository.lookup, ("pncp_contratacoes_rj", "contratacao")
        )


if __name__ == "__main__":
    unittest.main()
