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
            (self.config(resource="pca"), "contratacao e contrato"),
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
