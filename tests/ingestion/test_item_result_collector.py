import unittest

from src.fetch_corpus import resolve_source_targets
from src.ingestion.pncp_client import PNCPClientError
from src.ingestion.pncp_collector import ItemResultCollector
from src.schema import (
    CollectionCheckpoint,
    CollectionFailure,
    CollectedRecord,
    SourceConfig,
)


class FakePNCPClient:
    def __init__(self):
        self.requested = []
        self.request_options = []

    def build_url(self, endpoint, params=None, base_url=None):
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None, **kwargs):
        self.requested.append(endpoint)
        self.request_options.append(kwargs)
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
                {
                    "numero_controle": "12345678000199-1-000001/2025",
                    "numero_item": 1,
                    "tem_resultado": True,
                },
                {
                    "numero_controle": "12345678000199-1-000001/2025",
                    "numero_item": 2,
                    "tem_resultado": False,
                },
            ),
            key_fields=(
                "numeroControlePNCPCompra",
                "numeroItem",
                "sequencialResultado",
            ),
        )

    def test_uses_raw_items_and_preserves_result_payload(self):
        client = FakePNCPClient()

        collected = list(ItemResultCollector(client).collect(self.source()))
        records = [item for item in collected if isinstance(item, CollectedRecord)]
        checkpoints = [
            item for item in collected if isinstance(item, CollectionCheckpoint)
        ]

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].payload["campoOriginal"], "preservado")
        self.assertEqual(records[0].payload["valorTotalHomologado"], 20.0)
        self.assertEqual(
            records[0].external_id,
            "12345678000199-1-000001/2025|1|1",
        )
        self.assertEqual([item.cursor for item in checkpoints], ["1", "2"])
        self.assertEqual(len(client.requested), 1)
        self.assertIn("/itens/1/resultados", client.requested[0])
        self.assertNotIn("/itens?", client.requested[0])
        self.assertTrue(client.request_options[0]["not_found_as_empty"])

    def test_item_without_result_does_not_call_api_but_advances_target(self):
        client = FakePNCPClient()
        source = SourceConfig(
            **{**self.source().__dict__, "targets": (self.source().targets[1],)}
        )

        collected = list(ItemResultCollector(client).collect(source))

        self.assertEqual(client.requested, [])
        self.assertEqual(len(collected), 1)
        self.assertIsInstance(collected[0], CollectionCheckpoint)
        self.assertEqual(collected[0].cursor, "1")
        self.assertEqual(
            collected[0].target_key,
            "12345678000199-1-000001/2025|2",
        )

    def test_request_failure_is_deferred_and_next_target_continues(self):
        client = FakePNCPClient()

        def fail_first_target(endpoint, params=None, **kwargs):
            client.requested.append(endpoint)
            if "/itens/1/resultados" in endpoint:
                raise PNCPClientError("timeout")
            return [
                {
                    "numeroControlePNCPCompra": (
                        "12345678000199-1-000001/2025"
                    ),
                    "numeroItem": 2,
                    "sequencialResultado": 1,
                }
            ]

        client.get = fail_first_target
        source = SourceConfig(
            **{
                **self.source().__dict__,
                "targets": (
                    self.source().targets[0],
                    {
                        **self.source().targets[1],
                        "tem_resultado": True,
                    },
                ),
            }
        )

        collected = list(ItemResultCollector(client).collect(source))

        failures = [
            item for item in collected if isinstance(item, CollectionFailure)
        ]
        records = [
            item for item in collected if isinstance(item, CollectedRecord)
        ]
        checkpoints = [
            item
            for item in collected
            if isinstance(item, CollectionCheckpoint)
        ]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].cursor, "1")
        self.assertEqual(
            failures[0].target_key,
            "12345678000199-1-000001/2025|1",
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].cursor, "2")
        self.assertEqual([item.cursor for item in checkpoints], ["2"])

    def test_pending_target_preserves_original_cursor(self):
        target = {
            **self.source().targets[0],
            "_cursor": 508999,
            "_target_key": "pending-target",
        }
        source = SourceConfig(
            **{**self.source().__dict__, "targets": (target,)}
        )

        collected = list(
            ItemResultCollector(FakePNCPClient()).collect(source)
        )

        self.assertEqual(collected[-1].cursor, "508999")
        self.assertEqual(collected[-1].target_key, "pending-target")

    def test_rejects_result_without_composite_identifier(self):
        client = FakePNCPClient()

        def incomplete_result(endpoint, params=None, **kwargs):
            return [{"numeroItem": 1, "sequencialResultado": 1}]

        client.get = incomplete_result

        with self.assertRaisesRegex(ValueError, "numeroControlePNCPCompra"):
            list(ItemResultCollector(client).collect(self.source()))

    def test_rejects_invalid_parent_control_number(self):
        source = SourceConfig(
            **{
                **self.source().__dict__,
                "targets": (
                    {
                        "numero_controle": "invalido",
                        "numero_item": 1,
                        "tem_resultado": True,
                    },
                ),
            }
        )

        with self.assertRaisesRegex(ValueError, "pai inválido"):
            list(ItemResultCollector(FakePNCPClient()).collect(source))

    def test_raw_item_metadata_resolves_result_target(self):
        class FakeRepository:
            def latest_assets(self, source_id, resource_type):
                self.lookup = (source_id, resource_type)
                return [
                    {
                        "external_id": (
                            "98765432000199-1-000042/2026|7"
                        ),
                        "payload": {"numeroItem": 7, "temResultado": True},
                    }
                ]

        source = SourceConfig(
            **{
                **self.source().__dict__,
                "targets": (),
                "target_source_id": "pncp_itens_contratacao_rj",
                "target_resource_type": "contratacao_item",
                "target_field_paths": {
                    "numero_controle": "@parent_external_id",
                    "numero_item": "numeroItem",
                    "tem_resultado": "temResultado",
                },
            }
        )
        repository = FakeRepository()

        resolved = resolve_source_targets(repository, source)

        self.assertEqual(
            resolved.targets,
            (
                {
                    "numero_controle": "98765432000199-1-000042/2026",
                    "numero_item": 7,
                    "tem_resultado": True,
                },
            ),
        )
        self.assertEqual(
            repository.lookup,
            ("pncp_itens_contratacao_rj", "contratacao_item"),
        )

    def test_targets_from_multiple_sources_are_sorted_and_deduplicated(self):
        class FakeRepository:
            def latest_assets(self, source_id, resource_type):
                values = {
                    "m04": [
                        {"external_id": "compra-b", "payload": {"id": "b"}},
                    ],
                    "m06": [
                        {"external_id": "compra-a", "payload": {"id": "a"}},
                        {"external_id": "compra-b", "payload": {"id": "b"}},
                    ],
                }
                return values[source_id]

        source = SourceConfig(
            id="itens_completos",
            base="https://pncp.example",
            endpoint="/itens",
            target_source_ids=("m04", "m06"),
            target_resource_type="contratacao",
            target_field_paths={"numero_controle": "@external_id"},
        )

        resolved = resolve_source_targets(FakeRepository(), source)

        self.assertEqual(
            resolved.targets,
            (
                {"numero_controle": "compra-a"},
                {"numero_controle": "compra-b"},
            ),
        )


if __name__ == "__main__":
    unittest.main()
