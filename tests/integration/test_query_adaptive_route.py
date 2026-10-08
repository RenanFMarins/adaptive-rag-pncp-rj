"""Contrato HTTP do endpoint adaptativo sem depender de LLM, FAISS ou FTS5."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from src.query.adaptive_executor import AdaptiveExecutionResult
from src.query.planner import planejar_execucao
from src.query.schemas import (
    AdaptiveQueryResult,
    KnowledgeBase,
    QueryAnalysis,
    QueryEntity,
    QueryIntent,
    QueryRoute,
    StructuredQueryResult,
)
from src.retrieve import RankedChunk


class AdaptiveQueryRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        def test_db():
            yield object()

        app.dependency_overrides[get_db] = test_db
        app.dependency_overrides[get_current_user] = lambda: object()
        self.addCleanup(app.dependency_overrides.clear)
        self.client = self.enterContext(TestClient(app))

    def test_retorna_saida_estruturada_quando_plano_e_structured(self) -> None:
        analysis = QueryAnalysis(
            route=QueryRoute.STRUCTURED,
            intent=QueryIntent.LOOKUP,
            entity=QueryEntity.CONTRATO,
            bases=[KnowledgeBase.ESTRUTURADA],
        )
        execution = AdaptiveExecutionResult(
            analysis=analysis,
            plan=planejar_execucao(analysis),
            structured_result=AdaptiveQueryResult(
                analysis=analysis,
                plan=planejar_execucao(analysis),
                structured_result=StructuredQueryResult(
                    entity=QueryEntity.CONTRATO,
                    columns=["ano"],
                    rows=[{"ano": 2026}],
                    row_count=1,
                    limit_applied=20,
                ),
            ),
        )
        with patch(
            "app.modules.query.routes.executar_consulta_adaptativa_api",
            return_value=execution,
        ):
            response = self.client.post(
                "/query/ask",
                json={"pergunta": "Quais contratos existem em 2026?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["route"], "structured")
        self.assertEqual(response.json()["structured_result"]["rows"], [{"ano": 2026}])
        self.assertIsNone(response.json()["answer"])

    def test_retorna_saida_rag_quando_plano_e_rag(self) -> None:
        analysis = QueryAnalysis(
            route=QueryRoute.RAG,
            intent=QueryIntent.DOCUMENTAL,
            entity=QueryEntity.DOCUMENTO,
            bases=[KnowledgeBase.NORMATIVA],
            semantic_query="Quais documentos são exigidos?",
            needs_document_retrieval=True,
        )
        rag_result = type(
            "RagResult",
            (),
            {
                "answer": "Os documentos exigidos constam na evidência [1].",
                "sources": [
                    RankedChunk(
                        chunk_id="chunk-1",
                        content="Conteúdo",
                        rrf_score=0.03,
                        bm25_rank=1,
                        bm25_score=1.0,
                        dense_rank=1,
                        dense_score=0.9,
                        metadata={},
                    )
                ],
            },
        )()
        execution = AdaptiveExecutionResult(
            analysis=analysis,
            plan=planejar_execucao(analysis),
            rag_result=rag_result,
        )
        with patch(
            "app.modules.query.routes.executar_consulta_adaptativa_api",
            return_value=execution,
        ):
            response = self.client.post(
                "/query/ask",
                json={"pergunta": "Quais documentos são exigidos?", "top_k": 3},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["route"], "rag")
        self.assertEqual(response.json()["answer"], rag_result.answer)
        self.assertEqual(response.json()["sources"][0]["chunk_id"], "chunk-1")


if __name__ == "__main__":
    unittest.main()
