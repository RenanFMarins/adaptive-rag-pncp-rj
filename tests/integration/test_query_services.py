from __future__ import annotations

import unittest

from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.modules.query.model import Query, Response, ResponseSource
from app.modules.query.services import persistir_resultado_rag
from src.retrieve import RankedChunk


class QueryServicesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_persistir_resultado_rag(self):
        with SessionLocal() as db:
            # Usa um chunk real já existente no banco.
            from app.modules.documents.model import DocumentChunk

            chunk = db.scalar(
                select(DocumentChunk).order_by(DocumentChunk.id)
            )

            self.assertIsNotNone(chunk)

            source = RankedChunk(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                rrf_score=0.031,
                bm25_rank=1,
                bm25_score=5.0,
                dense_rank=2,
                dense_score=0.8,
                metadata={
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                },
            )

            query, response = persistir_resultado_rag(
                db=db,
                pergunta="Pergunta de teste",
                resposta="Resposta de teste [1].",
                sources=[source],
            )

            self.assertIsNotNone(query.id)
            self.assertIsNotNone(response.id)

            response_source = db.scalar(
                select(ResponseSource).where(
                    ResponseSource.response_id == response.id
                )
            )

            self.assertIsNotNone(response_source)
            self.assertEqual(response_source.chunk_id, chunk.id)
            self.assertEqual(response_source.rank, 1)


if __name__ == "__main__":
    unittest.main()