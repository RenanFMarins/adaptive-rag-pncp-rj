"""Consultas seguras sobre a camada normalizada em SQLite temporário."""

from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from src.query.normalized_structured_tool import executar_consulta_normalizada
from src.query.schemas import (
    KnowledgeBase,
    QueryAnalysis,
    QueryEntity,
    QueryFilters,
    QueryIntent,
    QueryRoute,
    StructuredField,
    StructuredOperation,
)
from src.query.structured_tool import StructuredQueryError


ROOT = Path(__file__).resolve().parents[2]


class NormalizedStructuredToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.executescript(
            (ROOT / "migrations" / "100_normalized_schema.sql").read_text(
                encoding="utf-8"
            )
        )
        lineage = ("raw-1", "hash-1", "2026-10-21T00:00:00Z")
        self.connection.execute(
            "INSERT INTO orgao VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("12345678000199", "Secretaria Estadual", "E", "E", *lineage),
        )
        self.connection.execute(
            "INSERT INTO unidade VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "12345678000199",
                "001",
                "Unidade Central",
                "3304557",
                "Rio de Janeiro",
                "RJ",
                "Rio de Janeiro",
                *lineage,
            ),
        )
        self.connection.execute(
            "INSERT INTO fornecedor VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "PJ",
                "99887766000155",
                "Fornecedor Tecnologia",
                None,
                None,
                None,
                None,
                "BRA",
                0,
                *lineage,
            ),
        )
        self.connection.execute(
            """INSERT INTO contratacao (
                numero_controle_pncp, orgao_cnpj, codigo_unidade, ano_compra,
                sequencial_compra, modalidade_id, modalidade_nome, objeto_compra,
                srp, valor_total_estimado_centavos,
                valor_total_homologado_centavos, data_publicacao_pncp,
                current_source_raw_asset_id, current_source_payload_hash,
                normalized_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "12345678000199-1-000001/2025",
                "12345678000199",
                "001",
                2025,
                1,
                6,
                "Pregão Eletrônico",
                "Aquisição de licenças de software",
                0,
                800_000_00,
                750_000_00,
                "2025-03-10T10:00:00Z",
                *lineage,
            ),
        )
        self.connection.execute(
            """INSERT INTO contrato (
                numero_controle_pncp, numero_controle_compra_externo,
                contratacao_id, parent_resolution_status, orgao_cnpj,
                codigo_unidade, tipo_pessoa_fornecedor, ni_fornecedor,
                nome_fornecedor_informado, supplier_resolution_status,
                ano_contrato, objeto_contrato, valor_inicial_centavos,
                valor_global_centavos, data_publicacao_pncp,
                current_source_raw_asset_id, current_source_payload_hash,
                normalized_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "12345678000199-2-000010/2025",
                "12345678000199-1-000001/2025",
                "12345678000199-1-000001/2025",
                "RESOLVED",
                "12345678000199",
                "001",
                "PJ",
                "99887766000155",
                "Fornecedor Tecnologia",
                "RESOLVED",
                2025,
                "Licenciamento de software corporativo",
                700_000_00,
                750_000_00,
                "2025-04-01T12:00:00Z",
                *lineage,
            ),
        )
        self.connection.commit()
        self.addCleanup(self.connection.close)

    @staticmethod
    def analysis(
        entity: QueryEntity,
        *,
        filters: QueryFilters | None = None,
        operations: list[StructuredOperation] | None = None,
        aggregation_field: StructuredField | None = None,
        group_by: list[StructuredField] | None = None,
    ) -> QueryAnalysis:
        operations = operations or [StructuredOperation.LIST]
        if group_by:
            operations = [*operations, StructuredOperation.GROUP_BY]
        return QueryAnalysis(
            route=QueryRoute.STRUCTURED,
            intent=(
                QueryIntent.AGGREGATE
                if StructuredOperation.LIST not in operations
                else QueryIntent.LOOKUP
            ),
            entity=entity,
            bases=[KnowledgeBase.ESTRUTURADA],
            filters=filters or QueryFilters(),
            operations=operations,
            aggregation_field=aggregation_field,
            group_by=group_by or [],
            limit=20,
        )

    def test_lista_contrato_com_joins_e_valores_em_reais(self) -> None:
        result = executar_consulta_normalizada(
            self.connection,
            self.analysis(
                QueryEntity.CONTRATO,
                filters=QueryFilters(
                    ano=2025,
                    objeto="software",
                    valor_minimo=500_000,
                    fornecedor="tecnologia",
                ),
            ),
        )

        self.assertEqual(result.row_count, 1)
        row = result.rows[0]
        self.assertEqual(row["numero_controle_pncp"], "12345678000199-2-000010/2025")
        self.assertEqual(row["orgao"], "Secretaria Estadual")
        self.assertEqual(row["municipio"], "Rio de Janeiro")
        self.assertEqual(row["fornecedor"], "Fornecedor Tecnologia")
        self.assertEqual(row["modalidade"], "Pregão Eletrônico")
        self.assertEqual(row["valor_global"], 750_000.0)

    def test_agrega_contratacoes_por_modalidade(self) -> None:
        result = executar_consulta_normalizada(
            self.connection,
            self.analysis(
                QueryEntity.CONTRATACAO,
                operations=[StructuredOperation.COUNT, StructuredOperation.SUM],
                aggregation_field=StructuredField.VALOR_GLOBAL,
                group_by=[StructuredField.MODALIDADE],
            ),
        )

        self.assertEqual(
            result.rows,
            [
                {
                    "modalidade": "Pregão Eletrônico",
                    "count": 1,
                    "sum_valor_global": 750_000.0,
                }
            ],
        )

    def test_rejeita_campo_inexistente_para_entidade(self) -> None:
        with self.assertRaisesRegex(StructuredQueryError, "fornecedor"):
            executar_consulta_normalizada(
                self.connection,
                self.analysis(
                    QueryEntity.CONTRATACAO,
                    filters=QueryFilters(fornecedor="empresa"),
                ),
            )

    def test_valores_sao_parametrizados_e_nao_executam_sql(self) -> None:
        result = executar_consulta_normalizada(
            self.connection,
            self.analysis(
                QueryEntity.CONTRATO,
                filters=QueryFilters(objeto="software%' OR 1=1 --"),
            ),
        )

        self.assertEqual(result.rows, [])
        count = self.connection.execute("SELECT COUNT(*) FROM contrato").fetchone()[0]
        self.assertEqual(count, 1)

    def test_exige_esquema_normalizado(self) -> None:
        empty = sqlite3.connect(":memory:")
        self.addCleanup(empty.close)
        with self.assertRaisesRegex(StructuredQueryError, "tabelas ausentes"):
            executar_consulta_normalizada(
                empty,
                self.analysis(QueryEntity.CONTRATO),
            )
