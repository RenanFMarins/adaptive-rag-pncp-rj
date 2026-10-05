from __future__ import annotations

import os
import unittest
from unittest.mock import patch

with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.core.security import get_current_user
    from app.main import app
    from src.generate import MENSAGEM_SEM_EVIDENCIA, RagAnswer
    from src.retrieve import RankedChunk


class QueryRoutesTests(unittest.TestCase):
    def setUp(self):
        def test_db():
            yield object()

        def test_user():
            return object()

        app.dependency_overrides[get_db] = test_db
        app.dependency_overrides[get_current_user] = test_user
        self.addCleanup(app.dependency_overrides.clear)
        self.client = self.enterContext(TestClient(app))

    def test_generate_exige_usuario_autenticado(self):
        del app.dependency_overrides[get_current_user]

        response = self.client.post(
            "/query/generate",
            json={"pergunta": "qual e o objeto?"},
        )

        self.assertEqual(response.status_code, 401)

    def test_generate_request_valido_retorna_answer_e_sources(self):
        source = RankedChunk(
            chunk_id="chunk-1",
            content="Conteudo",
            rrf_score=0.032,
            bm25_rank=1,
            bm25_score=3.0,
            dense_rank=2,
            dense_score=0.8,
            metadata={"document_id": 10},
        )

        with patch(
            "app.modules.query.routes.gerar_resposta_rag",
            return_value=RagAnswer(answer="Resposta [1].", sources=[source]),
        ) as gerar:
            response = self.client.post(
                "/query/generate",
                json={
                    "pergunta": "qual e o objeto do contrato 09/2026?",
                    "top_k": 3,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "answer": "Resposta [1].",
                "sources": [
                    {
                        "rank": 1,
                        "chunk_id": "chunk-1",
                        "relevance_score": 0.032,
                        "metadata": {"document_id": 10},
                    }
                ],
            },
        )
        gerar.assert_called_once()
        self.assertEqual(gerar.call_args.kwargs["pergunta"], "qual e o objeto do contrato 09/2026?")
        self.assertEqual(gerar.call_args.kwargs["top_k"], 3)
        self.assertIs(gerar.call_args.kwargs["persistir"], True)

    def test_generate_top_k_default_e_persistencia(self):
        with patch(
            "app.modules.query.routes.gerar_resposta_rag",
            return_value=RagAnswer(answer="Resposta.", sources=[]),
        ) as gerar:
            response = self.client.post(
                "/query/generate",
                json={"pergunta": "qual e o objeto?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Resposta.")
        self.assertEqual(response.json()["sources"], [])
        self.assertEqual(gerar.call_args.kwargs["top_k"], 5)
        self.assertIs(gerar.call_args.kwargs["persistir"], True)

    def test_generate_sem_evidencias(self):
        with patch(
            "app.modules.query.routes.gerar_resposta_rag",
            return_value=RagAnswer(answer=MENSAGEM_SEM_EVIDENCIA, sources=[]),
        ):
            response = self.client.post(
                "/query/generate",
                json={"pergunta": "pergunta sem evidencias"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], MENSAGEM_SEM_EVIDENCIA)
        self.assertEqual(response.json()["sources"], [])


if __name__ == "__main__":
    unittest.main()
