import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.ingestion.incremental_runner import (
    IncrementalConfigurationError,
    IncrementalRunConfig,
)
from src.ingestion.online_pilot import (
    run_online_operational,
    run_online_pilot,
)
from src.ingestion.scope_inventory import OrganizationUnit, ScopeInventory


class OnlinePilotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "pilot.db"
        self.member = OrganizationUnit(
            "12345678000199", "000001", "RJ"
        )
        inventory = ScopeInventory("RJ", (self.member,))
        self.inventory_path = Path(self.temporary.name) / "inventory.json"
        self.inventory_path.write_text(
            json.dumps(
                {
                    "scope": {
                        "uf": "RJ",
                        "inventory_id": inventory.inventory_id,
                        "members": [self.member.target],
                    },
                    "coverage_plans": {
                        "contrato": {
                            "name": "pncp-rj-contrato-inventario",
                            "inventory_id": inventory.inventory_id,
                            "member_count": 1,
                        },
                        "pca": {
                            "name": "pncp-rj-pca-inventario",
                            "inventory_id": inventory.inventory_id,
                            "member_count": 1,
                        },
                        "ata_registro_preco": {
                            "name": "pncp-rj-ata-inventario",
                            "inventory_id": inventory.inventory_id,
                            "member_count": 1,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def config(self, **changes):
        values = {
            "resource": "contratacao",
            "start_date": "2023-04-01",
            "end_date": "2023-04-01",
            "uf": "RJ",
            "modality": 6,
            "database_url": f"sqlite:///{self.database}",
        }
        values.update(changes)
        return IncrementalRunConfig(**values)

    def test_rejects_broad_or_out_of_scope_online_execution(self):
        invalid = (
            (self.config(end_date="2023-04-02"), "um dia"),
            (self.config(uf="SP"), "UF RJ"),
            (self.config(modality=15), "entre 1 e 14"),
            (
                self.config(resource="empenho"),
                "contratacao, contrato, pca, ata_registro_preco e "
                "contratacao_item",
            ),
        )
        for config, message in invalid:
            with self.subTest(message=message), self.assertRaisesRegex(
                IncrementalConfigurationError, message
            ):
                run_online_pilot(config)

    @patch("src.ingestion.online_pilot.run_adapter_incremental")
    def test_builds_real_transport_plan_but_delegates_safety_to_runner(
        self, run_adapter
    ):
        sentinel = object()
        run_adapter.return_value = sentinel

        result = run_online_pilot(self.config())

        self.assertIs(result, sentinel)
        config, plan = run_adapter.call_args.args
        self.assertEqual(
            config.job_name,
            "pncp_incremental_pilot_contratacao_rj_m06",
        )
        self.assertEqual(
            plan.endpoint,
            "/api/consulta/v1/contratacoes/atualizacao",
        )
        self.assertEqual(
            plan.filters,
            {"codigoModalidadeContratacao": 6, "uf": "RJ"},
        )

    @patch("src.ingestion.online_pilot.run_adapter_incremental")
    def test_builds_contract_plan_from_frozen_inventory(self, run_adapter):
        sentinel = object()
        run_adapter.return_value = sentinel
        config = self.config(
            resource="contrato",
            modality=None,
            organization_cnpj=self.member.cnpj,
            unit_code=self.member.unit_code,
            scope_inventory_path=self.inventory_path,
        )

        result = run_online_pilot(config)

        self.assertIs(result, sentinel)
        prepared, plan = run_adapter.call_args.args
        self.assertEqual(
            prepared.job_name,
            "pncp_incremental_pilot_contrato_rj_"
            "12345678000199_000001",
        )
        self.assertEqual(
            prepared.coverage_member,
            "orgao-unidade:12345678000199:000001",
        )
        self.assertEqual(
            prepared.coverage_name, "pncp-rj-contrato-inventario"
        )
        self.assertEqual(
            plan.endpoint, "/api/consulta/v1/contratos/atualizacao"
        )
        self.assertEqual(
            plan.filters,
            {
                "cnpjOrgao": "12345678000199",
                "codigoUnidadeAdministrativa": "000001",
            },
        )
        self.assertNotIn("uf", plan.filters)

    def test_rejects_contract_outside_frozen_inventory(self):
        invalid = (
            (
                self.config(
                    resource="contrato",
                    modality=None,
                    scope_inventory_path=self.inventory_path,
                ),
                "CNPJ inválido",
            ),
            (
                self.config(
                    resource="contrato",
                    modality=6,
                    organization_cnpj=self.member.cnpj,
                    unit_code=self.member.unit_code,
                    scope_inventory_path=self.inventory_path,
                ),
                "não aceita modalidade",
            ),
            (
                self.config(
                    resource="contrato",
                    modality=None,
                    organization_cnpj="99999999000199",
                    unit_code="000001",
                    scope_inventory_path=self.inventory_path,
                ),
                "não pertence ao inventário",
            ),
        )
        for config, message in invalid:
            with self.subTest(message=message), self.assertRaisesRegex(
                IncrementalConfigurationError, message
            ):
                run_online_pilot(config)

    @patch("src.ingestion.online_pilot.run_adapter_incremental")
    @patch("src.ingestion.online_pilot.PNCPPCAIncrementalAdapter.collect")
    def test_builds_pca_plan_from_frozen_inventory(
        self, collect, run_adapter
    ):
        sentinel = object()
        run_adapter.return_value = sentinel
        collect.return_value = iter(())
        config = self.config(
            resource="pca",
            modality=None,
            organization_cnpj=self.member.cnpj,
            unit_code=self.member.unit_code,
            scope_inventory_path=self.inventory_path,
        )

        result = run_online_pilot(config)

        self.assertIs(result, sentinel)
        prepared, plan = run_adapter.call_args.args
        self.assertEqual(
            prepared.job_name,
            "pncp_incremental_pilot_pca_rj_12345678000199_000001",
        )
        self.assertEqual(prepared.coverage_name, "pncp-rj-pca-inventario")
        self.assertEqual(
            plan.endpoint, "/api/consulta/v1/pca/atualizacao"
        )
        self.assertEqual(
            plan.filters,
            {"cnpj": "12345678000199", "codigoUnidade": "000001"},
        )

        list(plan.event_provider(()))
        self.assertEqual(collect.call_args.args[0], prepared.job_name)
        self.assertEqual(
            collect.call_args.kwargs["filters"], plan.filters
        )

    def test_rejects_pca_with_modality(self):
        with self.assertRaisesRegex(
            IncrementalConfigurationError, "pca não aceita modalidade"
        ):
            run_online_pilot(
                self.config(
                    resource="pca",
                    modality=6,
                    organization_cnpj=self.member.cnpj,
                    unit_code=self.member.unit_code,
                    scope_inventory_path=self.inventory_path,
                )
            )

    @patch("src.ingestion.online_pilot.run_adapter_incremental")
    @patch(
        "src.ingestion.online_pilot."
        "PNCPEndpointIncrementalAdapter.collect"
    )
    def test_builds_price_registry_plan_from_frozen_inventory(
        self, collect, run_adapter
    ):
        sentinel = object()
        run_adapter.return_value = sentinel
        collect.return_value = iter(())
        config = self.config(
            resource="ata",
            modality=None,
            organization_cnpj=self.member.cnpj,
            unit_code=self.member.unit_code,
            scope_inventory_path=self.inventory_path,
        )

        result = run_online_pilot(config)

        self.assertIs(result, sentinel)
        prepared, plan = run_adapter.call_args.args
        self.assertEqual(prepared.resource, "ata_registro_preco")
        self.assertEqual(
            prepared.job_name,
            "pncp_incremental_pilot_ata_registro_preco_rj_"
            "12345678000199_000001",
        )
        self.assertEqual(prepared.coverage_name, "pncp-rj-ata-inventario")
        self.assertEqual(
            plan.endpoint, "/api/consulta/v1/atas/atualizacao"
        )
        self.assertEqual(
            plan.filters,
            {
                "cnpj": "12345678000199",
                "codigoUnidadeAdministrativa": "000001",
            },
        )
        self.assertNotIn("uf", plan.filters)

        list(plan.event_provider(()))
        self.assertEqual(
            collect.call_args.args[:2],
            ("ata_registro_preco", prepared.job_name),
        )
        self.assertEqual(collect.call_args.kwargs["filters"], plan.filters)
        self.assertEqual(collect.call_args.kwargs["scope"], plan.filters)

    def test_rejects_price_registry_with_modality(self):
        with self.assertRaisesRegex(
            IncrementalConfigurationError,
            "ata_registro_preco não aceita modalidade",
        ):
            run_online_pilot(
                self.config(
                    resource="ata_registro_preco",
                    modality=6,
                    organization_cnpj=self.member.cnpj,
                    unit_code=self.member.unit_code,
                    scope_inventory_path=self.inventory_path,
                )
            )

    @patch("src.ingestion.online_pilot.run_adapter_incremental")
    @patch(
        "src.ingestion.online_pilot."
        "PNCPRelationshipIncrementalAdapter.collect_target"
    )
    @patch("src.ingestion.online_pilot._dependency_discoveries")
    def test_builds_purchase_item_plan_from_parent_run(
        self, discover, collect, run_adapter
    ):
        sentinel = object()
        target = {"numero_controle": "12345678000199-1-000007/2023"}
        discover.return_value = (target,)
        collect.return_value = iter(())
        run_adapter.return_value = sentinel
        config = self.config(
            resource="contratacao_item",
            modality=None,
            parent_run_id="parent-run",
        )

        result = run_online_pilot(config)

        self.assertIs(result, sentinel)
        prepared, plan = run_adapter.call_args.args
        self.assertEqual(
            prepared.job_name, "pncp_incremental_contratacao_item_rj"
        )
        self.assertEqual(
            plan.endpoint,
            "/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens",
        )
        self.assertEqual(plan.discoveries, (target,))
        discover.assert_called_once_with(prepared, self.database.resolve())

        list(plan.event_provider((target,)))
        self.assertEqual(
            collect.call_args.args[:3],
            ("contratacao_item", prepared.job_name, target),
        )

    def test_rejects_purchase_item_without_parent_run_or_with_modality(self):
        invalid = (
            (
                self.config(resource="contratacao_item", modality=None),
                "--parent-run-id",
            ),
            (
                self.config(
                    resource="contratacao_item",
                    parent_run_id="parent-run",
                ),
                "não aceita modalidade",
            ),
            (
                self.config(
                    resource="contratacao_item",
                    modality=None,
                    parent_run_id="parent-run",
                    organization_cnpj=self.member.cnpj,
                ),
                "não aceita CNPJ/unidade avulsos",
            ),
        )
        for config, message in invalid:
            with self.subTest(message=message), self.assertRaisesRegex(
                IncrementalConfigurationError, message
            ):
                run_online_pilot(config)

    def test_rejects_parent_run_for_endpoint_resource(self):
        with self.assertRaisesRegex(
            IncrementalConfigurationError,
            "aceito somente por recursos dependentes",
        ):
            run_online_pilot(self.config(parent_run_id="parent-run"))

    def test_missing_parent_database_is_a_configuration_error(self):
        with self.assertRaises(IncrementalConfigurationError):
            run_online_pilot(
                self.config(
                    resource="contratacao_item",
                    modality=None,
                    parent_run_id="parent-run",
                )
            )

    def test_operational_requires_explicit_log(self):
        with self.assertRaisesRegex(
            IncrementalConfigurationError, "--log-path"
        ):
            run_online_operational(self.config(), self.database)

    @patch("src.ingestion.online_pilot.run_adapter_incremental")
    def test_operational_delegates_database_confirmation(self, run_adapter):
        sentinel = object()
        run_adapter.return_value = sentinel
        log_path = self.database.with_suffix(".jsonl")

        result = run_online_operational(
            self.config(log_path=log_path), self.database
        )

        self.assertIs(result, sentinel)
        self.assertEqual(
            run_adapter.call_args.kwargs["confirmed_operational_database"],
            self.database,
        )


if __name__ == "__main__":
    unittest.main()
