import unittest

from src.query.analyzer import (
    QueryAnalysisError,
    analisar_pergunta,
    analisar_pergunta_estruturada,
)
from src.query.prompts import montar_prompt_analise
from src.query.schemas import (
    KnowledgeBase,
    QueryRoute,
    StructuredOperation,
)


class QueryAnalyzerTests(unittest.TestCase):
    def test_analisa_pergunta_estruturada_com_multiplas_operacoes(self):
        chamadas: list[str] = []

        def llm_fn(prompt: str) -> str:
            chamadas.append(prompt)
            return """{
                "route": "structured",
                "intent": "aggregate",
                "entity": "contrato",
                "bases": ["estruturada"],
                "filters": {
                    "period_start": "2026-08-01",
                    "period_end": "2026-08-31"
                },
                "operations": ["sum", "count", "group_by"],
                "aggregation_field": "valor_global",
                "group_by": ["municipio"],
                "order_by": [],
                "limit": null,
                "semantic_query": null,
                "needs_document_retrieval": false
            }"""

        analysis = analisar_pergunta(
            "Qual o valor total e a quantidade de contratos por município?",
            llm_fn=llm_fn,
        )

        self.assertEqual(analysis.route, QueryRoute.STRUCTURED)
        self.assertEqual(
            analysis.operations,
            [
                StructuredOperation.SUM,
                StructuredOperation.COUNT,
                StructuredOperation.GROUP_BY,
            ],
        )
        self.assertIn("Retorne exclusivamente um objeto JSON", chamadas[0])
        self.assertIn("Qual o valor total", chamadas[0])

    def test_aceita_json_em_cerca_markdown(self):
        analysis = analisar_pergunta(
            "Quais documentos de habilitação o edital exige?",
            llm_fn=lambda _prompt: """```json
            {
              "route": "rag",
              "intent": "documental",
              "entity": "documento",
              "bases": ["normativa"],
              "filters": {"tipo_documento": "Edital"},
              "operations": [],
              "aggregation_field": null,
              "group_by": [],
              "order_by": [],
              "limit": null,
              "semantic_query": "documentos exigidos para habilitação",
              "needs_document_retrieval": true
            }
            ```""",
        )

        self.assertEqual(analysis.route, QueryRoute.RAG)
        self.assertEqual(analysis.bases, [KnowledgeBase.NORMATIVA])
        self.assertTrue(analysis.needs_document_retrieval)

    def test_aceita_json_com_texto_antes_e_depois(self):
        analysis = analisar_pergunta(
            "Quantas contratações existem por modalidade em 2026?",
            llm_fn=lambda _prompt: """Plano identificado:\n```json
            {
              "route": "structured",
              "intent": "aggregate",
              "entity": "contratacao",
              "bases": ["estruturada"],
              "filters": {"ano": 2026},
              "operations": ["count", "group_by"],
              "aggregation_field": null,
              "group_by": ["modalidade"],
              "order_by": [],
              "limit": null,
              "semantic_query": null,
              "needs_document_retrieval": false
            }
            ```\nFim do plano.""",
        )

        self.assertEqual(analysis.route, QueryRoute.STRUCTURED)
        self.assertIn(StructuredOperation.COUNT, analysis.operations)
        self.assertIn(StructuredOperation.GROUP_BY, analysis.operations)

    def test_aceita_filtro_de_objeto_documental(self):
        analysis = analisar_pergunta(
            "Quais práticas de sustentabilidade existem para manutenção de elevadores?",
            llm_fn=lambda _prompt: """{
              "route": "rag",
              "intent": "documental",
              "entity": "documento",
              "bases": ["agregada"],
              "filters": {
                "tipo_entidade": "contratacao",
                "objeto": "manutenção de elevadores"
              },
              "operations": [],
              "aggregation_field": null,
              "group_by": [],
              "order_by": [],
              "limit": null,
              "semantic_query": "práticas de sustentabilidade",
              "needs_document_retrieval": true
            }""",
        )

        self.assertEqual(analysis.filters.objeto, "manutenção de elevadores")
        self.assertIn("objeto", montar_prompt_analise("teste"))

    def test_modo_estruturado_obriga_rota_e_base_estruturada(self):
        prompts: list[str] = []

        def llm_fn(prompt: str) -> str:
            prompts.append(prompt)
            return """{
              "route": "structured",
              "intent": "aggregate",
              "entity": "contratacao",
              "bases": ["estruturada"],
              "filters": {"ano": 2026},
              "operations": ["count", "group_by"],
              "aggregation_field": null,
              "group_by": ["modalidade"],
              "order_by": [],
              "limit": null,
              "semantic_query": null,
              "needs_document_retrieval": false
            }"""

        analysis = analisar_pergunta_estruturada(
            "Quantas contratações existem por modalidade em 2026?",
            llm_fn=llm_fn,
        )

        self.assertEqual(analysis.route, QueryRoute.STRUCTURED)
        self.assertIn('route DEVE ser "structured"', prompts[0])
        self.assertIn('bases DEVE ser ["estruturada"]', prompts[0])
        self.assertIn('"quantos", "quantidade" e "número de"', prompts[0])

    def test_modo_estruturado_rejeita_rota_diferente(self):
        with self.assertRaisesRegex(QueryAnalysisError, "endpoint exige 'structured'"):
            analisar_pergunta_estruturada(
                "Quantas contratações existem?",
                llm_fn=lambda _prompt: """{
                  "route": "rag",
                  "intent": "documental",
                  "entity": "documento",
                  "bases": ["agregada"],
                  "filters": {},
                  "operations": [],
                  "aggregation_field": null,
                  "group_by": [],
                  "order_by": [],
                  "limit": null,
                  "semantic_query": "contratações",
                  "needs_document_retrieval": true
                }""",
            )

    def test_aceita_plano_hibrido(self):
        analysis = analisar_pergunta(
            "Quais contratos ultrapassaram o limite previsto no decreto?",
            llm_fn=lambda _prompt: """{
                "route": "hybrid",
                "intent": "comparison",
                "entity": "contrato",
                "bases": ["estruturada", "normativa"],
                "filters": {},
                "operations": ["list"],
                "aggregation_field": null,
                "group_by": [],
                "order_by": [],
                "limit": 20,
                "semantic_query": "limite previsto no decreto",
                "needs_document_retrieval": true
            }""",
        )

        self.assertEqual(analysis.route, QueryRoute.HYBRID)
        self.assertEqual(analysis.operations, [StructuredOperation.LIST])
        self.assertTrue(analysis.needs_document_retrieval)

    def test_rejeita_json_invalido(self):
        with self.assertRaisesRegex(QueryAnalysisError, "JSON válido"):
            analisar_pergunta("Teste", llm_fn=lambda _prompt: "não é JSON")

    def test_rejeita_schema_invalido(self):
        with self.assertRaisesRegex(QueryAnalysisError, "plano inválido"):
            analisar_pergunta(
                "Teste",
                llm_fn=lambda _prompt: """{
                    "route": "rag",
                    "intent": "documental",
                    "entity": "documento",
                    "bases": ["normativa"],
                    "filters": {},
                    "operations": ["count"],
                    "aggregation_field": null,
                    "group_by": [],
                    "order_by": [],
                    "limit": null,
                    "semantic_query": "teste",
                    "needs_document_retrieval": true
                }""",
            )

    def test_rejeita_pergunta_vazia_sem_chamar_llm(self):
        def llm_fn(_prompt: str) -> str:
            raise AssertionError("A LLM não deveria ser chamada")

        with self.assertRaisesRegex(QueryAnalysisError, "não pode estar vazia"):
            analisar_pergunta("   ", llm_fn=llm_fn)


if __name__ == "__main__":
    unittest.main()
